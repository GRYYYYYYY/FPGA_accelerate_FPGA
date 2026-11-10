"""Independent byte replay and requirement-derived unit transaction matrix.
Source AW/B and lease/health inputs in this component bench are synthetic;
this auditor does not claim full query/authority integration.
"""
from pathlib import Path
import json,re,sys
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
assert all(t['exit_code']==0 for t in m['commands'])
source=bytes((i*17+3)%256 for i in range(512));assert(p/'source.bin').read_bytes()==source
banks={0x4000:bytearray(512),0x8000:bytearray(512)};pending=None;write_pending=False
reads=writes=replies=error_r=error_b=0;write_addresses=[]
def bank(address):
 for base,buf in banks.items():
  if base<=address<base+512:return base,buf
 raise AssertionError(hex(address))
for t in map(str.split,(p/'copy_axi.txt').read_text().splitlines()):
 if t[0]=='A':assert pending is None and t[2]=='1';pending=int(t[1],16)
 elif t[0]=='R':
  a=int(t[1],16);assert pending==a;pending=None
  if 0x1000<=a<0x1200:expected=source[a-0x1000:a-0x1000+64]
  else:b,buf=bank(a);expected=buf[a-b:a-b+64]
  assert int(t[2],16).to_bytes(64,'little')==expected and t[3]in['0','2'];reads+=1;error_r+=t[3]=='2'
 elif t[0]=='W':
  assert not write_pending and int(t[2],16)==2**64-1
  a=int(t[1],16);b,buf=bank(a);data=int(t[3],16).to_bytes(64,'little')
  assert data==source[a-b:a-b+64];buf[a-b:a-b+64]=data
  write_pending=True;writes+=1;write_addresses.append(a)
 else:
  assert t[0]=='B'and write_pending and t[1]in['0','2'];write_pending=False;replies+=1;error_b+=t[1]=='2'
assert pending is None and not write_pending
assert write_addresses==[0x4000,0x4040,0x8000,0x8040,0x8080,0x4000,0x4000,0x4000,0x4000]
assert (reads,writes,replies,error_r,error_b)==(18,9,9,2,1),(reads,writes,replies,error_r,error_b)
assert(p/'bank0.bin').read_bytes()==banks[0x4000]==source[:128]+bytes(384)
assert(p/'bank1.bin').read_bytes()==banks[0x8000]==source[:192]+bytes(320)
# status, verified, receipt, dirty, data_error, coverage_error, generation_floor, checkpoint_floor
bound=[0,0,0,0,0,0,1,17]
expected=[bound,[0,2,1,2,0,0,2,18],[3,0,0,3,1,0,2,18]]
expected += [[1,0,0,3,1,0,2,18]]*3
expected += [[0,0,0,3,0,0,2,18],[9,0,0,3,0,0,2,18]]
expected += [[4,0,0,3,0,0,2,18]]*4
expected += [[9,0,0,3,0,0,2,18],[0,3,1,3,0,0,3,19]]
expected += [bound,[3,0,0,4,0,1,1,17],[3,0,0,4,0,1,1,17]]
expected += [bound,[3,0,0,0,0,1,1,17],bound,[3,0,0,0,1,1,1,17]]
expected += [[3,0,0,0,0,1,0,0],[4,0,0,0,0,0,0,0],bound,[4,0,0,0,0,0,1,17]]
expected += [bound,[3,0,0,0,0,1,1,17],bound,[2,0,0,1,0,0,2,18],[9,0,0,1,0,0,2,18]]
expected += [bound,[3,0,0,0,0,1,1,17],bound,[3,0,0,1,1,1,1,17]]
for status in [5,6,7,2]:expected += [bound,[status,0,0,1,0,0,2,18]]
expected += [bound,[0,1,1,1,0,0,2,18],bound,[3,0,0,0,0,1,1,17]]
actual=[list(map(int,t[2:]))for t in map(str.split,(p/'events.txt').read_text().splitlines())if t[0]=='RESULT']
assert actual==expected,(len(actual),len(expected),[(i,a,b)for i,(a,b)in enumerate(zip(actual,expected))if a!=b])
log=(p/'simulate.log').read_text();busy='BUSY_RECEIPT'in(p/'events.txt').read_text();checks=288 if busy else 278
assert ('CUMULATIVE_OWNER_PASS checks='+str(checks))in log and 'Fatal:'not in log
if busy:
 assert 'PREPARED_RECEIPT 1 1 0 1'in(p/'events.txt').read_text()
 assert 'BUSY_RECEIPT 1 0 3'in(p/'events.txt').read_text()and 'INTEGRITY_RECEIPT 0 0 3'in(p/'events.txt').read_text()
else:
 assert (p/'events.txt').read_bytes()==(p.parent/'cumulative_owner_unit_v2/events.txt').read_bytes()
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=checks,temporary_busy_preserves_receipt=busy,transactions=len(actual),results=actual,read_beats=reads,write_beats=writes,write_addresses=write_addresses,error_read_beats=error_r,error_write_replies=error_b,scope='Component-only. Two actual destination AXI files independently replayed; synthetic source AW/B, lease/health/protocol and publication descriptors. Coverage poison cannot rearm; recoverable data B error preserves cumulative dirty/floors. No native PC lease, coordinator publication, full146MB G3 image, persistence or board proof.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('CUMULATIVE_OWNER_UNIT_AUDITED')
