from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 dep=ROOT/'results/owner_store_v2_20261024';g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed' and g['manifest_sha256']==sha(dep/'manifest.json') and m['model_gate_sha256']==sha(dep/'source_bound_audit.json')
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 assert sha(out/'sources/owner_store.hpp')==sha(dep/'sources/owner_store.hpp')
 assert [c['stage']for c in m['commands']]==['vector_build','vectors','compile','elaborate','simulate'] and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count('OWNER_AXI_PASS ')==1
 stats=dict(zip(['commands','reads','writes','bresponses','cycles'],map(int,re.search(r'OWNER_AXI_PASS commands=(\d+) reads=(\d+) writes=(\d+) bresponses=(\d+) cycles=(\d+)',log).groups())))
 commands=[]
 for line in (out/'commands.txt').read_text().splitlines():
  v=line.split();commands.append([int(x,16)if i in [2,3]else int(x)for i,x in enumerate(v)])
 observed=[list(map(int,line.split()))for line in (out/'observed.txt').read_text().splitlines()]
 assert len(commands)==len(observed)==stats['commands']==13549
 for command,got in zip(commands,observed):assert got==[command[0]]+command[4:]
 oracle=[(int(v[0]),int(v[1],16),int(v[2],16))for v in map(str.split,(out/'expected_writes.txt').read_text().splitlines())]
 memory=bytearray((out/'initial.bin').read_bytes());base=0x1fffff000;read_addr=None;waiting_b=False;reads=writes=bs=0
 for line in (out/'axi.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='A':
   assert read_addr is None and not waiting_b and int(v[2])==1
   read_addr=int(v[1],16);assert read_addr%64==0 and base<=read_addr<=base+len(memory)-64
  elif v[0]=='R':
   address=int(v[1],16);assert address==read_addr and int(v[3])==0
   offset=address-base;assert int(v[2],16).to_bytes(64,'little')==memory[offset:offset+64]
   read_addr=None;reads+=1
  elif v[0]=='W':
   assert read_addr is None and not waiting_b
   address,strobes,data=map(lambda x:int(x,16),v[1:]);_,expected_address,expected_data=oracle[writes]
   lane=expected_address%64
   assert address==expected_address&~63 and strobes==0xffff<<lane and data==expected_data<<(lane*8)
   offset=address-base;payload=data.to_bytes(64,'little')
   for i in range(64):
    if strobes>>i&1:memory[offset+i]=payload[i]
   writes+=1;waiting_b=True
  else:
   assert v==['B','0'] and waiting_b;waiting_b=False;bs+=1
 assert read_addr is None and not waiting_b and reads==stats['reads'] and writes==bs==stats['writes']==stats['bresponses']==len(oracle)
 assert bytes(memory)==(out/'actual.bin').read_bytes()==(out/'expected.bin').read_bytes()
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'stats':stats,'status_counts':dict(Counter(c[4]for c in commands)),'writes_per_command':dict(Counter(c[8]for c in commands)),'all_axi_bytes_replayed':True,'final_window_bytes':len(memory),'high_address_carry':True,'scope':'Actual owner AXI RTL vs tested executable storage spec, final full-window bytes, and response held until all B acknowledgements. Fault/reset integration and routed/board behavior require separate gates.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
