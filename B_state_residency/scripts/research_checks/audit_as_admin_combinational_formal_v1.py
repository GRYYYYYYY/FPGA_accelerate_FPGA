"""Independent combinational transition-cut and witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_as_admin_combinational_formal_v1';q=B/'ka_as_staging_cfg_combinational_probe_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==0 and not pr['retained_state_cells']
assert sha(p/'kernel.json')==pr['kernel_json_sha256']
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n] and c['type'] not in ['$dff','$memrd','$memrd_v2']
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
m=j(p/'manifest.json');assert m['status']=='observed'
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
assert 'Found 0 SCCs' in (p/'prepare.log').read_text()
for e in m['sources'].values():assert sha(Path(e['source']))==e['sha256']
h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assert(')==4 and 'assume(' not in h and h.count('cover(')==1
assert (q/'kernel.json').read_bytes()==(p/'kernel.json').read_bytes()
assert (q/'harness.sv').read_text()==h.replace('  assert(!f_authority_rearm_valid);','  assert(!f_authority_rearm_valid);\n  assert(!f_authority_cfg_valid);')
assert 'Status: FAILED' in (q/'bmc.log').read_text()
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
assert any(r.get('k_a_valid')==1 for f in p.glob('cover*.vcd') for r in wave(f))
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('k_a_valid')==1 and r.get('f_authority_cfg_valid')==1];assert bad
assert all(r.get('f_initial_safe')==0 and r.get('f_prepare_allowed')==1 and r.get('f_k_busy')==1 for r in bad)
cap=B/'ka_as_admin_combinational_evidence_v1';cap.mkdir();files={}
for root in [p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py']+list((R/'scripts/research_checks').glob('run_as_admin_combinational*.py'))+list((R/'scripts/research_checks').glob('run_as_staging_cfg_combinational*.py'))+list((R/'hardware/variants/ka_as_admin_combinational_formal_v1').glob('*')):files['repo/'+str(f.relative_to(R))]=f
for e in m['sources'].values():f=Path(e['source']);files['sources/'+f.name]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_as_native_initial_publish_rearm_combinational_exclusion_proved_staging_overlap_assignment_restored','retained_bits':0,'assertions':4,'assumptions':0,'covers':1,'overlap_values':[{n:r.get(n) for n in ['k_a_valid','f_authority_cfg_valid','f_prepare_allowed','f_initial_safe','f_k_busy']} for r in bad],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'All storage arbitrary, exact selected combinational logic. AS excludes native initial-safe eligibility, authority publish and rearm. AS/staging cfg overlap witness is only an arbitrary-state assignment, not an initialized full-system counterexample.','remaining':['Temporal publication/lease/recovery relation needed for staging cfg exclusion.','Discard validity and AS quiet/drained persistence remain pending.','No full-system ready, coverage waiver or physical acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_as_admin_combinational_formal_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
