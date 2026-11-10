"""Audit phase-specific lease guarantee using complete original modules."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_discard_lease_unit_v1';q=B/'ka_publication_discard_no_owned_busy_control_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
pr=j(p/'projection.json');m=j(p/'manifest.json');assert m['status']=='observed'
assert sha(p/'projection.json')==m['projection_sha256'];assert sha(p/'harness.sv')==pr['harness_sha256']==m['harness_sha256']
for f,h in pr['source_sha256'].items():assert sha(Path(f))==h
for name in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv']:
 assert (p/name).read_bytes()==(B/'stage_static_cp_shadow_system_v6/sources'/name).read_bytes()==(q/name).read_bytes()
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
h=(p/'harness.sv').read_text();assert h.count('assert(')==2 and h.count('assume(')==1 and h.count('cover(')==2
assert '.command_busy((other_command_busy||jp_owned))' in h and '.lease_owned(pc_owned)' in h
assert (q/'harness.sv').read_text()==h.replace('(other_command_busy||jp_owned)','other_command_busy',1)
assert 'Status: FAILED' in (q/'bmc.log').read_text()
query=B/'stage_static_cp_shadow_system_v6/sources/query_residency_system.sv';line=next(l for l in query.read_text().splitlines() if 'checkpoint_lease_guard checkpoint_lease(' in l);assert '||jp_owned||' in line
def wave(path):
 scopes=[];names={};vals={};rows=[]
 for l in path.read_text().splitlines():
  z=l.split()
  if not z:continue
  if z[0]=='$scope':scopes.append(z[2])
  elif z[0]=='$upscope':scopes.pop()
  elif z[0]=='$var' and len(scopes)==1:names[z[3]]=z[4]
  elif l.startswith('#'):
   if vals:rows.append(dict(vals))
  elif l.startswith('b'):
   bits,code=l[1:].split()
   if code in names and all(c in '01' for c in bits):vals[names[code]]=int(bits,2)
  elif l[0] in '01' and l[1:] in names:vals[names[l[1:]]]=int(l[0])
 if vals:rows.append(vals)
 return rows
rows=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==2
assert any(r.get('rst')==0 and r.get('pub_discard_valid',0)!=0 and r.get('pc_owned')==1 and r.get('jp_owned')==1 for r in rows)
assert any(r.get('rst')==0 and r.get('jp_owned')==1 and r.get('pc_owned')==0 for r in rows)
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('rst')==0 and r.get('pub_discard_valid',0)!=0 and r.get('pc_owned')==0];assert bad
cap=B/'ka_publication_discard_lease_unit_evidence_v1';cap.mkdir();files={}
for root in [p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_publication_discard_lease_unit_v1.py',R/'scripts/research_checks/run_publication_discard_lease_unit_v1.py',R/'scripts/research_checks/run_publication_discard_no_owned_busy_control_v1.py',R/'hardware/variants/ka_publication_discard_lease_unit_v1/harness.sv']:files['repo/'+str(f.relative_to(R))]=f
files['bound_sources/query_residency_system.sv']=query
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'original_two_module_discard_nonzero_implies_lease_owned_inductively_proved_dependency_control_restored','assertions':2,'assumptions':1,'covers':2,'query_command_busy_instance':line,'fault_values':[{n:r.get(n) for n in ['rst','pc_owned','jp_owned','pub_discard_valid']} for r in bad],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Complete original lease/publication modules, all other inputs arbitrary, common reset/clock and actual query command_busy includes jp_owned. Discard nonzero implies lease owned and publication owned. Orphan publication cover still reachable; no global owned-implies-lease assumption.','remaining':['Compose this phase guarantee with actual full-query AS excludes lease-owned temporal proof, which remains running.','Full initialized start/release overlap probe remains waiting memory.','No AS discard exclusion, complete native ready or full shadow acceptance claimed.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_publication_discard_lease_unit_v1_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
