"""Independent payload/CRC and observed terminal checks for native leaf slice."""
from pathlib import Path
import json,struct,sys,zlib
from run_checkpoint_authority import sha

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed' and len(m['commands'])==3
assert all(c['exit_code']==0 for c in m['commands'])
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
records=[(10,[0x1000,0x1001,0x1002,0x1003,0x12]),(20,[0x2000,0x2001,0x2002,0x2003,0x34])]
blob=lambda rs:b''.join(struct.pack('<6I',n,*v)for n,v in rs)
crc=zlib.crc32(blob(records));assert m['crc']==f'{crc:08x}'
assert (p/'crc.txt').read_text()==f'{crc:08x}\n'
log=(p/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log
lines=[t.split()for t in log.splitlines()if t.startswith('SEED_LEAF_')]
full=[(n,f,v)for n,values in records for f,v in enumerate(values)]
expected_results=[(1,0,0,2,2,10,crc),(2,1,0,2,2,10,crc),
                  (3,1,8,1,0,5,crc),(4,1,7,0,0,3,zlib.crc32(blob(records[:1])))]
for phase,skip,status,written,verified,count,actual_crc in expected_results:
    writes=[t for t in lines if t[0]=='SEED_LEAF_W'and int(t[1])==phase]
    assert [(int(t[2]),int(t[3]),int(t[4],16))for t in writes]==full[:count]
    assert all(int(t[5])==skip for t in writes)
assert [tuple(map(int,t[1:7]))+(int(t[7],16),)for t in lines if t[0]=='SEED_LEAF_RESULT']==expected_results
assert lines[-1]==['SEED_LEAF_PASS','checks=286','scenarios=4']
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    scenarios=4,checks=286,field_writes=28,independent_crc=f'{crc:08x}',
    start_permission_latched=True,delayed_reply_cycles=4,held_terminal_cycles=8,
    scope='Actual label_restore_controller with RAM backend model. Disabled/enabled permission pin reversal after acceptance; bad CRC rejects last record; abort after third field waits for delayed reply and remains stopped. Each scenario uses service reset. No whole-system cancellation or noncold retry proof.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('RESTORE_SEED_LEAF_AUDITED',p.name)
