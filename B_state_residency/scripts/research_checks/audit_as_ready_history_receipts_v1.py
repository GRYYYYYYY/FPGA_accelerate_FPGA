"""Verify conditional history proof and dependencies; integration deliberately pending."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_as_ready_history_composition_formal_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
pr=j(p/'preparation.json');cfg=pr['configuration'];assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert pr['retained_state_bits']==5 and len(pr['retained_state_cells'])==2
for n,c in b['cells'].items():
 if n not in pr['cuts']:assert c==a['cells'][n]
 else:
  cut=pr['cuts'][n];assert a['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
for n in pr['retained_state_cells']:assert b['cells'][n]['connections']['CLK']==a['ports']['clk']['bits']
for n,c in a['ports'].items():
 if c['direction']=='input':assert b['ports'][n]==c
for n,net in a['netnames'].items():
 v=json.loads(json.dumps(net));v.get('attributes',{}).pop('init',None);assert b['netnames'][n]==v
m=j(p/'manifest.json');assert m['status']=='observed';assert sha(p/'kernel.json')==m['kernel_json_sha256'] and sha(p/'harness.sv')==m['harness_sha256'] and sha(p/'contracts.json')==m['contracts_sha256']
contracts=j(p/'contracts.json')
for n,h in contracts['reports'].items():assert sha(R/'results'/n)==h
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
h=(p/'harness.sv').read_text();assert h.count('assert(')==6 and h.count('assume(')==5 and h.count('cover(')==2
negatives=[]
for name in ['without_drain_contract','without_quiet_persistence','without_response_retirement','without_ready_contract']:
 q=B/('ka_as_ready_history_'+name+'_v1');control=j(q/'control.json');assert (q/'kernel.json').read_bytes()==(p/'kernel.json').read_bytes();assert (q/'harness.sv').read_text()==h.replace(control['removed_line'],'',1);assert j(q/'manifest.json')['status']=='failed';assert 'Status: FAILED' in (q/'bmc.log').read_text();negatives.append(q)
def steps(path):
 scope=[];names={};vals={};rows={}
 for l in path.read_text().splitlines():
  z=l.split()
  if not z:continue
  if z[0]=='$scope':scope.append(z[2])
  elif z[0]=='$upscope':scope.pop()
  elif z[0]=='$var' and (len(scope)==1 or z[4]=='smt_step'):names[z[3]]=z[4]
  elif l.startswith('#'):
   if 'smt_step' in vals:rows[vals['smt_step']]=dict(vals)
  elif l.startswith('b'):
   bits,code=l[1:].split()
   if code in names and all(c in '01' for c in bits):vals[names[code]]=int(bits,2)
  elif l[0] in '01' and l[1:] in names:vals[names[l[1:]]]=int(l[0])
 if 'smt_step' in vals:rows[vals['smt_step']]=dict(vals)
 return rows
w=steps(p/'cover.vcd');as_rows=[(k,r) for k,r in w.items() if r.get('cold_rst')==0 and r.get('a_valid')==1 and r.get('a_ready')==1 and r.get('f_authority_quiet')==1];assert any(r.get('seen_aw_response')==0 for k,r in as_rows) and any(r.get('seen_aw_response')==1 for k,r in as_rows)
negative_values={}
for q in negatives:
 w=steps(q/'bmc_failure.vcd');bad=[]
 for k,r in w.items():
  if r.get('cold_rst')!=0:continue
  if (r.get('f_state') in [2,3,4,6,7,8,9] and r.get('f_authority_quiet')==0) or (r.get('a_valid')==1 and r.get('a_ready')==0):bad.append({'step':k,'state':r.get('f_state'),'quiet':r.get('f_authority_quiet'),'a_valid':r.get('a_valid'),'a_ready':r.get('a_ready')})
 assert bad;negative_values[q.name]=bad
cap=B/'ka_as_ready_history_receipt_evidence_v1';cap.mkdir();files={}
for root in [p]+negatives:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py']+list((R/'scripts/research_checks').glob('run_as_ready_history*.py'))+list((R/'hardware/variants/ka_as_ready_history_composition_formal_v1').glob('*'))+[R/'results'/n for n in contracts['reports']]:files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'conditional_as_ready_state_history_inductively_proved_dependency_controls_restored_integration_pending','assertions':6,'assumptions':5,'covers':2,'retained_bits':5,'as_trace_steps':[{'step':k,'seen_aw_response':r['seen_aw_response']} for k,r in as_rows],'cover_artifact_scope':'Runner used one cover.vcd, overwritten by second cover. Retained final trace independently contains both first-AS and post-AW-AS witnesses.','negative_values':negative_values,'contracts':contracts,'source_contract_integration_reviewed':False,'remaining':['Independently verify phase-wide admin/AP exclusion and exact request/response clock/reset wiring for all four contracts.','Verify no circular use of the quiet-to-ready condition and actual configured qualifier.','Only then assess native-ready safety scope; full shadow coverage gate is unchanged.'],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Conditional composition receipts, exact selected coordinator transitions and abstract dependency controls. This report does not grant full-system native ready or unconditional KA stall-unreachability acceptance.','full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_as_ready_history_composition_receipt_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
