from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 dep=ROOT/'results/access_owner_v3_20261024';dm=json.loads((dep/'manifest.json').read_text());gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')and m['functional_gate_sha256']==sha(dep/'source_bound_audit.json')
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']
 for n in dm['rtl']:
  if not Path(n).name.startswith('tb_'):assert sha(out/'sources'/n)==sha(dep/'sources'/n)
 assert all(c['exit_code']==0 for c in m['commands']) and [c['stage']for c in m['commands']]==['compile','elaborate','simulate']
 log=(out/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log and log.count('ACCESS_OWNER_BOUNDARIES_PASS ')==1
 assert 'ACCESS_OWNER_BOUNDARIES_PASS faults=4 recoveries=5 max_service_cycles=262083 cold_scans=8 cycles=2099921'in log
 scans=re.findall(r'^COLD_SCAN_COMPLETE fixture=(\d+) entries=262144$',log,re.M);assert list(map(int,scans))==[1,2,3,4,5,6,7,9]
 assert re.findall(r'^ACCESS_OWNER_FAULT kind=(\d+) status=(\w+) drained=1$',log,re.M)==[('1','5'),('2','5'),('3','5'),('4','host9')]
 source=(out/'sources/integration_body.inc').read_text();assert 'clear_index!==cold_scan_count[17:0]'in source and 'cold_scans!=8'in source
 memory=bytearray(10304);base=0x51fffff000;pending=None;waiting_b=False;reads=writes=bs=resets=rerr=berr=0
 for line in (out/'owner_axi.txt').open():
  r=line.split()
  if r[0]=='RESET':
   assert pending is None and not waiting_b;memory[:]=bytes(len(memory));resets+=1;assert int(r[1])==resets
  elif r[0]=='A':
   assert pending is None and not waiting_b and int(r[2])==1;pending=int(r[1],16);assert pending%64==0 and base<=pending<=base+len(memory)-64
  elif r[0]=='R':
   address=int(r[1],16);assert address==pending and int(r[2],16)==int.from_bytes(memory[address-base:address-base+64],'little');pending=None;reads+=1;rerr+=int(r[3])!=0
  elif r[0]=='W':
   assert pending is None and not waiting_b;address,strobe,data=[int(v,16)for v in r[1:]];offset=address-base
   assert address%64==0 and 0<=offset<=len(memory)-64 and strobe in [0xffff<<i for i in (0,16,32,48)]
   payload=data.to_bytes(64,'little')
   for i in range(64):
    if strobe>>i&1:memory[offset+i]=payload[i]
   writes+=1;waiting_b=True
  else:
   assert r[0]=='B'and waiting_b;bs+=1;berr+=int(r[1])!=0;waiting_b=False
 expected=bytearray(len(memory));expected[6*16:6*16+16]=(2).to_bytes(4,'little')+(0x10001).to_bytes(4,'little')+bytes(8)
 assert pending is None and not waiting_b and resets==9 and rerr==berr==1 and writes==bs
 assert memory==expected==(out/'owners.bin').read_bytes()
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'faults':4,'recoveries':5,'max_service_cycles':262083,'full_default_directory_scans':8,'cycles':2099921,'owner_axi':{'reads':reads,'writes':writes,'bresponses':bs,'r_errors':rerr,'b_errors':berr,'design_reloads':resets},'owner_final_bytes_verified':len(memory),'scope':'Actual default-capacity integrated access HLS/dispatch/coordinates/pager/owner bridge/AXI owner store: owner R error, stalled AR abort, late owner reply abort, host B error and cold recovery. Other old fault classes remain covered by frozen component gates, not repeated here.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
