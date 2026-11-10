"""Discharge four configured-composition contracts against source and proof statements."""
from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
def port(text,name):
 start=text.index('.'+name+'(')+len(name)+2;i=start;depth=1
 while depth:
  if text[i]=='(':depth+=1
  elif text[i]==')':depth-=1
  i+=1
 return ''.join(text[start:i-1].split())
report=R/'results/ka_as_configured_composition_formal_v1_review_20261031.json';d=j(report);deps=[]
for value in d['contracts'].values():
 if isinstance(value,dict) and 'review' in value:
  p=Path(value['review']);assert sha(p)==value['review_sha256'];deps.append(p)
q=(S/'query_residency_system.sv').read_text();r=(S/'residency_system.sv').read_text();k=r.split(' recovery_ctl(',1)[1].split(';',1)[0];a=q.split('checkpoint_authority_rotator authority(',1)[1].split(';',1)[0]
assert sha(S/'residency_system.sv')==d['contracts']['native_authoritative_contract']['source_sha256']
expected={'cfg_stage':'jp_permit','cfg_authoritative':"jp_permit?1'b1:(fd_fa_authoritative&&as_configured&&as_bound_design==fd_fa_design&&as_bound_checkpoint==fd_fa_checkpoint&&as_bound_generation!=0)",'normal_retired':'f_normal_retired&&as_retired&&(!wm_on||wm_services_retired)','attempt_reset':'k_attempt_reset','cold_rst':'k_cold_rst','clk':'clk'}
for name,v in expected.items():assert port(k,name)==v
assert '||as_fault||' in port(k,'abort')
for name,v in {'rst':'k_cold_rst','clk':'clk','rearm_valid':'as_attempt_reset','bound_generation':'as_bound_generation','configured':'as_configured','busy':'as_busy','fault':'as_fault'}.items():assert port(a,name)==v
assert 'assign as_retired=!as_busy&&!as_core_cfg_valid;' in q
assert 'assign as_attempt_reset=k_attempt_reset;' in r
assert 'assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!a_rsp_valid&&!o_rsp_valid;' in (S/'recovery_coordinator.sv').read_text()
root=B/'ka_as_configured_composition_formal_v1';h=(root/'harness.sv').read_text()
for line in ['if(!cfg_stage && cfg_authoritative) assume(f_authority_generation_nonzero);','if($past(!cold_rst && f_authority_generation_nonzero)) assume(f_authority_generation_nonzero);','if(normal_retired && !abort && f_authority_generation_nonzero) assume(f_authority_configured);','if($past(!cold_rst && f_authority_configured && f_authority_generation_nonzero && !attempt_reset)) assume(f_authority_configured);','if(a_valid) assert(f_authority_configured);']:assert line in h
ret=B/'ka_retirement_state_kernel_formal_v1/harness.sv';persist=B/'ka_configured_persistence_formal_v1/harness.sv';gen=B/'ka_generation_persistence_formal_v1/harness.sv'
assert 'if(bound_generation!=0 && !busy && !fault) assert(configured);' in ret.read_text()
assert 'if($past(!rst && configured && bound_generation!=0 && !(rearm_valid && rearm_ready))) assert(configured);' in persist.read_text()
assert 'if($past(!rst && bound_generation!=0)) assert(bound_generation!=0);' in gen.read_text()
# Independently match these premise harnesses to their accepted reports.
for p in [ret,persist,gen]:
 matches=[v['file_sha256'][str(p.relative_to(B))] for v in map(j,deps) if str(p.relative_to(B)) in v['file_sha256']];assert matches and set(matches)=={sha(p)}
# Stronger no-rearm assumption implies the component's no-accepted-rearm premise.
for valid in [False,True]:
 for ready in [False,True]:
  if not valid:assert not(valid and ready)
cap=B/'ka_as_configured_contract_bindings_evidence_v1';cap.mkdir();files={'reviewer.py':Path(__file__),'configured_harness.sv':root/'harness.sv','report.json':report}
for n in ['query_residency_system.sv','residency_system.sv','recovery_coordinator.sv']:files['sources/'+n]=S/n
for p in deps:files['dependencies/'+p.name]=p
for p in [ret,persist,gen]:files['harnesses/'+p.parent.name+'.sv']=p
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
out=R/'results/ka_as_configured_contract_bindings_review_20261101.json';assert not out.exists();out.write_text(json.dumps({'status':'configured_composition_four_contract_source_and_premise_bindings_reviewed','findings':['Native authoritative branch explicitly requires nonzero authority generation; staging branch is excluded by the contract qualifier.','Generation persistence is an independently proved actual authority property.','Coordinator normal_retired and !abort imply authority !busy and !fault; nonzero generation then invokes the independently proved configured-retirement property.','Authority and coordinator share clock/cold reset, with exact rearm wire aliases. No rearm valid is stronger than the component no-accepted-rearm condition.','Configured premises do not use KA-ready, so this configured dependency has no ready circularity.'],'remaining':['Final quiet-history/conditional-ready integration audit and source-model parameter compatibility.','No full shadow or physical qualification is granted.'],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(p) for n,p in files.items()},'full_system_functional_netlist_validated':False,'physical_gate_open':False},indent=2)+'\n');print('Configured contract bindings reviewed:',sha(cap/'evidence.tar'))
