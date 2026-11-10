"""Replay actual responses and AXI bytes independently of the RTL/vector generator."""
from pathlib import Path
import hashlib,json,mmap,struct,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']
 for n,h in m['gates'].items():assert sha(Path(n))==h
 inp=Path(m['oracle']);graph=Path(m['graph']);cov=read(inp/'coverage.json');im=read(inp/'manifest.json');vm=read(ROOT/'results/coordinate_inputs_verify_20261024/manifest.json')
 assert vm['status']=='passed' and vm['input_manifest_sha256']==sha(inp/'manifest.json')
 for root,mm in [(inp,im),(ROOT/'results/coordinate_inputs_verify_20261024',vm),(graph,read(graph/'manifest.json'))]:
  for n,h in mm['artifacts'].items():assert sha(root/n)==h
 results={}
 for case,cm in m['cases'].items():
  d=out/case;fixture=cm['fixture'];gp=inp/'synthetic'if fixture=='synthetic'else graph
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  for n,h in cm['artifacts'].items():assert sha(d/n)==h
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  cnt={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
  files=[(gp/n).open('rb')for n in ['offsets.u32le','edges.u32le','nodes.rrt32']]
  bufs=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)if f.seek(0,2)else b'' for f in files]
  attrs=bufs[2];rows=(inp/fixture/'rows.bin').read_bytes();cols=(inp/fixture/'columns.bin').read_bytes();N=len(attrs)//32
  labels={};active=False;q=p=0;queries=reads=treads=grequests=0;sll_seen=set();absent=present=explicit_none=default_flip=0
  def i16(n,o):return struct.unpack_from('<h',attrs,n*32+o)[0]
  vectors=(out/fixture/'vectors.txt').read_text().splitlines();actual=(d/'output.txt').read_text().splitlines();assert len(actual)==len(vectors)
  for v,a in zip(vectors,actual):
   vi=v.split();ai=a.split();kind=vi[0]
   if kind=='C':
    op,q,p=map(int,vi[1:]);assert ai==['Q']+vi[1:]
    if op==0:labels={};active=True
    if op==2:active=False
   elif kind=='W':
    n,f=int(vi[1]),int(vi[2]);value=int(vi[3],16);assert ai==['L',str(n),str(f),str(value)];labels.setdefault(n,{})[f]=value
   else:
    assert kind==ai[0]=='R';cookie,op,n,rq,rp=map(int,vi[1:6]);assert list(map(int,ai[1:6]))==[cookie,op,n,rq,rp]
    status=1 if n>=N or(op==2 and not cols)else 2 if not active or(rq,rp)!=(q,p)else 0
    y=slr=nx=pr=lp=rd=pres=north=abits=0
    if status==0:
     abits=int.from_bytes(attrs[n*32:n*32+32],'little');grequests+=1
     if op==2:nx,pr=struct.unpack_from('<ii',cols,i16(n,14)*8);treads+=1
     elif op!=3:
      y=i16(n,16)
      if attrs[n*32+8]==5:
       sll_seen.add(n);reads+=1;rd=1;pres=int(n in labels);lp=labels.get(n,{}).get(2,0);present+=pres;absent+=1-pres
       if lp==0xffffffff:explicit_none+=1
       else:
        grequests+=1
        if i16(lp,16)==y:
         if not pres and y!=i16(n,12):default_flip+=1
         y=i16(n,12)
      if op==1:slr,north=struct.unpack_from('<ii',rows,y*8);treads+=1
    expected=[x&0xffffffff for x in [status,y,slr,nx,pr,lp,rd,pres,north]]+[abits]
    assert list(map(lambda x:int(x,16),vi[6:]))==expected,(case,cookie,'vector')
    assert list(map(lambda x:int(x,16),ai[6:]))==expected,(case,cookie,'rtl');queries+=1
  assert cnt['queries']==queries and cnt['native_reads']==reads and cnt['table_reads']==treads and cnt['host_blocks']>0 and cnt['checkpoints']>0
  if fixture=='real':assert len(sll_seen)==cov['real']['sll_nodes']==11520
  for kind,bases,buffers in [('graph',[0x1fffff000,0x10fffff000,0x20fffff000],bufs),('table',[0x31fffff000,0x41fffff000],[rows,cols])]:
   pending=[];nreads=0
   with (d/(kind+'_axi.txt')).open()as f:
    for line in f:
     r=line.split();addr=int(r[1],16)
     if r[0]=='A':assert not pending and int(r[2])==1;pending=[addr];nreads+=1
     else:
      assert r[0]=='R'and pending==[addr]and int(r[3])==0;pending=[]
      candidates=[(b,buf)for b,buf in zip(bases,buffers)if b<=addr<b+(len(buf)+63)//64*64];assert len(candidates)==1
      b,buf=candidates[0];offset=addr-b;assert offset%64==0
      assert int(r[2],16)==int.from_bytes(buf[offset:offset+64].ljust(64,b'\0'),'little')
   assert not pending and nreads==cnt[kind+'_reads']
  memory=bytearray(3145728);pending=[];nreads=beats=responses=0
  with (d/'label_axi.txt').open()as f:
   for line in f:
    r=line.split()
    if r[0]=='A':
     assert not pending;addr=int(r[1],16);length=int(r[2]);assert 1<=length<=3
     pending=[addr+64*i for i in range(length)];nreads+=1
    elif r[0]=='R':
     addr=int(r[1],16);assert pending.pop(0)==addr and int(r[3])==0
     assert 0<=addr<=len(memory)-64 and addr%64==0 and int(r[2],16)==int.from_bytes(memory[addr:addr+64],'little')
    elif r[0]=='W':
     addr=int(r[1],16);assert int(r[2],16)==2**64-1 and 0<=addr<=len(memory)-64 and addr%64==0
     memory[addr:addr+64]=int(r[3],16).to_bytes(64,'little');beats+=1
    else:assert r==['B','0'];responses+=1
  assert not pending and nreads==cnt['label_reads']and responses==cnt['label_writes']and responses<=beats<=3*responses
  assert hashlib.sha256(memory).hexdigest()==sha(d/'labels.bin')
  results[case]={**cnt,'sll_nodes':len(sll_seen),'absent_prev':absent,'present_prev':present,'explicit_minus_one':explicit_none,'absent_zero_changes_static_y':default_flip,'graph_meta_requests':grequests}
  for b in bufs:
   if isinstance(b,mmap.mmap):b.close()
  for f in files:f.close()
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 report={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':results,'scope':m['scope'],'limitations':['Functional directory FRAMES16384/INDEX14/HASH15; defaults not synthesized in this run.','Synthetic Laguna tables; real image has no Laguna columns.','Scripted labels, not full dense/sparse routing equivalence.','No fault-injection coverage in this functional suite.']}
 (out/'source_bound_audit.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
