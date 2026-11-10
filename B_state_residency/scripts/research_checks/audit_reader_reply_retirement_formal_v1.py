"""Independent combinational transition-cut and witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_reader_reply_retirement_formal_v7';q=B/'ka_reader_reply_no_clear_rsp_control_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==101 and len(pr['retained_state_cells'])==21
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
h=(p/'harness.sv').read_text();assert sha(p/'harness.sv')==m['harness_sha256'];assert h.count('assert(')==42 and h.count('assume(')==1 and h.count('cover(')==5
import re,collections
previous=None
for version in range(1,8):
 root=B/('ka_reader_reply_retirement_formal_v'+str(version));text=(root/'harness.sv').read_text();expressions=collections.Counter(re.findall(r'assert\((.*?)\);',text,re.S))
 if previous is not None:assert not (previous-expressions),'prior target/auxiliary assertion removed'
 previous=expressions
 if version<7:assert j(root/'manifest.json')['status']=='failed'
 if version==1:assert 'Status: FAILED' in (root/'bmc.log').read_text()
 elif version<7:assert 'Status: PASSED' in (root/'bmc.log').read_text() and 'Temporal induction failed' in (root/'induction.log').read_text()
binding=j(p/'memory_binding.json');assert sha(p/'memory_binding.json')==m['memory_binding_sha256'];assert sha(p/'memory_control.sv')==binding['memory_sha256']==m['memory_control_sha256'];assert sha(Path(binding['review']))==binding['review_sha256']
assert (p/'memory_control.sv').read_bytes()==(B/'ka_dual_bank_memory_pending_formal_v2/memory_control.sv').read_bytes()
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
positive=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==5
assert any(r.get('rst')==0 and r.get('memory_rp')==1 and r.get('f_bank0_pending')==1 for r in positive)
assert any(r.get('rst')==0 and r.get('memory_rp')==1 and r.get('f_bank1_pending')==1 for r in positive)
assert any(r.get('rst')==0 and r.get('saw_memory_read')==1 and r.get('rsp_valid')==1 and r.get('rsp_ready')==1 for r in positive)
def steps(path):return {r['smt_step']:r for r in wave(path) if 'smt_step' in r}
returns=[];retirements=[]
for f in p.glob('cover*.vcd'):
 w=steps(f)
 for k,r in w.items():
  if k-1 not in w or r.get('rst')!=0 or w[k-1].get('rst')!=0:continue
  old=w[k-1]
  if r.get('f_state')==0 and old.get('f_state')==4 and r['f_axi_bank']!=old['f_axi_bank']:returns.append(k)
  if old.get('rsp_valid')==1 and old.get('rsp_ready')==1 and r.get('busy')==0 and r.get('drained')==1:retirements.append(k)
assert returns and retirements
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('rst')==0 and r.get('rsp_valid')==1 and r.get('f_store0_rsp_valid')==1 and r.get('f_store0_busy')==1];assert bad
cap=B/'ka_reader_reply_retirement_evidence_v1';cap.mkdir();files={}
for root in [B/('ka_reader_reply_retirement_formal_v'+str(v)) for v in range(1,8)]+[q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py',Path(binding['review']),R/'results/ka_reader_reply_retirement_v1_abstraction_failure_20261101.json']+list((R/'scripts/research_checks').glob('run_reader_reply*.py'))+list((R/'hardware/variants').glob('ka_reader_reply_retirement_formal_v*/*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_reader_reply_and_response_retirement_idle_drained_inductively_proved_fault_control_restored','retained_bank_codec_bits':101,'assertions':42,'assumptions':1,'covers':5,'configuration_return_vcd_steps':returns,'retirement_vcd_steps':retirements,'fault_values':[{n:r.get(n) for n in ['rsp_valid','f_reader0_state','f_store0_rsp_valid','f_store0_busy','memory_rp','drained']} for r in bad],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Actual selected reader/codec transitions plus reviewed single-beat read-only fixture control. Reply valid implies drained/no pending/codec idle; next non-reset cycle after external reply handshake is !busy and drained. All data/status inputs arbitrary. Covers/fault are abstract model reachability; not full fixture or AS-ready proof.','history':'v1 BMC failure from arbitrary stopped losing timeout latch; v2-v6 BMC pass/induction fail histories preserved. v2 retains original stopped DFFs; v3-v7 only add readonly aliases and actual state/phase/GET/AR-R invariants. No previous assertion removed or environment assumptions added.','remaining':['First AS after DRAIN and later AS after AW require history composition and no competing requests.','AS configured/fault and all ready qualifiers still need combined review.','Full shadow KA stalled gate unchanged; full start/release probe waits memory.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_reader_reply_retirement_formal_v7_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
