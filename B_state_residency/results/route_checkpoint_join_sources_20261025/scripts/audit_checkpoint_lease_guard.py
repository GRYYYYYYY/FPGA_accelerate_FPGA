from pathlib import Path
import json,hashlib,sys,importlib.util
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
for n,h in m['artifacts'].items():assert sha(p/n)==h
sp=importlib.util.spec_from_file_location('pc_guard_builder',p/'sources/build.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);assert b.GUARD==(p/'sources/checkpoint_lease_guard.sv').read_text()
assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
log=(p/'simulate.log').read_text();assert 'CHECKPOINT_LEASE_GUARD_PASS checks=26'in log and 'Fatal:'not in log and '$finish called'in log
rows=[t.split()for t in(p/'events.txt').read_text().splitlines()];assert len(rows)==26
owned=0;fault_release=False;blocked=set()
for i,t in enumerate(rows):
 assert t[0]=='G'and int(t[1])==i and len(t[3])==10
 rst,av,rv,healthy,retired,offers,route,cbusy,cvalid,test=map(int,t[3]);ar=int(not rst and not owned and healthy and route and offers and not cbusy and not test);rr=int(not rst and owned and retired and route and not cbusy and not cvalid and not test);safe=int(not rst and owned and healthy)
 assert t[2]==f'{ar}{rr}{safe}{owned}',(i,t)
 if owned and not healthy and rr and rv:fault_release=True
 if owned and rv and not rr:
  for name,value in [('physical/logical_not_retired',not retired),('route_not_retired',not route),('held_command_reply',cbusy),('pending_command',cvalid),('diagnostic_reset',test)]:
   if value:blocked.add(name)
 if rst:owned=0
 elif av and ar:owned=1
 elif rv and rr:owned=0
assert fault_release and blocked=={'physical/logical_not_retired','route_not_retired','held_command_reply','pending_command','diagnostic_reset'}
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=26,retired_error_release=fault_release,blocked_reasons=sorted(blocked),scope='Unit of production lease guard. Input predicates modeled; healthy acquisition, exclusive ownership, pending/held replies, real-retirement conditions, release despite sticky normal fault, reset and simultaneous edges checked. No real-AXI fault/recovery handoff claim.')
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
