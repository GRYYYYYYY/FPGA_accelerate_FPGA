"""Preserve an actual two-module initialized publication/release overlap witness."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_overlap_unit_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
pr=j(p/'projection.json');m=j(p/'manifest.json');assert m['status']=='failed'
for f,h in pr['source_sha256'].items():assert sha(Path(f))==h
assert sha(p/'harness.sv')==pr['harness_sha256']==m['harness_sha256']
assert 'Status: FAILED' in (p/'bmc.log').read_text()
for c in m['commands']:assert sha(p/(c['stage']+'.log'))==c['log_sha256']
S=B/'stage_static_cp_shadow_system_v6/sources'
for n in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv']:assert (p/n).read_bytes()==(S/n).read_bytes()
query=(S/'query_residency_system.sv').read_text();lease=next(l for l in query.splitlines() if 'checkpoint_lease_guard checkpoint_lease(' in l);publication=query.split('checkpoint_publish_barrier publication(',1)[1].split(';',1)[0]
assert '.release_valid(pc_release_valid)' in lease and '||jp_owned||' in lease and '.command_valid(ap_valid||cp_valid||qc_cp_valid)' in lease
assert '.start_valid(jp_start&&jp_start_open)' in publication
assert 'wire jp_start_open=!ap_valid&&!ap_owned&&!cp_valid&&!qc_cp_valid&&!as_cfg_valid&&f_sv==0&&!k_rec_valid&&!boot_pending;' in query
h=(p/'harness.sv').read_text();assert h.count('assert(')==1 and h.count('assume(')==1
def wave(path):
 scopes=[];names={};vals={};rows=[]
 for l in path.read_text().splitlines():
  z=l.split()
  if not z:continue
  if z[0]=='$scope':scopes.append(z[2])
  elif z[0]=='$upscope':scopes.pop()
  elif z[0]=='$var' and (len(scopes)==1 or z[4]=='smt_step'):names[z[3]]=z[4]
  elif l.startswith('#'):
   if vals:rows.append(dict(vals))
  elif l.startswith('b'):
   bits,code=l[1:].split()
   if code in names and all(c in '01' for c in bits):vals[names[code]]=int(bits,2)
  elif l[0] in '01' and l[1:] in names:vals[names[l[1:]]]=int(l[0])
 if vals:rows.append(vals)
 return rows
w={r['smt_step']:r for r in wave(p/'bmc_failure.vcd') if 'smt_step' in r};witness=[]
for k,row in w.items():
 if k-1 not in w:continue
 prev=w[k-1]
 if row.get('rst')==0 and row.get('jp_owned')==1 and row.get('pc_owned')==0 and prev.get('rst')==0 and all(prev.get(n)==1 for n in ['start_valid','start_ready','release_valid','release_ready']):witness.append({'previous_step':k-1,'result_step':k,'previous':prev,'result':row})
assert witness
cap=B/'ka_publication_release_overlap_unit_evidence_v1';cap.mkdir();files={}
for f in p.rglob('*'):
 if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/run_publication_release_overlap_unit_v1.py',R/'hardware/variants/ka_publication_release_overlap_unit_v1/harness.sv']:files['repo/'+str(f.relative_to(R))]=f
files['bound_sources/query_residency_system.sv']=S/'query_residency_system.sv'
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'original_two_module_publication_start_and_lease_release_overlap_counterexample_preserved','witness':witness,'query_lease_instance':lease,'query_publication_instance':publication,'quiet_input_domain':'healthy/retired/route_retired/no_offers true; remaining command terms zero; valid baseline and proposed generation/checkpoint metadata constants. Only acquire/release/start/reset are arbitrary.','finding':'Same-clock publication start and lease release are simultaneously accepted; next cycle publication owned is true while lease owned is false. Therefore publication-owned implies lease-owned cannot be assumed unconditionally for discard proof.','scope':'Original two modules with all internal state retained, initial reset. This is an initialized unit composition witness; full-query initial-state reachability and caller protocol legality have not been established. No production RTL edited.','archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'next':['Inspect documented caller contract for simultaneous release/new publication commands.','Confirm the unit input predicates in an actual full-system initialized scenario before classifying system defect or implementing repair.','Continue existing lease/fence/coordinator proofs; do not infer their AS exclusion from this separate witness.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_publication_release_overlap_unit_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'witness_steps':[(x['previous_step'],x['result_step']) for x in witness],'archive_sha256':report['archive_sha256'],'files':len(files)}))
