"""Audit the new configured persistence proof and its model fault witness."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_configured_persistence_formal_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256']
assert sha(p/'kernel.json')==pr['kernel_json_sha256']
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n]
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits']
  assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
assert sum(len(a['cells'][n]['connections']['Q']) for n in pr['retained_state_cells'])==271
for n in pr['retained_state_cells']:assert a['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
m=j(p/'manifest.json');assert m['status']=='observed'
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
for s in m['sources'].values():assert sha(Path(s['source']))==s['sha256']
assert sha(p/'harness.sv')==m['harness_sha256']
assert (p/'harness.sv').read_text().count('assert(')==11
assert (p/'harness.sv').read_text().count('assume(')==1
q=B/'ka_configured_persistence_clear_on_request_v2';mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']]
assert (q/'harness.sv').read_bytes()==(p/'harness.sv').read_bytes()
assert set(fault['cells'])-set(b['cells'])=={'fault_request_gate','fault_configured_mux'}
for n,c in b['cells'].items():
 d=json.loads(json.dumps(fault['cells'][n]))
 if n==mut['changed_dff']:d['connections']['D']=mut['original_D']
 assert c==d
assert 'Status: FAILED' in (q/'bmc.log').read_text() and 'harness.sv:127.' in (q/'bmc.log').read_text()
def waves(path):
 scopes=[];names={};values={};rows={}
 for l in path.read_text().splitlines():
  z=l.split()
  if not z:continue
  if z[0]=='$scope':scopes.append(z[2])
  elif z[0]=='$upscope':scopes.pop()
  elif z[0]=='$var':names[z[3]]='.'.join(scopes+[z[4]])
  elif l.startswith('#'):
   if 'smt_step' in values:rows[values['smt_step']]=dict(values)
  elif l[0]=='b':
   bits,code=l[1:].split()
   if all(c in '01' for c in bits):values[names[code]]=int(bits,2)
  elif l[0] in '01' and l[1:] in names:values[names[l[1:]]]=int(l[0])
 if 'smt_step' in values:rows[values['smt_step']]=dict(values)
 return rows
w=waves(q/'bmc_failure.vcd');top='ka_configured_persistence_formal.';witness=[]
for step,row in sorted(w.items()):
 if step-1 not in w:continue
 prev=w[step-1];get=lambda d,n:d[top+n]
 if not get(row,'rst') and not get(prev,'rst') and get(prev,'configured') and get(prev,'bound_generation') and not(get(prev,'rearm_valid') and get(prev,'rearm_ready')) and not get(row,'configured'):witness.append(step)
assert witness
cap=B/'ka_configured_persistence_evidence_v1';cap.mkdir();files={}
for root in [p,B/'ka_configured_persistence_clear_on_request_v1',q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in list((R/'hardware/variants/ka_configured_persistence_formal_v1').glob('*'))+list((R/'scripts/research_checks').glob('*configured_persistence*.py'))+[R/'scripts/research_checks/prepare_selected_state_cone_v2.py',R/'scripts/shadow_terminal_receipt_v1.py']:
 files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'configured_persistence_actual_transition_overapproximation_inductively_proved_fault_witness_restored','retained_state_bits':271,'selected_cells':pr['selected_cells'],'cuts':len(pr['cuts']),'assertions':11,'assumptions':1,'covers':2,'fault_bmc_witness_vcd_steps':witness,'fault_v1':'10-step BMC passed but induction failed; v2 same model with 20-step BMC finds reachable abstraction witness.','scope':'Configured persists after nonzero active generation unless prior accepted rearm or cold reset. Covers and fault witness are abstract model reachability only; not full-system stimulus.','archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_configured_persistence_formal_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:report[k] for k in ['status','fault_bmc_witness_vcd_steps','archive_sha256']}))
if __name__=='__main__':pass
