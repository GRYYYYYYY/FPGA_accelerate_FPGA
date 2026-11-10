"""Independent combinational transition-cut and witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_axi_selector_return_formal_v2';q=B/'ka_axi_selector_pending_switch_control_v3';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
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
h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assert(')==6 and h.count('assume(')==1 and h.count('cover(')==2
assert (q/'harness.sv').read_text()==h;mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']];assert set(fault['cells'])-set(b['cells'])=={mut['added_cell']}
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
def steps(path):return {r['smt_step']:r for r in wave(path) if 'smt_step' in r}
positive=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==2
assert any(r.get('rst')==0 and r.get('f_bank0_pending')==1 for r in positive)
returns=[]
for f in p.glob('cover*.vcd'):
 w=steps(f)
 for k,r in w.items():
  if k-1 in w and r.get('rst')==0 and w[k-1].get('rst')==0 and r.get('f_state')==0 and w[k-1].get('f_state')==4 and r['f_axi_bank']!=w[k-1]['f_axi_bank']:returns.append(k)
assert returns
w=steps(q/'bmc_failure.vcd');bad=[]
for k,r in w.items():
 if k-1 in w and r.get('rst')==0 and w[k-1].get('rst')==0 and r['f_axi_bank']!=w[k-1]['f_axi_bank'] and (r.get('f_bank0_pending') or r.get('f_bank1_pending')):bad.append(k)
assert bad
cap=B/'ka_axi_selector_return_evidence_v2';cap.mkdir();files={}
for root in [B/'ka_axi_selector_return_formal_v1',p,B/'ka_axi_selector_pending_switch_control_v1',B/'ka_axi_selector_pending_switch_control_v2',q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py']+list((R/'scripts/research_checks').glob('run_axi_selector*.py'))+list((R/'hardware/variants/ka_axi_selector_return_formal_v1').glob('*'))+list((R/'hardware/variants/ka_axi_selector_return_formal_v2').glob('*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_axi_selector_changes_require_both_pending_zero_inductively_proved_fault_control_restored','retained_bits':23,'assertions':6,'assumptions':1,'covers':2,'configuration_return_vcd_steps':returns,'fault_pending_selector_switch_vcd_steps':bad,'earlier_fault_attempts':'On weaker prior-pending-only assertion set, 10/20-step BMC passed and induction failed; neither is accepted initialized fault coverage. Added current-pending-zero assertion in positive v2 and fault v3.','archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual reader/store control plus parent selectors and both pending DFFs. Config phases store IDLE/no runtime reader state; every non-cold selector change has both pending zero before and after the transition. Abstract covers and fault are not full-system reachable stimuli.','remaining':['Shared memory rp versus bank pending is not yet proved; private-reset memory correspondence remains.','AS quiet/drained and configuration/publication exclusion still pending.','No full-system or physical acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_axi_selector_return_formal_v2_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
