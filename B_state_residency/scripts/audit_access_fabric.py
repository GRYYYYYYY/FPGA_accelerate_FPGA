"""Independent label/coordinate/owner-value replay plus complete backing-byte audit."""
from pathlib import Path
import hashlib,json,struct,mmap,re,sys,itertools
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='passed';inp=Path(m['inputs']);im=read(inp/'manifest.json');assert im['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']
 for n,h in m['gates'].items():assert sha(Path(n))==h
 for n,h in im['artifacts'].items():assert sha(inp/n)==h
 for n,h in im['gates'].items():assert sha(Path(n))==h
 assert all(c['exit_code']==0 for c in im['commands'])
 for n in ['original_access.inc','coordinates.inc','candidate_access.inc','access_machine.hpp']:
  assert sha(inp/'sources'/n)==sha(ROOT/'results/search_access_unit_v3_20261024/sources'/n)
 results={}
 for case,cm in m['cases'].items():
  d=out/case;meta=im['cases'][cm['fixture']];gp=Path(meta['graph']);tp=Path(meta['tables']);assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  cnt={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
  wanted=set(cm['case_ids'])if cm['case_ids']else None
  for name,col in [('contexts.txt',0),('vectors.txt',1)]:
   lines=(inp/cm['fixture']/name).read_text().splitlines();expected=[s for s in lines if wanted is None or int(s.split()[col])in wanted];assert (d/name).read_text()=='\n'.join(expected)+'\n'
  handles=[(gp/n).open('rb')for n in ['offsets.u32le','edges.u32le','nodes.rrt32']];bufs=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)if f.seek(0,2)else b''for f in handles];attrs=bufs[2];rows=(tp/'rows.bin').read_bytes();cols=(tp/'columns.bin').read_bytes()
  def i16(n,o):return struct.unpack_from('<h',attrs,n*32+o)[0]
  def i32(n,o):return struct.unpack_from('<I',attrs,n*32+o)[0]
  labels={};native=coord=owner=table=steps=services=decisions=0;requests={};actions={};lasttoken=0;sll_reads=0
  def endy(n):
   nonlocal native,sll_reads
   y=i16(n,16)
   if attrs[n*32+8]==5:
    native+=1;sll_reads+=1;prev=labels.get((n,2),0)
    if prev!=0xffffffff and i16(prev,16)==y:y=i16(n,12)
   return y
  with (d/'observed.txt').open()as observed,(d/'vectors.txt').open()as vectors:
   def expect(row):
    got=observed.readline().split();assert got==list(map(str,row)),(case,decisions,got,row)
   def packet():
    r=vectors.readline().split();assert len(r)==28
    return int(r[0]),int(r[1]),list(map(lambda s:int(s,16),r[2:22])),list(map(lambda s:int(s,16),r[22:]))
   for ctx in (d/'contexts.txt').read_text().splitlines():
    r=ctx.split();cid,parent,child,sink,pred=map(int,r[:5]);pp,cp,visited,target=map(lambda s:int(s,16),r[5:9]);occ,uses=map(int,r[9:]);labels={}
    expect(['Q',0,1,3])
    for node,field,v in [(parent,2,pp),(child,2,cp),(child,3,visited),(child,4,target)]:
     if v:expect(['L',node,field,v]);labels[node,field]=v
    if decisions%50==0:expect(['Q',1,1,3])
    row,c,x,y=packet();assert c==cid and x[0]==0;config=x[6:];case_steps=0
    while True:
     assert y[0]==0 and x[6:]==config;expect(['K',row,cid,f'{sum(v<<(32*i)for i,v in enumerate(y)):048x}']);steps+=1;case_steps+=1
     kind=y[4];phase=y[1];aux=y[3]
     if not kind:break
     node=sink if kind==8 else parent if kind==9 else aux if kind==10 else child
     if kind in [1,2,5,9]:
      native+=1;value=labels.get((node,3 if kind==1 else 2 if kind==9 else 4),0)
     elif kind==4:value=int(occ>1 or(occ==1 and uses==0));owner+=1
     elif kind==6:value=uses;owner+=1
     elif kind==10:value=i32(node,0);coord+=1
     else:
      value=endy(node);coord+=1
      if kind in [7,8]:value=struct.unpack_from('<I',rows,value*8)[0];table+=1
     value&=0xffffffff
     previous=y;row,c,x,y=packet();assert c==cid and x[0]==1 and x[1:5]==[previous[i]for i in [1,2,3,5]]and x[5]==value,(case,cid,kind,'oracle value')
     s=observed.readline().split();assert len(s)==8 and s[:6]==list(map(str,['S',cid,kind,phase,node,0]))and int(s[6])>lasttoken and int(s[7],16)==value,(case,cid,s,value)
     lasttoken=int(s[6]);services+=1;requests[kind]=requests.get(kind,0)+1
    expect(['D',cid,y[2],y[5],case_steps,case_steps-1]);expect(['Q',2,1,3]);decisions+=1;actions[y[5]]=actions.get(y[5],0)+1
   assert not vectors.read()and not observed.read()
  assert cnt['cases']==decisions and cnt['steps']==steps and cnt['services']==services and cnt['native_reads']==native and cnt['owner_calls']==owner and cnt['table_reads']==table
  assert cnt['host_blocks']>0 and cnt['checkpoints']>=(decisions+49)//50
  for kind,bases,buffers in [('graph',[0x1fffff000,0x10fffff000,0x20fffff000],bufs),('table',[0x31fffff000,0x41fffff000],[rows,cols])]:
   pending=[];reads=0
   with (d/(kind+'_axi.txt')).open()as f:
    for line in f:
     r=line.split();addr=int(r[1],16)
     if r[0]=='A':assert not pending and int(r[2])==1;pending=[addr];reads+=1
     else:
      assert r[0]=='R'and pending==[addr]and int(r[3])==0;pending=[]
      choices=[(b,buf)for b,buf in zip(bases,buffers)if b<=addr<b+(len(buf)+63)//64*64];assert len(choices)==1
      b,buf=choices[0];offset=addr-b;assert offset%64==0 and int(r[2],16)==int.from_bytes(buf[offset:offset+64].ljust(64,b'\0'),'little')
   assert not pending and reads==cnt[kind+'_reads']
  mem=bytearray(3145728);pending=[];reads=beats=responses=0
  with (d/'label_axi.txt').open()as f:
   for line in f:
    r=line.split()
    if r[0]=='A':
     assert not pending;addr=int(r[1],16);length=int(r[2]);assert 1<=length<=3;pending=[addr+64*i for i in range(length)];reads+=1
    elif r[0]=='R':
     addr=int(r[1],16);assert pending.pop(0)==addr and int(r[3])==0 and 0<=addr<=len(mem)-64 and addr%64==0 and int(r[2],16)==int.from_bytes(mem[addr:addr+64],'little')
    elif r[0]=='W':
     addr=int(r[1],16);assert int(r[2],16)==2**64-1 and 0<=addr<=len(mem)-64 and addr%64==0;mem[addr:addr+64]=int(r[3],16).to_bytes(64,'little');beats+=1
    else:assert r==['B','0'];responses+=1
  assert not pending and reads==cnt['label_reads']and responses==cnt['label_writes']and responses<=beats<=3*responses and hashlib.sha256(mem).hexdigest()==sha(d/'labels.bin')
  results[case]={**cnt,'requests':requests,'actions':actions,'coordinate_calls':coord,'sll_coordinate_reads':sll_reads}
  for b in bufs:
   if isinstance(b,mmap.mmap):b.close()
  for f in handles:f.close()
 assert set(results['synthetic']['requests'])==set(range(1,12))and results['synthetic']['cases']==11664 and results['real']['cases']==512
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':results,'scope':m['scope'],'limitations':['Ownership/overuse queries are explicit test models, not device occupancy state.','Config/dead/static snapshots provided by fixture, not yet children-store metadata integration.','No complete search, recursion, commit, routed timing, platform or board.']};(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
