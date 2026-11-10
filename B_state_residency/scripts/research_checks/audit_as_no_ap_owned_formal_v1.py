"""Source-bound AP ownership/busy proof and negative witness audit."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_as_no_ap_owned_formal_v1';q=B/'ka_as_no_ap_owned_no_busy_contract_v1';pr=j(p/'preparation.json');cfg=pr['configuration'];a=j(Path(cfg['source_json']))['modules'][cfg['module']];b=j(p/'kernel.json')['modules'][cfg['module']]
assert sha(Path(cfg['source_json']))==cfg['source_json_sha256'];assert pr['retained_state_bits']==5 and len(pr['retained_state_cells'])==2
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
needed_bits={v for n in pr['retained_state_cells'] for bs in b['cells'][n]['connections'].values() for v in bs}
bit_remap={}
for name,net in b['netnames'].items():
 if name not in mapped['netnames']:continue
 newer=mapped['netnames'][name]['bits']
 assert len(net['bits'])==len(newer)
 for oldbit,newbit in zip(net['bits'],newer):
  if oldbit not in needed_bits:continue
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
h=(p/'harness.sv').read_text();assert h.count('assert(')==6 and h.count('assume(')==2 and h.count('cover(')==2
assert (q/'kernel.json').read_bytes()==(p/'kernel.json').read_bytes()
assert (q/'harness.sv').read_text()==h.replace('  if(f_ap_owned) assume(as_busy);\n','')
assert 'Status: FAILED' in (q/'bmc.log').read_text()
contract=j(p/'contracts.json')['ap_owned_implies_busy'];assert sha(Path(contract['review']))==contract['review_sha256']
assert sha(p/'contracts.json')==m['contracts_sha256']
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
positive_rows=[row for f in p.glob('cover*.vcd') for row in wave(f)]
assert len(list(p.glob('cover*.vcd')))==2
assert any(r.get('k_a_valid')==1 and r.get('f_ap_owned')==0 and r.get('f_k_cold_rst')==0 for r in positive_rows)
assert any(r.get('f_ap_owned')==1 and r.get('f_k_cold_rst')==0 for r in positive_rows)
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('f_ap_owned')==1 and r.get('f_k_cold_rst')==0 and 2<=r.get('f_coordinator_state',99)<=9];assert bad
cap=B/'ka_as_no_ap_owned_evidence_v1';cap.mkdir();files={}
for root in [p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_selected_state_cone_v2.py',Path(contract['review'])]+list((R/'scripts/research_checks').glob('run_as_no_ap_owned*.py'))+list((R/'hardware/variants/ka_as_no_ap_owned_formal_v1').glob('*')):files['repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_as_no_ap_owned_conditional_composition_inductively_proved_dependency_control_restored','retained_bits':5,'assertions':6,'assumptions':2,'covers':2,'contract':contract,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'negative_witness_states':sorted({r['f_coordinator_state'] for r in bad}),'scope':'Actual AP-owned/coordinator-state transitions plus independently proved AP-owned implies authority busy. AS has neither historical owned AP nor new AP offer. Abstract covers are not full fixture stimulation.','remaining':['AS quiet/drained persistence and configuration/publication/rearm exclusion.','Actual reader/native ready, then full coverage failure disposition; physical gate remains closed.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_as_no_ap_owned_formal_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
