from pathlib import Path
import json,re,struct,sys,zlib
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h,n
assert all(t['exit_code']==0 for t in m['commands'])
rows=[t.split()for t in(p/'events.txt').read_text().splitlines()];chunks=[];current=[]
for t in rows:
 if t[0]=='RESULT':chunks.append((current,t));current=[]
 else:current.append(t)
assert not current and len(chunks)==14
path=[]
for sink,first in [(204279,339193),(67922,990179)]:path +=[1,3,26422,66893,sink,0x9abcdef0,0x12345678,first,558358,265324]+[0]*29
query=[0x51435031,1,0x9abcdef0,0x12345678,3,1,5,0x57,180328,0]
def crc(v):return zlib.crc32(struct.pack('<'+'I'*len(v),*v))
for i,(stream,t)in enumerate(chunks):
 assert int(t[1])==i
 paths=[r for r in stream if r[0]=='PATH'];queries=[r for r in stream if r[0]=='QUERY']
 pw=[int(r[2],16)for r in paths];qw=[int(r[2],16)for r in queries]
 if paths:
  want=path.copy()
  if i==3:want[5]^=1
  assert pw==want
  assert [int(r[1])for r in paths]==([*range(20),19,*range(21,78)]if i==4 else list(range(78)))
  assert [int(r[3])for r in paths]==[0]*77+[1]
 if queries:
  want=query.copy()
  if i==6:want[8]-=1
  if i==7:want[4]-=1
  assert qw==want and[int(r[1])for r in queries]==list(range(10))and[int(r[3])for r in queries]==[0]*9+[1]
 expected_state=([1,0,7,1]if i==0 else[0,0,7,0]if i==1 else [1,1,1,0]if i in [2,13]else [1,1,3,0]if i in[3,4,5]else[1,1,7,0]if i in[6,7]else[1,1,0,0]if i in[8,9,10,11,12]else None)
 # Path parser records its native successful CRC despite a sticky earlier identity/order fault.
 assert list(map(int,t[2:6]))==expected_state,(i,t,expected_state)
 pc=int(t[6],16);qc=int(t[7],16)
 if i in [0,1,3,4,5,6,7,9,10,11]:assert pc==crc(path if i!=3 else pw)
 else:assert pc==0
 if i in [0,1,6,7,9,10,11]:assert qc==crc(query if i not in[6,7]else qw)
 else:assert qc==0
log=(p/'simulate.log').read_text();assert 'EXPORT_MANIFEST_PASS checks=114'in log and 'Fatal:'not in log
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=114,scenarios=14,path_crc=f'{crc(path):08x}',query_crc=f'{crc(query):08x}',scope='Synthetic native export parser/CRC and handshake checks; no native-controller or DDR/persistence proof from this unit alone.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('EXPORT_MANIFEST_UNIT_AUDITED')
