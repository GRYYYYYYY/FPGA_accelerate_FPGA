"""Strict prepared input validation shared by runtime and terminal audit."""
from pathlib import Path
from shadow_recovered_evidence_v7 import ROOT,BASE,read,sha
from stage_static_cp_shadow_common_v7_revision2 import TARGET,REFERENCE,SYNTH,VARIANT,evidence

def validate_preparation(p=TARGET):
 pr=read(p/'preparation.json');assert pr['status']=='full_shadow_v7_prepared_not_executed'
 assert sha(REFERENCE/'manifest.json')==pr['reference_manifest_sha256'] and sha(REFERENCE/'source_bound_audit.json')==pr['reference_audit_sha256']
 for n,h in pr['tools'].items():assert sha(ROOT/'scripts'/n)==h
 for n,e in pr['sources'].items():assert sha(p/'sources'/n)==e['sha256']
 for n,h in pr['shadow_inputs'].items():assert sha(p/'sources'/n)==h
 for n,e in pr['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/n)
 assert {e['source']:e['sha256'] for e in pr['bound'].values()}==pr['predecessors']
 assert sha(p/'full/run.tcl')==pr['run_tcl_sha256'] and sha(p/'namespace.json')==pr['namespace_sha256']
 assert sha(p/'input_plan.json')==pr['input_plan_sha256']
 for n,e in pr['read_only_inputs'].items():assert Path(n).stat().st_size==e['bytes'] and sha(n)==e['sha256']
 for e in read(p/'input_plan.json')['regions'].values():assert Path(e['path']).stat().st_size==e['bytes'] and sha(e['path'])==e['sha256']
 return pr

def check_admission(m):
 samples=m['memory_samples'];assert len(samples)>=2;chosen=m['memory_admission'];assert chosen==samples[-1]
 assert chosen['stable_seconds']>=60 and chosen['current_bytes']<=225*1024**3 and chosen['current_bytes']*4<=chosen['limit_bytes']*3
 start=chosen['monotonic']-chosen['stable_seconds'];window=[s for s in samples if s['monotonic']>=start-0.001]
 assert window[-1]['monotonic']-window[0]['monotonic']>=60
 for s in window:assert s['current_bytes']<=225*1024**3 and s['current_bytes']*4<=s['limit_bytes']*3
 assert all(0 < b['monotonic']-a['monotonic']<=15 for a,b in zip(window,window[1:]))
 return chosen
