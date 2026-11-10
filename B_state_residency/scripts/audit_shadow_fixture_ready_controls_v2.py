"""Audit actual58 terminal XSim controls; synthetic parser calibration is insufficient."""
from pathlib import Path
import json,hashlib,sys
sys.path.insert(0,str(Path(__file__).resolve().parent/'research_checks'))
from check_shadow_fixture_ready_control_logs_v1 import parse
from audit_shadow_payload_contract_controls_v1 import EXPECTED
R=Path(__file__).resolve().parents[1];B=Path('/tmp/B_state_residency_recovery_20261102')
from shadow_fixture_ready_recovery_v2 import predecessor
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def main():
 p=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else B/'shadow_fixture_ready_controls_v2';assert p.exists(),'Actual controls have not run; preparation/parser calibration cannot be accepted.'
 m=j(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
 stat=Path('/proc')/str(m['runner_pid'])/'stat'
 if stat.exists():assert stat.read_text().rsplit(')',1)[1].split()[19]!=str(m['runner_start_ticks'])
 assert m['runner_sha256']==sha(R/'scripts/run_shadow_fixture_ready_controls_v2.py')
 assert m['predecessor']==predecessor()
 assert m['helper_sha256']==sha(R/'scripts/shadow_fixture_ready_recovery_v2.py')
 expected=dict(EXPECTED)
 for key in ['ka_stall_flip','ka_no_stalls']:del expected[key]
 expected['ka_no_transfers']=('KA_NO_TRANSFERS','KA_FIXTURE_READY_INVARIANT');expected['ka_unexpected_stall']=('KA_UNEXPECTED_STALL','KA_FIXTURE_READY_INVARIANT')
 assert len(expected)==m['planned_cases']==58 and set(m['cases'])==set(expected)
 v=R/'hardware/variants/stage_static_cp_shadow_fixture_ready_v1';vm=j(v/'manifest.json');assert m['checker_sha256']==sha(v/'shadow.sv')==vm['files']['shadow.sv'];assert m['checker_manifest_sha256']==sha(v/'manifest.json')
 assert sha(R/'results/ka_as_ready_temporal_composition_review_20261101.json')==vm['proof_report_sha256']
 admission=m['memory_admission'];assert admission['stable_seconds']>=60 and admission['current_bytes']*4<=admission['limit_bytes']*3
 assert admission['current_bytes']<=225*2**30
 samples=m['memory_samples'];assert len(samples)>=7 and samples[-1]==admission
 start=admission['monotonic_seconds']-admission['stable_seconds']
 window=[x for x in samples if x['monotonic_seconds']>=start]
 assert window[-1]['monotonic_seconds']-window[0]['monotonic_seconds']>=60
 assert all(x['current_bytes']<=min(225*2**30,x['limit_bytes']*3//4) for x in window)
 outcomes={}
 for name,(define,error) in expected.items():
  d=p/name;c=m['cases'][name];assert c['status']=='observed'
  assert c['expected']==(error if error is not None else 'FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS')
  assert c['inputs']=={f:sha(d/f) for f in ['control.sv','shadow.sv','run.tcl']}
  assert sha(d/'control.sv')==vm['files']['control.sv'] and sha(d/'shadow.sv')==vm['files']['shadow.sv']
  assert (d/'run.tcl').read_text()=='run 2us\nquit\n'
  assert [x['stage'] for x in c['commands']]==['compile','elaborate','simulate']
  argv=c['commands'][0]['argv'];assert [argv[i+1] for i,x in enumerate(argv) if x=='-d']==['SHADOW_NETLIST_TOP=protocol_gate']+([define] if define else [])
  binpath='/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/'
  assert argv==[binpath+'xvlog','--sv','-d','SHADOW_NETLIST_TOP=protocol_gate']+(['-d',define] if define else [])+['shadow.sv','control.sv']
  assert c['commands'][1]['argv']==[binpath+'xelab','tb_candidate_offer','stage_static_cp_shadow','-s','control','--O0','--mt','2']
  assert c['commands'][2]['argv']==[binpath+'xsim','control','-tclbatch','run.tcl']
  for cmd in c['commands']:assert cmd['exit_code']==0 and sha(d/(cmd['stage']+'.stdout.log'))==cmd['stdout_sha256']
  for stage in ['compile','elaborate']:
   assert not __import__('re').search(r'^\s*(?:ERROR:|Error:|Fatal:)',(d/(stage+'.stdout.log')).read_text(),__import__('re').M)
  outcomes[name]=parse((d/'simulate.stdout.log').read_text(),name,error)
 out=p/'source_bound_audit.json';assert not out.exists();out.write_text(json.dumps({'status':'actual58_candidate_controls_independently_audited','outcomes':outcomes,'manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'full_system_functional_netlist_validated':False,'physical_gate_open':False},indent=2)+'\n');print('ACTUAL58_CONTROLS_AUDITED')
if __name__=='__main__':main()
