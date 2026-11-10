from pathlib import Path
from collections import Counter
import hashlib,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='passed';dep=ROOT/'results/metadata_v2_20261024';dm=read(dep/'manifest.json');g=read(dep/'source_bound_audit.json');assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')and m['functional_gate_sha256']==sha(dep/'source_bound_audit.json')
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']
 for n in dm['rtl']:
  if not Path(n).name.startswith('tb_'):assert sha(out/'sources'/n)==sha(dep/'sources'/n)
 assert all(c['exit_code']==0 for c in m['commands'])and [c['stage']for c in m['commands']]==['compile','elaborate','simulate']
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count('METADATA_BOUNDARIES_PASS errors=15 recoveries=15 normal_checks=19 cycles=5789')==1
 statuses=Counter(map(int,re.findall(r'^METADATA_FAULT fixture=\d+ status=(\d+) drained=1$',log,re.M)));assert statuses==Counter({4:1,2:3,5:5,0:1,6:1})
 assert len(re.findall(r'^METADATA_CONFIG_FAULT fixture=\d+$',log,re.M))==3 and len(re.findall(r'^METADATA_HOST_B_FAULT fixture=\d+$',log,re.M))==1
 inputs=ROOT/'results/access_fabric_inputs_20261024/synthetic';attrs=(out/'attrs.bin').read_bytes();original=(inputs/'nodes.rrt32').read_bytes();assert len(attrs)==2048
 patched=bytearray(original);patched[9]&=~1;struct.pack_into('<h',patched,14,-32768);struct.pack_into('<i',patched,0,-2147483648);struct.pack_into('<hh',patched,36*32+10,-32768,32767);struct.pack_into('<i',patched,36*32,2147483647);assert attrs==patched
 def u32(n,o):return struct.unpack_from('<I',attrs,n*32+o)[0]
 def i16(n,o):return struct.unpack_from('<h',attrs,n*32+o)[0]&0xffffffff
 flags=0x11d|2|(32 if attrs[18*32+9]&2 else 0)|(64 if attrs[9]&2 else 0)|(128 if attrs[9]&128 else 0)
 words=[0xffffffff,flags,attrs[8],attrs[18*32+8],attrs[36*32+8],i16(0,14),u32(0,0),u32(36,0),i16(36,10),i16(36,12),0x80000000,0x7fffffff,0xffffffff,0]
 assert int((out/'numeric_expected.txt').read_text(),16)==sum(v<<(32*i)for i,v in enumerate(words))
 buffers=[(inputs/'offsets.u32le').read_bytes(),b'',attrs];bases=[0x1fffff000,0x10fffff000,0x20fffff000];pending=None;greads=gerr=0
 for line in (out/'graph_axi.txt').open():
  r=line.split();address=int(r[1],16)
  if r[0]=='A':assert pending is None and int(r[2])==1;pending=address
  else:
   assert r[0]=='R'and address==pending;pending=None;greads+=1;gerr+=int(r[3])!=0
   choices=[(b,buf)for b,buf in zip(bases,buffers)if b<=address<b+(len(buf)+63)//64*64];assert len(choices)==1
   b,buf=choices[0];offset=address-b;assert offset%64==0 and int(r[2],16)==int.from_bytes(buf[offset:offset+64].ljust(64,b'\0'),'little')
 assert pending is None and gerr==1
 mem=bytearray(1024);base=0x61fffff000;pending=None;waiting_b=False;reads=writes=bs=resets=rerr=berr=0;partial_b_changed=False
 for line in (out/'design_axi.txt').open():
  r=line.split()
  if r[0]=='RESET':assert pending is None and not waiting_b;mem[:]=bytes(1024);resets+=1;assert int(r[1])==resets
  elif r[0]=='A':assert pending is None and not waiting_b and int(r[2])==1;pending=int(r[1],16)
  elif r[0]=='R':
   address=int(r[1],16);assert address==pending and address%64==0 and base<=address<=base+1024-64 and int(r[2],16)==int.from_bytes(mem[address-base:address-base+64],'little');pending=None;reads+=1;rerr+=int(r[3])!=0
  elif r[0]=='W':
   assert pending is None and not waiting_b;address,strobe,data=[int(v,16)for v in r[1:]];assert address==base and strobe==0xffff and data in (1,3)
   mem[:16]=data.to_bytes(16,'little');writes+=1;waiting_b=True
  else:
   assert r[0]=='B'and waiting_b;waiting_b=False;bs+=1
   if int(r[1]):berr+=1;assert mem[:16]==(1).to_bytes(16,'little');partial_b_changed=True
 assert pending is None and not waiting_b and resets==33 and writes==bs and rerr==berr==1 and partial_b_changed
 expected=bytearray(1024);expected[0]=3;assert mem==expected==(out/'design.bin').read_bytes()
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'errors':15,'recoveries':15,'normal_checks':19,'cycles':5789,'status_counts':dict(statuses),'graph':{'reads':greads,'r_errors':gerr},'design':{'reads':reads,'writes':writes,'bresponses':bs,'r_errors':rerr,'b_errors':berr,'explicit_reloads':resets},'static_created_merge':True,'dynamic_created_required_when_static_false':True,'signed_16_to_32_limits':True,'actual_token3_exhaustion':True,'failed_B_changed_physical_bytes':True,'scope':'Actual metadata service with graph/design AXI: configuration count consistency, held cfg inputs, created merge, descriptor/owner rejection, errors/abort/drain, timeout, late fault, numeric extremes and token exhaustion. Query/owner context externally driven; pipeline and board not proven.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
