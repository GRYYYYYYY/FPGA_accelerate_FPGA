"""Source-bound AP ownership/busy proof and negative witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_ap_ownership_busy_formal_v2';q=B/'ka_ap_ownership_no_clear_control_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==12 and len(pr['retained_state_cells'])==6
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n]
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
for n in pr['retained_state_cells']:assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
mapped=j(p/'combinational_bitmapped.json')['modules'][cfg['module']]
bit_remap={}
for name,net in b['netnames'].items():
 if name not in mapped['netnames']:continue
 newer=mapped['netnames'][name]['bits']
 assert len(net['bits'])==len(newer)
 for oldbit,newbit in zip(net['bits'],newer):
  if oldbit in bit_remap:assert bit_remap[oldbit]==newbit
  bit_remap[oldbit]=newbit
for n in pr['retained_state_cells']:
 original=b['cells'][n];newer=mapped['cells'][n]
 for key in ['type','parameters','attributes','port_directions']:assert original[key]==newer[key]
 for port,bits in original['connections'].items():assert [bit_remap.get(v,v) for v in bits]==newer['connections'][port]
assert 'scc -expect 0' in (p/'prepare.ys').read_text()
log=(p/'prepare.log').read_text();assert 'Found 0 SCCs' in log and 'Found and reported 0 problems.' in log
m=j(p/'manifest.json');assert m['status']=='observed'
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
for s in m['sources'].values():assert sha(Path(s['source']))==s['sha256']
assert sha(p/'kernel.json')==m['kernel_json_sha256'] and sha(p/'harness.sv')==m['harness_sha256']
h=(p/'harness.sv').read_text();assert h.count('assert(')==6 and h.count('assume(')==1 and h.count('cover(')==2
assert (q/'harness.sv').read_bytes()==(p/'harness.sv').read_bytes();mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']]
assert set(fault['cells'])-set(b['cells'])=={'ap_fault_not_cold','ap_fault_hold_gate','ap_fault_no_clear'}
for n,c in b['cells'].items():
 d=json.loads(json.dumps(fault['cells'][n]))
 if n==mut['changed_dff']:d['connections']['D']=mut['original_D']
 assert d==c
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
assert any(r.get('f_ap_owned')==1 and r.get('as_busy')==1 and r.get('f_k_cold_rst')==0 for r in wave(p/'cover0.vcd'))
assert any(r.get('f_ap_owned')==0 and r.get('as_busy')==0 and r.get('f_k_cold_rst')==0 for r in wave(p/'cover1.vcd'))
assert any(r.get('f_ap_owned')==1 and r.get('as_busy')==0 and r.get('f_k_cold_rst')==0 for r in wave(q/'bmc_failure.vcd'))
failed=B/'ka_ap_ownership_busy_formal_v1';assert 'Found logic loop' in (failed/'prepare.log').read_text();assert j(failed/'manifest.json')['status']=='failed'
cap=B/'ka_ap_ownership_busy_evidence_v1';cap.mkdir();files={}
for root in [failed,p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py',R/'results/ka_full_actual_rtl_model_v1_review_20261031.json']+list((R/'scripts/research_checks').glob('run_ap_ownership*.py'))+list((R/'hardware/variants/ka_ap_ownership_busy_formal_v1').glob('*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_ap_owned_implies_authority_busy_inductively_proved_fault_control_restored','retained_bits':12,'selected_cells':pr['selected_cells'],'cuts':len(pr['cuts']),'assertions':6,'assumptions':1,'covers':2,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual full-source transitions overapproximation: outside cold reset AP owned implies authority busy, parent IDLE and active reader request/reply state. KA valid excludes new AP offer. Covers and fault trace are abstract reachability.','remaining':['Compose DRAIN no-busy and AP-owned implication with AP offer exclusion through AS.','Prove AS quiet/drained and configuration/publication exclusion.','No full-system KA-ready or acceptance conclusion.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_ap_ownership_busy_formal_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
