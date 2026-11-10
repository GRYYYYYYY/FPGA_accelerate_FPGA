"""Audit conditional AS configured composition without granting full acceptance."""
from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_as_configured_composition_formal_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert sha(p/'kernel.json')==pr['kernel_json_sha256']
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n]
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
assert pr['retained_state_bits']==5
for n in pr['retained_state_cells']:assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
for n in cfg['roots']:assert b['ports'][n]=={'direction':'output','bits':a['netnames'][n]['bits']}
contracts=j(p/'contracts.json')
for c in contracts.values():
 if isinstance(c,dict) and 'review' in c:assert sha(Path(c['review']))==c['review_sha256']
src=B/'stage_static_cp_shadow_system_v6/sources';qtext=(src/'query_residency_system.sv').read_text();stext=(src/'search_residency_system.sv').read_text();rtext=(src/'residency_system.sv').read_text()
assert 'assign as_retired=!as_busy&&!as_core_cfg_valid;' in qtext
assert 'assign as_attempt_reset=k_attempt_reset;' in rtext
assert '.rearm_valid(as_attempt_reset)' in qtext
for t in [qtext,stext]:
 assert '.as_attempt_reset(as_attempt_reset)' in t and '.as_retired(as_retired)' in t
assert '.normal_retired(f_normal_retired&&as_retired&&(!wm_on||wm_services_retired))' in rtext
assert '.attempt_reset(k_attempt_reset)' in rtext
abort=rtext.split(' recovery_ctl(',1)[1].split('.abort(',1)[1].split('.backend_drained',1)[0];assert '||as_fault||' in abort
h=(p/'harness.sv').read_text();assert h.count('assert(')==10 and h.count('assume(')==5 and h.count('cover(')==1
m=j(p/'manifest.json');assert m['status']=='observed'
assert sha(p/'harness.sv')==m['harness_sha256'] and sha(p/'contracts.json')==m['contracts_sha256']
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
negatives=[]
for name,line in [('no_retirement_contract','  if(normal_retired && !abort && f_authority_generation_nonzero) assume(f_authority_configured);\n'),('no_configured_persistence_contract','  if($past(!cold_rst && f_authority_configured && f_authority_generation_nonzero && !attempt_reset)) assume(f_authority_configured);\n')]:
 q=B/('ka_as_configured_composition_'+name+'_v1');assert (q/'kernel.json').read_bytes()==(p/'kernel.json').read_bytes();assert (q/'harness.sv').read_text()==h.replace(line,'');assert 'Status: FAILED' in (q/'bmc.log').read_text();negatives.append(q)
# Inspect top-level VCD values at completed timestamps.
def wave(path):
 scopes=[];names={};values={};rows=[]
 for line in path.read_text().splitlines():
  z=line.split()
  if not z:continue
  if z[0]=='$scope':scopes.append(z[2])
  elif z[0]=='$upscope':scopes.pop()
  elif z[0]=='$var':
   if len(scopes)==1:names[z[3]]=z[4]
  elif line.startswith('#'):
   if values:rows.append(dict(values))
  elif line[0]=='b':
   bits,code=line[1:].split()
   if code in names and all(c in '01' for c in bits):values[names[code]]=int(bits,2)
  elif line[0] in '01' and line[1:] in names:values[names[line[1:]]]=int(line[0])
 if values:rows.append(values)
 return rows
assert any(r.get('a_valid')==1 and r.get('f_authority_configured')==1 and r.get('f_authority_generation_nonzero')==1 and r.get('cold_rst')==0 for r in wave(p/'cover.vcd'))
for q in negatives:assert any(r.get('f_state')==2 and r.get('f_authority_configured')==0 for r in wave(q/'bmc_failure.vcd'))
cap=B/'ka_as_configured_composition_evidence_v1';cap.mkdir();files={}
for root in [p]+negatives:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in list((R/'scripts/research_checks').glob('*as_configured_composition*.py'))+list((R/'hardware/variants/ka_as_configured_composition_formal_v1').glob('*'))+[R/'scripts/research_checks/prepare_selected_state_cone_v2.py',R/'results/ka_coordinator_transition_integration_v3_review_20261031.json']+[Path(c['review']) for c in contracts.values() if isinstance(c,dict) and 'review' in c]:files['repo/'+str(f.relative_to(R))]=f
for n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']:files['sources/'+n]=src/n
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'as_authority_configured_conditional_composition_inductively_proved_dependency_controls_restored','assertions':10,'assumptions':5,'covers':1,'contracts':contracts,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual coordinator five-state-bit overapproximation with independently proven native/generation/retirement/configured-persistence contracts. Negative traces reach RESET with authority configured false after removing one guarantee; not actual full-system bugs.','remaining':['Reader IDLE and no outstanding response/codec busy.','No overlapping configuration, publication, rearm or AP ownership interfering with KA ready.','Full shadow coverage failure remains; no physical gate acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_as_configured_composition_formal_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
