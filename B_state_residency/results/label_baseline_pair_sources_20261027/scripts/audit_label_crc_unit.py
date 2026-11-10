from pathlib import Path
import json,struct,zlib,re,sys
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
assert all(t['exit_code']==0 for t in m['commands'])
log=(p/'simulate.log').read_text();disabled=m['disabled'];rows=[(10,[0x1000+i for i in range(5)]),(20,[0x2000+i for i in range(5)])]
crc=lambda r:zlib.crc32(b''.join(struct.pack('<6I',n,*v)for n,v in r))
assert int((p/'crc.txt').read_text(),16)==crc(rows)
results=[]
for phase in ([1,2]if disabled else[1,2,3,4]):
 accepted=[(int(n),[(int(v,16)>>(32*i))&0xffffffff for i in range(5)])for ph,n,v in re.findall(r'CRC_UNIT_STREAM (\d+) (\d+) ([0-9a-f]+)',log)if int(ph)==phase]
 expected=[(n,list(v))for n,v in rows]
 if phase==3:expected[1][1][0]^=1
 if phase==4:expected.reverse()
 assert accepted==expected
 r=next(tuple(map(int,t[:4]))+(int(t[4],16),int(t[5]),int(t[6]))for t in re.findall(r'CRC_UNIT_RESULT (\d+) (\d+) (\d+) (\d+) ([0-9a-f]+) (\d+) (\d+)',log)if int(t[0])==phase)
 bad=not disabled and phase>1
 assert r==(phase,8 if bad else 0,1 if bad else 2,0 if bad else 2,0 if disabled else crc(accepted),5 if bad else 10,1 if bad else 3)
 writes=[(int(n),int(f),int(v,16))for ph,n,f,v in re.findall(r'CRC_UNIT_W (\d+) (\d+) (\d+) ([0-9a-f]+)',log)if int(ph)==phase]
 assert writes==[(n,f,v)for n,vals in accepted[:1 if bad else 2]for f,v in enumerate(vals)]
 controls=[int(op)for ph,op in re.findall(r'CRC_UNIT_CONTROL (\d+) (\d+)',log)if int(ph)==phase];assert controls==([0]if bad else[0,1])
 results.append(r)
checks=16 if disabled else 32;assert f'LABEL_CRC_UNIT_PASS checks={checks}'in log and 'Fatal:'not in log
r={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'checks':checks,'disabled':disabled,'results':results,'scope':'Independent zlib over accepted node+payload stream; actual backend field writes, checkpoint commands and read counts checked. Correct CRC with changed pins succeeds; wrong expected CRC, altered payload and row permutation reject before last row write when enabled. Disabled mode preserves trusted-stream behavior. RAM backend unit, not full-system proof.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('LABEL_CRC_UNIT_AUDITED',disabled)
