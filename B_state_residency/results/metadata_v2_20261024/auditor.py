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
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='passed';inputs=ROOT/'results/metadata_inputs_20261024';im=read(inputs/'manifest.json');assert im['status']=='passed'and m['input_manifest_sha256']==sha(inputs/'manifest.json')
 source=ROOT/'results/access_fabric_inputs_20261024';sm=read(source/'manifest.json');assert sm['status']=='passed'and sha(source/'manifest.json')==im['source_manifest_sha256']
 integrated=ROOT/'results/access_owner_v3_20261024';ig=read(integrated/'source_bound_audit.json');assert ig['status']=='passed'and ig['manifest_sha256']==sha(integrated/'manifest.json')and sha(integrated/'source_bound_audit.json')==im['integrated_gate_sha256']
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 for name,digest in m['gates'].items():assert sha(Path(name))==digest
 assert sha(inputs/'generator.py')==im['generator_sha256']
 results={}
 for case,cm in m['cases'].items():
  d=out/case;meta=im['cases'][case];gp=Path(meta['graph']);assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands'])
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  cnt={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert cnt['cases']==meta['count']and cnt['host_blocks']>0
  assert sha(d/'commands.txt')==sha(inputs/case/'commands.txt')==meta['commands_sha256']
  original={}
  for line in (source/meta['fixture']/'vectors.txt').open():
   r=line.split();x=[int(v,16)for v in r[2:22]]
   if x[0]==0:original[int(r[1])]=x[6:]
  files=[(gp/n).open('rb')for n in ['offsets.u32le','edges.u32le','nodes.rrt32']];buffers=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)if f.seek(0,2)else b''for f in files];attrs=buffers[2]
  assert sha(gp/'nodes.rrt32')==meta['attrs_sha256']
  state={};claim=None;expected_writes=[];host_count=0;expected_graph_reads=0;marked=set();ids=[]
  with (d/'observed.txt').open()as observed:
   def host(op,node,owner=0,arg=0):
    nonlocal claim,host_count
    old=state.get(node,(0,0,0));flags,count,mask=old
    if op==2:flags|=1
    elif op==3:flags|=2
    elif op==1:assert claim is None and not(flags&4);claim=(node,owner,arg)
    elif op==5:assert claim==(node,owner,0);flags|=4;claim=None
    else:raise AssertionError(op)
    new=(flags,count,mask)
    if new!=old:expected_writes.append((node,struct.pack('<4I',*new,0)));state[node]=new
    row=observed.readline().split();assert row==list(map(str,['H',op,node,owner,arg,*new]));host_count+=1
   for i,line in enumerate((d/'commands.txt').read_text().splitlines()):
    r=line.split();cid,parent,child,sink,dead=map(int,r[:5]);ids.append(cid);desc=[int(v,16)for v in r[5:11]];expected=int(r[11],16);words=[expected>>(32*j)&0xffffffff for j in range(14)]
    assert words==original[cid]and desc==[words[0],words[1]&0x11d]+words[10:]
    assert dead==bool(words[1]&2)and (dead or child not in marked)
    if dead:marked.add(child)
    host(2,child)
    if dead:host(3,child)
    if i==0 and meta['edges']==0:host(1,parent,1,0);host(5,parent,1,0)
    def i16(n,o):return struct.unpack_from('<h',attrs,n*32+o)[0]&0xffffffff
    def u32(n,o):return struct.unpack_from('<I',attrs,n*32+o)[0]
    flags=desc[1]|(2 if state[child][0]&2 else 0)|(32 if attrs[parent*32+9]&2 else 0)|(64 if attrs[child*32+9]&2 else 0)|(128 if attrs[child*32+9]&128 else 0)
    actual_words=[desc[0],flags,attrs[child*32+8],attrs[parent*32+8],attrs[sink*32+8],i16(child,14),u32(child,0),u32(sink,0),i16(sink,10),i16(sink,12)]+desc[2:]
    assert actual_words==words and (attrs[child*32+9]&1 or state[child][0]&1)
    assert observed.readline().split()==['M',str(cid),f'{expected:0112x}']
    expected_graph_reads+=6+sum(node%16==15 for node in [parent,child,sink])
   assert not observed.read()and claim is None
  assert ids==meta['ordered_case_ids']and len(marked)==meta['dead_nodes']and host_count==cnt['host_commands']
  pending=None;reads=0;bases=[0x1fffff000,0x10fffff000,0x20fffff000]
  for line in (d/'graph_axi.txt').open():
   r=line.split();address=int(r[1],16)
   if r[0]=='A':assert pending is None and int(r[2])==1;pending=address
   else:
    assert r[0]=='R'and pending==address and int(r[3])==0;pending=None;reads+=1
    choices=[(b,buf)for b,buf in zip(bases,buffers)if b<=address<b+(len(buf)+63)//64*64];assert len(choices)==1
    b,buf=choices[0];offset=address-b;assert offset%64==0 and int(r[2],16)==int.from_bytes(buf[offset:offset+64].ljust(64,b'\0'),'little')
  assert pending is None and reads==cnt['graph_reads']==expected_graph_reads
  memory=bytearray((meta['nodes']*16+63)&~63);base=0x61fffff000;pending=None;waiting_b=False;reads=writes=bs=0
  for line in (d/'design_axi.txt').open():
   r=line.split()
   if r[0]=='A':assert pending is None and not waiting_b and int(r[2])==1;pending=int(r[1],16)
   elif r[0]=='R':
    address=int(r[1],16);assert pending==address and address%64==0 and base<=address<=base+len(memory)-64 and int(r[3])==0 and int(r[2],16)==int.from_bytes(memory[address-base:address-base+64],'little');pending=None;reads+=1
   elif r[0]=='W':
    assert pending is None and not waiting_b;address,strobe,data=[int(v,16)for v in r[1:]];node,value=expected_writes[writes];offset=node*16;lane=offset%64
    assert address==base+(offset&~63)and strobe==0xffff<<lane and data==int.from_bytes(value,'little')<<(lane*8)
    memory[offset:offset+16]=value;writes+=1;waiting_b=True
   else:assert r==['B','0']and waiting_b;waiting_b=False;bs+=1
  assert pending is None and not waiting_b and reads==cnt['design_reads']==host_count+cnt['cases']and writes==bs==cnt['design_writes']==len(expected_writes)
  expected_memory=bytearray(len(memory))
  for node,value in state.items():expected_memory[node*16:node*16+16]=struct.pack('<4I',*value,0)
  assert memory==expected_memory and hashlib.sha256(memory).hexdigest()==sha(d/'design.bin')
  results[case]={**cnt,'config_words_verified':14*cnt['cases'],'final_design_bytes':len(memory),'persistent_dead_nodes':len(marked)}
  for b in buffers:
   if isinstance(b,mmap.mmap):b.close()
  for f in files:f.close()
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':results,'scope':'Actual graph/design AXI and Config14 controller, same source-bound original CPU configurations in monotonic dead order. Owner configuration and query context are external inputs here; access_owner/children-engine pipeline integration and board remain incomplete.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
