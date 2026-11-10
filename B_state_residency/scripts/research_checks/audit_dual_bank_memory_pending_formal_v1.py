"""Independent combinational transition-cut and witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_dual_bank_memory_pending_formal_v2';q=B/'ka_dual_bank_wrong_rvalid_route_control_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==23 and len(pr['retained_state_cells'])==11
assert sha(p/'kernel.json')==pr['kernel_json_sha256']
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n]
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
m=j(p/'manifest.json');assert m['status']=='observed'
for n in pr['retained_state_cells']:assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
for e in m['sources'].values():assert sha(Path(e['source']))==e['sha256']
h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assert(')==16 and h.count('assume(')==1 and h.count('cover(')==3
binding=j(p/'memory_binding.json');assert sha(p/'memory_binding.json')==m['memory_binding_sha256'];assert sha(p/'memory_control.sv')==binding['memory_sha256']==m['memory_control_sha256'];assert sha(Path(binding['review']))==binding['review_sha256']
original_memory=B/'ka_memory_control_equivalence_v3/memory_control.sv';assert sha(original_memory)==binding['parent_memory_sha256']
s=(p/'memory_control.sv').read_text().replace(' output wire obs_wp,obs_wend,\n','',1).replace('assign obs_wp=wp;assign obs_wend=wend;\n','',1);assert s==original_memory.read_text()
assert (q/'harness.sv').read_text()==h and (q/'memory_control.sv').read_bytes()==(p/'memory_control.sv').read_bytes();mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']];assert set(fault['cells'])==set(b['cells'])
for n,c in b['cells'].items():
 d=json.loads(json.dumps(fault['cells'][n]))
 if n==mut['changed_cell']:d['connections'][mut['changed_port']]=mut['original_bits']
 assert c==d
assert 'Status: FAILED' in (q/'bmc.log').read_text()
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
positive=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==3
assert any(r.get('rst')==0 and r.get('memory_rp')==1 and r.get('f_bank0_pending')==1 for r in positive)
assert any(r.get('rst')==0 and r.get('memory_rp')==1 and r.get('f_bank1_pending')==1 for r in positive)
def steps(path):return {r['smt_step']:r for r in wave(path) if 'smt_step' in r}
returns=[]
for f in p.glob('cover*.vcd'):
 w=steps(f)
 for k,r in w.items():
  if k-1 in w and r.get('rst')==0 and w[k-1].get('rst')==0 and r.get('f_state')==0 and w[k-1].get('f_state')==4 and r['f_axi_bank']!=w[k-1]['f_axi_bank']:returns.append(k)
assert returns
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('rst')==0 and r.get('memory_rp')!=(r.get('f_bank0_pending') or r.get('f_bank1_pending'))];assert bad
failed=B/'ka_dual_bank_memory_pending_formal_v1';assert j(failed/'manifest.json')['status']=='failed';assert 'Status: PASSED' in (failed/'bmc.log').read_text() and 'Temporal induction failed' in (failed/'induction.log').read_text()
cap=B/'ka_dual_bank_memory_pending_evidence_v1';cap.mkdir();files={}
for root in [failed,p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py',Path(binding['review'])]+list((R/'scripts/research_checks').glob('run_dual_bank*.py'))+list((R/'hardware/variants/ka_dual_bank_memory_pending_formal_v1').glob('*'))+list((R/'hardware/variants/ka_dual_bank_memory_pending_formal_v2').glob('*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_dual_bank_pending_matches_source_derived_shared_memory_control_inductively_proved_fault_control_restored','retained_bank_bits':23,'assertions':16,'assumptions':1,'covers':3,'memory_binding':binding,'configuration_return_vcd_steps':returns,'fault_witness_values':[{n:r.get(n) for n in ['memory_rp','f_bank0_pending','f_bank1_pending','f_axi_bank','m_rvalid','m_rready']} for r in bad],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual selected bank transitions plus reviewed source-derived single-beat read-only memory control. Memory rp equals disjunction of bank pending, never both, pending routed to current AXI bank; private reset has no outstanding memory read. Data/status inputs arbitrary overapproximation. File/data/fatal equivalence and arbitrary external AXI environment are excluded.','v1_failure':'10-step BMC passes, induction fails on BVALID zero; v2 keeps all assertions and adds proven memory WP/WEND-zero and RP⇒rdlen1/rdpos0 auxiliaries via readonly observations.','remaining':['AS quiet/drained preservation and configuration/publication/rearm exclusion.','Complete native ready composition and full failed shadow coverage disposition.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_dual_bank_memory_pending_formal_v2_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
