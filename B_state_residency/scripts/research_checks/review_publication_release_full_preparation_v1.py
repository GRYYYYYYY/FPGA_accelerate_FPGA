"""Independent preparation/live-admission review, never a simulation verdict."""
from pathlib import Path
import json,hashlib,datetime
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_full_rtl_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
pr=json.loads((p/'preparation.json').read_text());m=json.loads((p/'manifest.json').read_text());ref=Path(pr['reference']);rm=json.loads((ref/'manifest.json').read_text())
assert sha(ref/'source_bound_audit.json')==pr['reference_audit_sha256']=='f087aaff4c300605867c02d9fadf149b67125ebb6d9e13f6599edc7dbd01c770'
assert pr['parameters']==rm['parameters'] and len(pr['parameters'])==13 and pr['parameters']['SLOTS']==32
assert len(pr['production_sha256'])==133
for n,h in pr['production_sha256'].items():assert sha(p/'sources'/n)==h==sha(ref/'sources'/n)==sha(B/'stage_static_cp_shadow_system_v6/sources'/n)
for n,h in pr['sources'].items():assert sha(p/'sources'/n)==h
text=(p/'sources/tb_query_fault.sv').read_text();assert text.replace(pr['verification_call'],'',1).replace(pr['verification_task'],'',1)==(ref/'sources/tb_query_fault.sv').read_text()
assert text.count(pr['verification_call'])==1 and text.count(pr['verification_task'])==1
for expected,actual in zip(rm['cases']['full']['commands'],pr['commands']):
 mapped=[x.replace(str(ref),str(p)) for x in expected['argv']]
 if Path(mapped[0]).name=='xsim':mapped+=['-onfinish','stop']
 assert mapped==actual
assert sha(p/'full/run.tcl')==pr['run_tcl_sha256']
assert sha(p/'input_plan.json')==pr['input_plan_sha256'] and sha(p/'preparation.json')==m['preparation_sha256']
assert m['status']=='running' and m['stage']=='wait_memory' and not m['commands'] and 'active_process' not in m
assert not list((p/'full').glob('*.bin'))
fields=Path('/proc',str(m['runner_pid']),'stat').read_text().rsplit(')',1)[1].split();assert fields[19]==m['runner_start_ticks']
assert sha(R/'scripts/research_checks/run_publication_release_full_rtl_v1.py')==m['runner_sha256']
cg=Path('/sys/fs/cgroup');stats=dict(x.split() for x in (cg/'memory.stat').read_text().splitlines());memory={'current_bytes':int((cg/'memory.current').read_text()),'limit_bytes':int((cg/'memory.max').read_text()),'anon_bytes':int(stats['anon']),'file_bytes':int(stats['file']),'events':(cg/'memory.events').read_text()}
report={'status':'actual_full_rtl_early_probe_sources_parameters_and_additive_stimulus_preparation_reviewed_waiting_memory','time_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'runner_pid':m['runner_pid'],'runner_start_ticks':m['runner_start_ticks'],'runner_session':72272,'production_count':133,'parameters':pr['parameters'],'preparation_sha256':sha(p/'preparation.json'),'reviewer_sha256':sha(Path(__file__)),'memory':memory,'memory_policy':pr['memory_policy'],'scope':'Preparation and verified lightweight wait only. No compile/elaboration/simulation or fresh big image creation yet. Reference complete regression preserved; this is a bounded early prefix probe and cannot replace full shadow acceptance.','full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_publication_release_full_rtl_v1_preparation_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','runner_pid','runner_start_ticks','memory']}))
