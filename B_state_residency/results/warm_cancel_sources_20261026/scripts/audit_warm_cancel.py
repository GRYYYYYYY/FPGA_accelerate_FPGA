from pathlib import Path
import sys,json,runpy,tempfile,struct
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());negative='--negative'in sys.argv;partial='--partial'in sys.argv
assert m['status']==('failed'if negative else 'observed')or partial
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
base=p.parent/'warm_shared_last_v1';bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
changed={'residency_system.sv','search_residency_system.sv','query_residency_system.sv','recovery_coordinator.sv','tb_query_fault.sv','cancel_build.py','cancel_build_tb.py','regression_runner.py'}
for n,h in m['sources'].items():
 if n not in changed:assert h['sha256']==bm['sources'][n]['sha256'],n
t=runpy.run_path(str(p/'sources/cancel_build_tb.py'));assert t['make']()==(p/'sources/tb_query_fault.sv').read_text()
if negative:
 for n in ['residency_system.sv','search_residency_system.sv','query_residency_system.sv']:assert sha(p/'sources'/n)==bm['sources'][n]['sha256'],n
 expected=p.parent/'warm_cancel_fixed_v2/sources/recovery_coordinator.sv'if 'cancel_transition'in p.name else base/'sources/recovery_coordinator.sv'
 assert sha(p/'sources/recovery_coordinator.sv')==sha(expected)
if not negative:
 b=runpy.run_path(str(p/'sources/cancel_build.py'))
 with tempfile.TemporaryDirectory()as tmp:
  b['make'].__globals__['HERE']=Path(tmp);b['make']()
  for n in ['residency_system.sv','search_residency_system.sv','query_residency_system.sv','recovery_coordinator.sv']:assert (Path(tmp)/n).read_bytes()==(p/'sources'/n).read_bytes()
 t=runpy.run_path(str(p/'sources/cancel_build_tb.py'));assert t['make']()==(p/'sources/tb_query_fault.sv').read_text()
report={};inp=Path(json.loads((Path(bm['base'])/'manifest.json').read_text())['input']);original=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
if not negative and not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if not negative and c['status']!='observed':assert partial;continue
 d=p/name;log=(d/'simulate.log').read_text();r=[x.split()for x in(d/'natural_trace.txt').read_text().splitlines()]
 def by(tag):return[x for x in r if x[0]==tag]
 held=by('CANCEL_HELD')
 if negative:
  assert 'WARM_CANCEL_PASS'not in log
  if 'cancel_transition'in p.name:
   assert 'Fatal: warm failure completed before query reply retirement'in log and any(x[3]=='1'for x in held)
   kind='premature failure before accepted query response retired'
  else:
   assert 'Fatal: joint watchdog'in log and len(held)==8 and len(by('WQR'))==1 and not by('CANCEL_COMPLETE');kind='successful-only LABELS callback leaves canceled coordinator stuck after query reply retired'
  report[name]=dict(expected_failure=kind,held_rows=held);continue
 assert 'WARM_CANCEL_PASS'in log and 'Fatal:'not in log and len(held)==8
 assert all(x[2]=='2'and x[3]=='0'and x[5:]==['1','1']for x in held)
 assert len(by('WQR'))==len(by('CANCEL_COMPLETE'))==len(by('WARM_CANCEL_PASS'))==1
 assert by('WQR')[0][2:]==['2','00000000'] and by('CANCEL_COMPLETE')[0][2:]==['6','6','18']
 assert int(held[-1][1])<=int(by('WQR')[0][1])<int(by('CANCEL_COMPLETE')[0][1])<int(by('WARM_CANCEL_PASS')[0][1])
 assert not by('WARM_COMPLETE')and not by('WARM_RETRY')
 # Prefix9 source words accepted, no last word or successful query receipt.
 wq=r.index(by('WQ')[0]);wqr=r.index(by('WQR')[0]);qs=[x for x in r[wq:wqr]if x[0]=='QCS'];assert len(qs)==9 and [int(x[2])for x in qs]==list(range(9))and all(x[4]=='0'for x in qs)
 oldrows=[x.split()for x in(base/name/'natural_trace.txt').read_text().splitlines()];prefix=r.index(qs[-1])+1;assert r[:prefix]==oldrows[:prefix]
 bundle=Path(c['bundle']);mf=verify(bundle);warm=(bundle/'owner_primary.bin').read_bytes()+(bundle/'owner_allocator.bin').read_bytes();assert [int(x[3],16)for x in qs]==list(struct.unpack('<10I',(bundle/'query.bin').read_bytes()))[:9]
 assert (d/'owners.bin').read_bytes()==warm
 immutable=mf['immutable_resources'];regions=[('graph',[(0x1fffff000,Path(immutable['graph0']['path'])),(0x10fffff000,Path(immutable['graph1']['path'])),(0x20fffff000,Path(immutable['graph2']['path']))],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],d/'cost.bin'),('owner',[(0x61fffff000,original)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(immutable['qstate0']['path']))],None),('table',[(0x41fffff000,Path(immutable['tables0']['path'])),(0x51fffff000,Path(immutable['tables1']['path']))],None),('snapshot',[(0x91fffff000,inp/'owners.bin'),(0x9208aaef40,inp/'owner_allocator.bin'),(0xa000000000,warm)],None)]
 memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
 for tag,v in memory.items():assert v['error_read_beats']==0 and v['error_write_replies']==(2 if tag=='owner'else 0)
 report[name]=dict(held_cycles=8,query_words=9,cancel_status=2,recovery_error=6,retained_journal=6,checkpoint=18,final_owner_equals_G2=True,memory=memory);print(name,'cancellation and all AXI audited',flush=True)
a=dict(status='passed',expected_failure=negative,manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=report,limits=['Query9/10 cancellation after successful label/path restoration; not AXI-inflight cancellation, late-success abort or non-cold retry.','Failure remains quarantined in join HALT; target reset/attempt floor is not rearmed in this test.'])
if partial:a['status']='partial'
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(a,indent=2)+'\n')
