"""Audit source-reviewed fixture control projection, not full RTL equivalence."""
from pathlib import Path
import hashlib,json,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_axi_read_pending_control_v2';q=B/'ka_axi_read_pending_no_clear_control_v1';pr=j(p/'projection.json');m=j(p/'manifest.json')
assert m['status']=='observed' and sha(p/'projection.json')==m['projection_sha256']
assert sha(p/'harness.sv')==pr['harness_sha256']==m['harness_sha256']
for f,h in pr['source_sha256'].items():assert sha(Path(f))==h
memory=next(Path(f).read_text() for f in pr['source_sha256'] if f.endswith('/axi_file_memory.sv'))
for f in pr['checked_memory_fragments']:assert f in memory and f in (p/'harness.sv').read_text()
reader=next(Path(f).read_text() for f in pr['source_sha256'] if f.endswith('/checkpoint_authority_reader.sv'))
assert pr['reader_process'] in reader and pr['reader_process'] in (p/'harness.sv').read_text()
h=(p/'harness.sv').read_text();assert 'rlast<=0;rdpos<=0;delay_r<=0;' in h and 'rdlen<=0;' not in h
assert h.count('assert(')==4 and h.count('assume(')==1 and h.count('cover(')==2
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
assert (q/'harness.sv').read_text()==h.replace('if(m_rvalid&&m_rready&&m_rlast)read_pending<=0;','if(m_rvalid&&m_rready&&m_rlast)read_pending<=read_pending;')
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
assert any(r.get('rst')==0 and r.get('rvalid')==1 and r.get('rready')==1 and r.get('read_pending')==1 for r in rows)
assert any(r.get('rst')==0 and r.get('read_pending')==0 and r.get('rvalid')==0 and r.get('past_valid')==1 for r in rows)
assert any(r.get('rst')==0 and r.get('rp')==0 and r.get('read_pending')==1 for r in wave(q/'bmc_failure.vcd'))
cap=B/'ka_axi_read_pending_control_evidence_v1';cap.mkdir();files={}
for root in [B/'ka_axi_read_pending_control_v1',p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in list((R/'scripts/research_checks').glob('*axi_read_pending*.py'))+[R/'results/ka_axi_read_pending_control_v1_scope_correction_20261031.json']+list((R/'hardware/variants/ka_axi_read_pending_control_v1').glob('*'))+list((R/'hardware/variants/ka_axi_read_pending_control_v2').glob('*')):files['repo/'+str(f.relative_to(R))]=f
for f in pr['source_sha256']:files['sources/'+Path(f).name]=Path(f)
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'single_beat_fixture_source_reviewed_control_projection_inductively_proved_negative_control_restored','assertions':4,'assumptions':1,'covers':2,'source_projection':pr,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Source-reviewed control projection only: current single-beat legal fixture, common reset, no data/file-I/O/fatal-shape semantics. rp equals read_pending; R valid implies pending. This is not automatic formal equivalence to original memory or dual-bank system.','remaining':['Prove original memory control projection equivalence if used as formal full-system contract.','Handle private reader reset, shared AXI bank routing and state transitions.','AS drained and ready not established.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_axi_read_pending_control_v2_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
