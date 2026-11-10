"""Verify exact core provenance and parameter compatibility across KA components."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
roots=['ka_reader_quiet_persistence_formal_v1','ka_as_ready_history_composition_formal_v1','ka_as_configured_composition_formal_v1','ka_retirement_state_kernel_formal_v1','ka_generation_persistence_formal_v1','ka_configured_persistence_formal_v1','ka_ready_combinational_formal_v1'];rows=[];cores={};files={'reviewer.py':Path(__file__)}
for name in roots:
 path=B/name/'preparation.json';d=j(path)['configuration'];core=Path(d['source_json']);assert sha(core)==d['source_json_sha256']
 for e in d.get('source_bindings',{}).values():assert sha(Path(e['source']))==e['sha256']
 m=j(core)['modules'][d['module']];params={k:int(v,2) for k,v in m.get('parameter_default_values',{}).items()};cores[d['module']]=params
 assert d['clock']=='clk';rows.append({'component':name,'core':str(core),'core_sha256':sha(core),'parameters':params,'clock':d['clock']});files['preparation/'+name+'.json']=path
assert cores['checkpoint_authority_rotator']=={'MAX_CYCLES':1048576}
assert cores['recovery_coordinator']=={'ENTRIES':32,'RESET_HOLD':5,'MAX_CORRECTIONS':1024,'MAX_CYCLES':1048576,'EXCLUSIVE_BACKEND_RESPONSES':1}
query=(S/'query_residency_system.sv').read_text();res=(S/'residency_system.sv').read_text();coor=(S/'recovery_coordinator.sv').read_text();rot=(S/'checkpoint_authority_rotator.sv').read_text();tb=(S/'tb_query_fault.sv').read_text()
assert 'checkpoint_authority_rotator authority(' in query
assert 'MAX_CYCLES=1048576' in rot
assert 'recovery_coordinator #(.EXCLUSIVE_BACKEND_RESPONSES(EXCLUSIVE_BACKEND_RESPONSES),.ENTRIES(32),.RESET_HOLD(5),.MAX_CYCLES(1048576)) recovery_ctl(' in res
assert 'MAX_CORRECTIONS=1024' in coor
assert 'search_residency_system #(.EXCLUSIVE_BACKEND_RESPONSES(1)' in query
assert 'bench_rst=1;k_cold_rst=1;' in tb
# Coordinator source preparation manifest must bind the same exact source and model.
p=B/'ka_coordinator_contract_core_v1/manifest.json';m=j(p);assert sha(S/'recovery_coordinator.sv')==m['source_sha256'];assert m['parameters']==cores['recovery_coordinator'];assert sha(B/'ka_coordinator_contract_core_v1/core.json')==m['core_sha256'];files['coordinator_core_manifest.json']=p
for n in ['query_residency_system.sv','residency_system.sv','recovery_coordinator.sv','checkpoint_authority_rotator.sv','tb_query_fault.sv']:files['sources/'+n]=S/n
cap=B/'ka_as_component_parameters_evidence_v1';cap.mkdir()
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
out=R/'results/ka_as_component_parameters_review_20261101.json';assert not out.exists();out.write_text(json.dumps({'status':'seven_component_core_provenance_and_current_parameter_bindings_reviewed','components':rows,'findings':['Authority component proofs share the identical SHA-bound MAX_CYCLES1048576 core.','Both coordinator compositions share the identical SHA-bound 32entry/5reset/1024correction/1048576cycle/exclusive-response core matching actual source instantiation.','Actual testbench initially asserts cold reset; temporal proofs still require matching sampled initial-reset and past-valid qualification in final integration.'],'remaining':['Complete final temporal composition audit of first-AS and subsequent-AS induction, including sampled reset and all cuts; parameter matching alone does not discharge it.'],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(p) for n,p in files.items()},'full_system_functional_netlist_validated':False,'physical_gate_open':False},indent=2)+'\n');print('Seven component parameters verified:',sha(cap/'evidence.tar'))
