"""Independent source/cut/pruning audit for stronger lease-state abstraction."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_as_lease_staging_boundary_formal_v1';q=B/'ka_as_lease_boundary_recover_gate_fault_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
br=j(p/'boundary_preparation.json');parent=Path(br['parent']);pr=j(parent/'preparation.json');cfg=pr['configuration'];assert sha(parent/'kernel.json')==br['parent_kernel_sha256'];assert sha(parent/'preparation.json')==br['parent_preparation_sha256'];assert sha(Path(cfg['source_json']))==cfg['source_json_sha256']
original=j(Path(cfg['source_json']))['modules'][cfg['module']];old=j(parent/'kernel.json')['modules'][cfg['module']];new=j(p/'kernel.json')['modules'][cfg['module']]
for n,c in old['cells'].items():
 if n not in pr['cuts']:assert c==original['cells'][n]
 else:
  cut=pr['cuts'][n];assert original['cells'][n]['connections'][cut['original_port']]==cut['bits'];assert c['type']=='$anyseq' and c['connections']=={'Y':cut['bits']}
assert br['retained_state_bits']==pr['retained_state_bits']==9 and len(br['retained_state_cells'])==3
for n in br['retained_state_cells']:assert old['cells'][n]==new['cells'][n]==original['cells'][n] and new['cells'][n]['connections']['CLK']==original['ports']['clk']['bits']
for k,v in old.items():
 if k!='cells':assert new[k]==v
cells=dict(old['cells']);assert len(br['scalar_cuts'])==20
for n,entry in br['scalar_cuts'].items():
 c=old['cells'][n];assert c==entry['original_cell'] and n not in br['retained_state_cells'] and c['type'] not in ['$dff','$anyseq']
 outputs=[v for port,v in c['connections'].items() if c['port_directions'][port]=='output'];assert len(outputs)==1 and len(outputs[0])==1 and isinstance(outputs[0][0],int)
 assert old['netnames'][entry['signal']]['bits']==outputs[0]
 cells[n]={'hide_name':1,'type':'$anyseq','parameters':{'WIDTH':format(1,'032b')},'attributes':{},'port_directions':{'Y':'output'},'connections':{'Y':outputs[0]}}
drivers={}
for n,c in cells.items():
 for port,bits in c['connections'].items():
  if c['port_directions'][port]=='output':
   for bit in bits:
    if isinstance(bit,int):assert bit not in drivers;drivers[bit]=n
pending=[b for n in cfg['state_names']+cfg['roots']+list(cfg['observations'].values()) for b in old['netnames'][n]['bits']];seen=set();expected={}
while pending:
 bit=pending.pop()
 if not isinstance(bit,int) or bit in seen:continue
 seen.add(bit);n=drivers.get(bit)
 if n is None or n in expected:continue
 c=cells[n];expected[n]=c
 for port,bits in c['connections'].items():
  if c['port_directions'][port]=='input':pending.extend(bits)
assert new['cells']==expected and len(expected)==5526
inputs={v for c in new['ports'].values() if c['direction']=='input' for v in c['bits']}
for c in expected.values():
 for port,bits in c['connections'].items():
  if c['port_directions'][port]=='input':assert all(not isinstance(b,int) or b in drivers or b in inputs for b in bits)
m=j(p/'manifest.json');assert m['status']=='observed';assert sha(p/'kernel.json')==m['kernel_json_sha256'];assert sha(p/'boundary_preparation.json')==m['boundary_preparation_sha256']
assert (p/'harness.sv').read_bytes()==(parent/'harness.sv').read_bytes() and sha(p/'harness.sv')==m['harness_sha256'];h=(p/'harness.sv').read_text();assert h.count('assert(')==8 and h.count('assume(')==1 and h.count('cover(')==2
for e in m['sources'].values():assert sha(Path(e['source']))==e['sha256']
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
assert 'Found 0 SCCs' in (p/'prepare.log').read_text()
assert (q/'harness.sv').read_text()==h;mut=j(q/'mutation.json');fault=j(q/'kernel.json')['modules'][cfg['module']];assert set(fault['cells'])==set(new['cells'])
for n,c in new['cells'].items():
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
  elif z[0]=='$var' and len(scopes)==1:names[z[3]]=z[4]
  elif l.startswith('#'):
   if vals:rows.append(dict(vals))
  elif l.startswith('b'):
   bits,code=l[1:].split()
   if code in names and all(c in '01' for c in bits):vals[names[code]]=int(bits,2)
  elif l[0] in '01' and l[1:] in names:vals[names[l[1:]]]=int(l[0])
 if vals:rows.append(vals)
 return rows
rows=[r for f in p.glob('cover*.vcd') for r in wave(f)];assert len(list(p.glob('cover*.vcd')))==2
assert any(r.get('f_k_cold_rst')==0 and r.get('k_a_valid')==1 and r.get('f_authority_cfg_valid')==0 for r in rows)
assert any(r.get('f_k_cold_rst')==0 and r.get('f_lease_owned')==1 and r.get('f_prepare_allowed')==1 for r in rows)
bad=[r for r in wave(q/'bmc_failure.vcd') if r.get('f_k_cold_rst')==0 and r.get('f_lease_owned')==1 and (r.get('f_filtered_recover_valid')==1 or r.get('f_fence_state',0)>=7 or r.get('f_coordinator_state',0)!=0)];assert bad
cap=B/'ka_lease_temporal_boundary_evidence_v1';cap.mkdir();files={}
for root in [p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/prepare_lease_temporal_boundary_v1.py',R/'scripts/research_checks/run_as_lease_staging_boundary_formal_v1.py',R/'scripts/research_checks/run_as_lease_boundary_recover_gate_fault_v1.py',parent/'kernel.json',parent/'preparation.json']:files['bound/'+f.name if not f.is_relative_to(R) else 'repo/'+str(f.relative_to(R))]=f
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'actual_lease_temporal_boundary_overapproximation_inductively_proved_fault_control_restored','retained_bits':9,'scalar_comb_boundaries':20,'selected_cells':5526,'assertions':8,'assumptions':1,'covers':2,'abstraction_argument':'Each removed scalar producer is replaced by unconstrained one-bit value at identical shared bit/aliases; choosing its original output reproduces any parent trace. Only unreachable fanin after those cuts is pruned; full traversal independently reconstructed; all original retained DFFs/clock/reset unchanged. No extra environment assumptions.','proved':'Outside cold reset lease owned implies fence not recovering/coordinator NORMAL; AS implies lease absent and authority cfg_valid/prepare_allowed absent.','scope':'Safety proof lifts to original initialized two-state RTL through overapproximation. Covers and gate fault traces are abstraction-only; no arbitrary-parameter/XZ or full-fixture simulation acceptance. Original uncut proof jobs remain unaccepted/running.','archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'fault_scope':'First failure may hit intermediate lease/recovery invariant rather than AS overlap.','full_system_functional_netlist_validated':False,'physical_gate_open':False};out=R/'results/ka_lease_temporal_boundary_v1_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
