from pathlib import Path
import json,sys,re
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
assert all(t['exit_code']==0 for t in m['commands'])
source=bytes((i*17+3)%256 for i in range(512));assert (p/'source.bin').read_bytes()==source
buf=bytearray(512);pending=None;wb=False;rr=ww=bb=er=eb=0
for t in map(str.split,(p/'copy_axi.txt').read_text().splitlines()):
 if t[0]=='A':assert pending is None and t[2]=='1';pending=int(t[1],16)
 elif t[0]=='R':
  address=int(t[1],16);assert pending==address;pending=None
  expected=source[address-0x1000:address-0x1000+64]if 0x1000<=address<0x1200 else bytes(buf[address-0x4000:address-0x4000+64])
  assert int(t[2],16).to_bytes(64,'little')==expected and t[3]in ['0','2'];rr+=1;er+=t[3]=='2'
 elif t[0]=='W':
  address=int(t[1],16);assert 0x4000<=address<0x4200 and int(t[2],16)==2**64-1 and not wb
  buf[address-0x4000:address-0x4000+64]=int(t[3],16).to_bytes(64,'little');ww+=1;wb=True
 else:assert t[0]=='B'and wb and t[1]in ['0','2'];wb=False;bb+=1;eb+=t[1]=='2'
assert pending is None and not wb and rr==10 and ww==5 and bb==5 and er==2 and eb==1
assert (p/'target.bin').read_bytes()==buf and bytes(buf)==source[:128]+bytes(384)
results=[tuple(map(int,t))for t in re.findall(r'SNAPSHOT_RESULT (\d+) (\d+) (\d+)',(p/'simulate.log').read_text())]
assert results==[(0,0,1),(0,2,1),(1,0,0),(2,0,0),(2,0,0),(5,0,0),(6,0,0),(7,0,0),(3,0,0),(3,0,0),(4,0,0)]
a={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'checks':66,'results':results,'read_beats':rr,'write_beats':ww,'error_read_beats':er,'error_write_replies':eb,'scope':'Actual AXI bytes independently replayed; dirty dedup, descriptor capture, no-lease and in-flight R/B cancellation, R/B/verify errors, capacity overflow, source B error and overlap reject. No system integration or board claim.'}
(p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print('SNAPSHOT_UNIT_AUDITED')
