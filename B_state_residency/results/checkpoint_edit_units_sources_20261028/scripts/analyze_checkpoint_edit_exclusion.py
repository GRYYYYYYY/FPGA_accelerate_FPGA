"""Source-bound native CP permission/edit exclusion; two-state, not RTL formal."""
from pathlib import Path
from itertools import product
import json
from run_checkpoint_authority import ROOT,sha

p=Path('/tmp/B_state_residency_offer_20261025/query_native_synth_v1')
gate=json.loads((p.parent/'query_native_synth_followup_v1/manifest.json').read_text())
assert gate['status']=='observed'and gate['stage']=='complete'
m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
rp=ROOT/'results/query_native_synth_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert a['status']==r['status']=='passed'and r['audit_byte_identical']
assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_sha256']==sha(p/'source_bound_audit.json')
required={
 'query_residency_system.sv':[
  'wire host_base=!wm_owned&&!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;',
  'wire host_open=host_base&&!boot_pending;',
  'wire boot_admin_open=host_base&&boot_admin_allowed;',
  "wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16'hc17f);",
  'assign f_sr=b_f_sr&host_mask;',
  '.cp_safe((wm_owned?wm_safe:(pc_owned&&pc_safe))&&!qc_reset_held)',
  '.host_label_edit(f_sv[8]&&f_sr[8]&&f_sp[19456])'],
 'query_lifecycle.sv':[
  'wire cp_drift=(cp_rebasing&&!cp_rebase_permit)||!active||!cp_safe||!backend_drained||host_label_edit||active_design!=cp_ctx_design||active_generation!=cp_ctx_generation||active_version!=cp_ctx_version||active_query!=cp_ctx_query||active_price!=cp_ctx_price;']}
for n,expressions in required.items():
 s=(p/'sources'/n).read_text();assert sha(p/'sources'/n)==m['sources'][n]
 for expression in expressions:assert s.count(expression)==1,(n,expression)
root=(p/'sources/query_residency_system.sv').read_text()
controller=[l for l in root.splitlines()if l.startswith('query_lifecycle #')]
assert len(controller)==1 and all(x in controller[0]for x in required['query_residency_system.sv'][-2:])
count=safe_cases=edit_cases=0
for bits in product([False,True],repeat=14):
 wm,ws,pc,ps,reset,qbusy,qfault,ascfg,boot,admin,backend_ready,host_valid,write,other=bits
 safe=(ws if wm else pc and ps)and not reset
 host_base=not wm and not qbusy and not qfault and not pc and not ascfg
 host_open=host_base and not boot
 admin_open=host_base and admin
 mask8=host_open or (admin_open and bool((0xc17f>>8)&1))
 edit=host_valid and backend_ready and mask8 and write
 assert not(safe and edit)
 original=other or not safe or edit
 candidate=other or not safe
 assert original==candidate
 count+=1;safe_cases+=int(safe);edit_cases+=int(edit)
assert safe_cases>0 and edit_cases>0
result=dict(status='native_cp_safe_excludes_edit_two_state_not_rtl_validation',
 analyzer_sha256=sha(Path(__file__)),reference=str(p),reference_audit_sha256=sha(p/'source_bound_audit.json'),
 reference_restore_sha256=sha(rp),source_sha256={n:sha(p/'sources'/n)for n in required},
 checked_source_expressions=required,valuations=count,cp_safe_cases=safe_cases,host_edit_cases=edit_cases,
 generic_counterexample=dict(cp_safe=True,host_label_edit=True,other_drift=False,original_drift=True,specialized_drift=False),
 scope='Direct combinational wiring excludes host edit whenever native query CP safe is true, including normal and boot admin masks. Other drift terms arbitrary; no sequential reachability assumption. Only CP drift edit term may specialize; host edit/label-dirty semantics elsewhere unchanged. Generic default must preserve overlapping external inputs. No X/Z, RTL formal, timing or full-system candidate proof.')
out=ROOT/'results/checkpoint_edit_exclusion_20261028.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('NATIVE_CP_EDIT_EXCLUSION',count,'cases','safe',safe_cases,'edit',edit_cases)
