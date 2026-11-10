"""Close recovered-source, core, assumption and actual-fixture bindings for a new checker policy."""
from pathlib import Path
import ast,json,datetime,sys,tarfile,shutil
from plan_shadow_ka_recovery_v2 import R,sha
from reaudit_shadow_ka_dependencies_v1 import MappedPath,V
B=Path('/tmp/B_state_residency_recovery_20261102');ref=B/'stage_static_cp_host_full_static_v1'
def j(p):return json.loads(Path(p).read_text())
def main():
 index=R/'results/session_handoff_ka_dependency_inventory_20261102.json';di=j(index)
 for v in di['reports'].values():assert sha(v['path'])==v['sha256']
 for e in di['edges']:assert sha(R/'results'/e['to'])==e['sha256']
 rp=R/'results/shadow_ka_dependency_actual_restore_20261102.json';rr=j(rp)
 for a in rr['archives'].values():
  assert sha(a['archive'])==a['archive_sha256']
  for n,h in a['file_sha256'].items():assert sha(Path(a['actual_restore'])/n)==h
 ra=R/'results/shadow_ka_readonly_reaudit_v1_20261102.json';supp=R/'results/shadow_ka_readonly_reaudit_supplement_20261102.json';s=j(supp);audits={}
 for name,v in j(ra)['rows'].items():
  assert sha(v['log'])==v['log_sha256'] and sha(v['source'])==v['source_sha256']
  if v['exit_code']:
   v=s[Path(v['source']).stem];assert v['exit_code']==0 and sha(v['log'])==v['log_sha256']
  audits[name]=dict(log=v['log'],log_sha256=v['log_sha256'])
 assert len(audits)==20
 # Independently revisit early selected-state proofs whose reviewers were interactive.
 extra={}
 for name,assumes,asserts in [('ka_retirement_state_kernel_formal_v1',1,7),('ka_generation_persistence_formal_v1',1,8),('ka_coordinator_config_generation_formal_v1',3,7)]:
  p=V/name;m=j(p/'manifest.json');pr=j(p/'preparation.json');cfg=pr['configuration'];core=MappedPath(cfg['source_json']);assert sha(core)==cfg['source_json_sha256']
  a=j(core)['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
  assert sha(p/'kernel.json')==pr['kernel_json_sha256']==m['kernel_json_sha256'];assert sha(p/'preparation.json')==m['preparation_sha256']
  for n,c in b['cells'].items():
   if n not in pr['cuts']:assert c==a['cells'][n]
   else:
    cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
  for n in pr['retained_state_cells']:assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
  for n,v in a['ports'].items():
   if v['direction']=='input':assert b['ports'][n]==v
  for n,net in a['netnames'].items():
   expected=json.loads(json.dumps(net));expected.get('attributes',{}).pop('init',None);assert b['netnames'][n]==expected
  assert m['status']=='observed' and not m.get('active_process')
  assert [c['stage'] for c in m['commands']]==['prepare','bmc','induction','cover']
  for c in m['commands']:
   log=p/(c['stage']+'.log');assert c['exit_code']==0 and sha(log)==c['log_sha256']
   if c['stage']!='prepare':assert 'Status: PASSED' in log.read_text()
  h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assume(')==assumes and h.count('assert(')==asserts
  for e in m['sources'].values():assert sha(MappedPath(e['source']))==e['sha256']
  extra[name]=dict(core_sha256=sha(core),kernel_sha256=sha(p/'kernel.json'),retained_state_bits=pr['retained_state_bits'],assumptions=assumes,assertions=asserts,harness_sha256=sha(p/'harness.sv'))
 # Read-only reuse of the exact coordinator wiring review before its report construction.
 script=R/'scripts/research_checks/audit_coordinator_transition_integration_v3.py';tree=ast.parse(script.read_text());body=[]
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='report' for t in node.targets):break
  body.append(node)
 tree.body=body;code=ast.unparse(tree).replace('from pathlib import Path','from reaudit_shadow_ka_dependencies_v1 import MappedPath as Path');exec(compile(code,str(script),'exec'),{'__file__':str(script)})
 # Authority core provenance is preparation evidence; parent stale running/cover is NOT accepted.
 cp=R/'results/shadow_authority_core_copy_20261102.json';cr=j(cp);core=V/'ka_active_configured_formal_v1/core.json';cm=j(V/'ka_active_configured_formal_v1/manifest.json')
 assert sha(core)==cm['core_json_sha256']==cr['core_sha256']
 for c in cm['commands']:
  if c['stage'] in ['core','prepare']:assert c['exit_code']==0 and sha(V/'ka_active_configured_formal_v1'/(c['stage']+'.log'))==c['log_sha256']
 for e in cm['sources'].values():assert sha(MappedPath(e['source']))==e['sha256']
 assert 'hierarchy -top checkpoint_authority_rotator' in (V/'ka_active_configured_formal_v1/core.ys').read_text()
 # Source-bound full flattened model remains structural evidence only.
 fm=j(ref/'manifest.json');sm=j(B/'stage_static_cp_synth_v1/manifest.json');em=j(V/'ka_full_rtl_elaboration_v2/manifest.json');lm=j(V/'ka_full_rtl_lowering_v1/manifest.json')
 assert lm['parameters']==em['parameters']==fm['parameters']==sm['parameters'] and len(fm['parameters'])==13 and fm['parameters']['SLOTS']==32
 assert lm['predecessor_manifest_sha256']==sha(V/'ka_full_rtl_elaboration_v2/manifest.json');assert lm['input_rtlil_sha256']==sha(V/'ka_full_rtl_elaboration_v2/elaborated.il')
 assert lm['json_sha256']==sha(V/'ka_full_rtl_lowering_v1/full.json') and lm['exit_code']==0
 for n in sm['rtl']:assert sha(ref/'sources'/n)==sha(V/'ka_full_rtl_elaboration_v2/sources'/n)==em['sources'][n]==sm['sources'][n]
 assert len(sm['rtl'])==133
 # All current core configurations have original source bindings and exact model bytes.
 configurations=[]
 for a in rr['archives'].values():
  for n in a['file_sha256']:
   if n.endswith('preparation.json') or n.startswith('preparation/'):
    c=j(Path(a['actual_restore'])/n).get('configuration',{})
    if 'source_json' not in c:continue
    assert sha(MappedPath(c['source_json']))==c['source_json_sha256']
    for e in c.get('source_bindings',{}).values():assert sha(MappedPath(e['source']))==e['sha256']
    configurations.append(dict(file=n,core_sha256=c['source_json_sha256'],module=c['module'],clock=c['clock']))
 proofs=[index,rp,ra,supp,cp,R/'results/shadow_ka_dependency_path_supplement_20261102.json',R/'results/shadow_ka_dependency_review_view_20261102.json',script,Path(__file__)]
 out=R/'results/shadow_ka_dependency_gate_review_20261102.json';assert not out.exists()
 result=dict(status='restored_KA_dependencies_source_core_parameters_and_fixture_contracts_reviewed',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reports=30,archives=24,restored_files=862,readonly_original_audits=audits,early_selected_state_rechecks=extra,configurations=configurations,production_sources=133,parameters=fm['parameters'],bound_reports={n:v['sha256'] for n,v in di['reports'].items()},bound_evidence={str(p):sha(p) for p in proofs},core_sha256=sha(core),initialization='Original cold reset retained; each temporal premise qualifies initial reset/past_valid. Shared clk/k_cold_rst and current source instantiations rechecked by original parameter/handshake/configured audits.',memory_scope='READ_ONLY1 MAX_BEATS1 READ_DELAY0; actual unconnected hold_r never equals1 and is included in arbitrary formal hold_r. Data/status arbitrary; only legal nonfatal control traces, not file/data equivalence or arbitrary AXI.',composition='DRAIN establishes quiet; phase1..9 admin/AP exclusions preserve it until AS. Successful AW exact handshake retires reader and restores quiet. Configured follows independent metadata/retirement/persistence. Final combinational ready implication consumes these independent premises, never used to establish them.',policy='Current-fixture KA valid requires known ready1 at sample and pre-edge, zero stalls plus active/transfer/edge/idle coverage. CP/PW stall requirements remain. Actual four-state complete shadow required separately.',historical_exclusions=['Rejected AXI control v1 reset projection remains excluded; v2 accepted.','Failed AP ownership v1 preparation remains excluded; v2 accepted.','Core parent running/cover manifest is preparation provenance only, not an accepted proof.','Prior full shadow v6 remains failed; no full-system or physical acceptance.'],full_system_functional_netlist_validated=False,physical_gate_open=False)
 out.write_text(json.dumps(result,indent=2)+'\n');print(result['status'],len(configurations))
if __name__=='__main__':main()
