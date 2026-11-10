"""Independent combinational transition-cut and witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_reader_quiet_persistence_formal_v1';q=B/'ka_reader_quiet_spontaneous_fault_control_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==103 and len(pr['retained_state_cells'])==23
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
h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assert(')==45 and h.count('assume(')==1 and h.count('cover(')==6
import re,collections
old=(B/'ka_reader_reply_retirement_formal_v7/harness.sv').read_text();assert not(collections.Counter(re.findall(r'assert\((.*?)\);',old,re.S))-collections.Counter(re.findall(r'assert\((.*?)\);',h,re.S)))
binding=j(p/'memory_binding.json');assert sha(p/'memory_binding.json')==m['memory_binding_sha256'];assert sha(p/'memory_control.sv')==binding['memory_sha256']==m['memory_control_sha256'];assert sha(Path(binding['review']))==binding['review_sha256']
assert (q/'harness.sv').read_text()==h and (q/'memory_control.sv').read_bytes()==(p/'memory_control.sv').read_bytes();mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']];assert set(fault['cells'])-set(b['cells'])==set(mut['added_cells'])
for n,c in b['cells'].items():
 d=json.loads(json.dumps(fault['cells'][n]))
 if n==mut['changed_dff']:d['connections']['D']=mut['original_D']
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
positive=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==6
assert any(r.get('rst')==0 and r.get('saw_memory_read')==1 and r.get('rsp_valid')==1 and r.get('rsp_ready')==1 and r.get('fault')==0 for r in positive)
def steps(path):return {r['smt_step']:r for r in wave(path) if 'smt_step' in r}
bad=[];w=steps(q/'bmc_failure.vcd')
for k,r in w.items():
 if k-1 not in w:continue
 old=w[k-1]
 if r.get('rst')==0 and old.get('rst')==0 and old.get('busy')==0 and old.get('drained')==1 and old.get('fault')==0 and old.get('abort')==0 and all(old.get(n)==0 for n in ['cfg_valid','publish_valid','discard_valid','rearm_valid','req_valid']) and r.get('fault')==1:bad.append({'step':k,'previous':old,'current':r})
assert bad
cap=B/'ka_reader_quiet_persistence_evidence_v1';cap.mkdir();files={}
for root in [p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py',Path(binding['review']),R/'scripts/research_checks/run_reader_quiet_persistence_formal_v1.py',R/'scripts/research_checks/run_reader_quiet_spontaneous_fault_control_v1.py']+list((R/'hardware/variants/ka_reader_quiet_persistence_formal_v1').glob('*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_reader_quiet_and_fault_free_persistence_inductively_proved_fault_control_restored','retained_bank_codec_bits':103,'assertions':45,'assumptions':1,'covers':6,'contracts':['Idle/drained persists on next non-reset cycle if previously idle/drained and no cfg/publish/discard/rearm/request.','If additionally previously no fault and no abort, idle/drained/no-fault persists.','If previously response valid/ready with no fault/abort, next non-reset cycle is idle/drained/no-fault.'],'fault_witness_steps':[r['step'] for r in bad],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual reader/codec transitions plus source-derived single-beat read-only fixture control; arbitrary data/status inputs. Covers/fault are abstraction-only. All42 prior retirement assertions retained. No AS-ready/full-system acceptance yet.','full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_reader_quiet_persistence_formal_v1_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
