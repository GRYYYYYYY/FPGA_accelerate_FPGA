"""Terminal-only audit for actual-full-RTL early probe; never full-regression PASS."""
from pathlib import Path
import hashlib,json,importlib.util,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_recovery_20261102');p=B/'ka_publication_release_full_rtl_v4';d=p/'full'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
m=j(p/'manifest.json');assert m['status']=='reproduction_observed' and m['stage']=='complete' and 'active_process' not in m
pr=j(p/'preparation.json');assert sha(p/'preparation.json')==m['preparation_sha256'];assert len(pr['production_sha256'])==133 and len(pr['parameters'])==13 and pr['parameters']['SLOTS']==32
for n,h in pr['sources'].items():assert sha(p/'sources'/n)==h
v6=R/'results/stage_static_cp_shadow_v6_failure_preservation_20261031.json';assert sha(v6)==pr['source_comparison_report_sha256'];v6files=j(v6)['files']['stage_static_cp_shadow_system_v6']
for n,h in pr['production_sha256'].items():assert sha(p/'sources'/n)==h==v6files['sources/'+n]
assert m['attempt_kind']=='independent_new_host_attempt'
assert m['memory_observation']['stable_seconds']>=60 and m['memory_observation']['current_bytes']<=225*1024**3
for name,e in pr['read_only_inputs'].items():assert Path(name).stat().st_size==e['bytes'] and sha(Path(name))==e['sha256']
ref=Path(pr['reference']);assert sha(ref/'source_bound_audit.json')==pr['reference_audit_sha256']
tb=(p/'sources/tb_query_fault.sv').read_text();assert tb.replace(pr['verification_call'],'',1).replace(pr['verification_task'],'',1)==(ref/'sources/tb_query_fault.sv').read_text()
assert len(m['commands'])==3
for c,argv in zip(m['commands'],pr['commands']):assert c['exit_code']==0 and c['argv']==argv and sha(d/(c['stage']+'.stdout.log'))==c['stdout_sha256']
assert sha(R/'scripts/research_checks/run_publication_release_full_rtl_v2.py')==m['runner_sha256']
checker=R/'scripts/research_checks/check_publication_release_full_probe_v1.py';cal=R/'results/ka_publication_release_full_probe_parser_calibration_20261101.json';assert sha(checker)==j(cal)['checker_sha256']
spec=importlib.util.spec_from_file_location('probe_checker',checker);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
parsed=module.parse_probe_text((d/'simulate.log').read_text());natural=(d/'natural_trace.txt').read_text();assert 'BASELINE_NO_PRELOAD 73' in natural and 'FULL_RTL_RELEASE_OVERLAP_OBSERVED' in natural
plan=j(p/'input_plan.json');assert sha(p/'input_plan.json')==pr['input_plan_sha256'];assert sha(Path(plan['binding']))==plan['binding_sha256'];regions=plan['regions']
for e in regions.values():assert sha(Path(e['path']))==e['sha256']
original=j(Path(plan['binding']))['regions']
assert plan['original_regions']=={k:original[k] for k in regions}
for k,e in regions.items():assert {x:e[x] for x in ['bytes','sha256']}=={x:original[k][x] for x in ['bytes','sha256']}
concat=hashlib.sha256()
for key in ['owners','owner_pool','owner_allocator']:
 with Path(regions[key]['path']).open('rb') as f:
  for block in iter(lambda:f.read(1024*1024),b''):concat.update(block)
owner_hash=concat.hexdigest();expected={'design.bin':regions['design']['sha256'],'cost.bin':regions['cost_history_prices_nets']['sha256'],'allocator.bin':regions['owner_allocator']['sha256'],'owners.bin':owner_hash,'snapshot.bin':owner_hash,'pool.bin':owner_hash,'g3.bin':owner_hash,'labels.bin':hashlib.sha256(bytes(3145728)).hexdigest()};assert expected==m['fresh_input_sha256']
vcd=(d/'probe.vcd').read_text();assert '1ps' in vcd
scopes=[];names={};values={};rows={};time=0
for l in vcd.splitlines():
 z=l.split()
 if not z:continue
 if z[0]=='$scope':scopes.append(z[2])
 elif z[0]=='$upscope':scopes.pop()
 elif z[0]=='$var':names[z[3]]='.'.join(scopes[1:]+[z[4]])
 elif l.startswith('#'):rows[time]=dict(values);time=int(l[1:])
 elif l.startswith('b'):
  bits,code=l[1:].split()
  if code in names:values[names[code]]=int(bits,2) if all(c in '01' for c in bits) else bits
 elif l[0] in '01xz' and l[1:] in names:values[names[l[1:]]]=int(l[0]) if l[0] in '01' else l[0]
rows[time]=dict(values)
expected_objects={'clk','bench_rst','k_cold_rst','pc_acquire_valid','pc_acquire_ready','pc_release_valid','pc_release_ready','pc_owned','jp_start','jp_start_ready','jp_owned','jp_done','jp_result','system.publication.start_ok'};assert set(names.values())==expected_objects
at=lambda t:rows[max(k for k in rows if k<=t)]
ready=at(parsed['ready_ps']);split=at(parsed['split_ps']);halt=at(parsed['halt_ps'])
assert all(ready[n]==1 for n in ['pc_owned','jp_start_ready','pc_release_ready','system.publication.start_ok']) and ready['jp_owned']==0
assert split['jp_owned']==1 and split['pc_owned']==0 and halt['jp_done']==1 and halt['jp_result']==3
cap=B/'ka_publication_release_full_rtl_evidence_v4';assert not cap.exists();cap.mkdir();files={}
for f in p.rglob('*'):
 if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),checker,cal,R/'scripts/research_checks/run_publication_release_full_rtl_v2.py',R/'results/ka_publication_release_full_rtl_v4_preparation_review_20261102.json']:files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'attempt_kind':m['attempt_kind'],'old_host_backend_status':m['old_host_backend_status'],'status':'actual_full_rtl_cold_prefix_publication_release_overlap_reproduced_restored','parsed_observation':parsed,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'scope':'Full 133 production RTL sources with actual original cold boot and first lease, bounded additive early probe. Interface race reproduced if accepted. Caller protocol permissibility separate; not original full regression, gate netlist acceptance or KA coverage disposition.','functional_invariant_verdict':'owned_implies_lease_owned_failed_in_this_initialized_full_rtl_trace','full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_publication_release_full_rtl_v4_review_20261102.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(out)
