"""Independent read-control miter and source-transformation audit."""
from pathlib import Path
import hashlib,json,re,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
p=B/'ka_memory_control_equivalence_v3';q=B/'ka_memory_control_equivalence_no_rp_clear_v1';pr=j(p/'projection.json');m=j(p/'manifest.json');assert m['status']=='observed'
assert sha(p/'projection.json')==m['projection_sha256'] and sha(p/'harness.sv')==pr['harness_sha256']==m['harness_sha256']
for f,h in pr['source_sha256'].items():assert sha(Path(f))==h
original=next(Path(f).read_text() for f in pr['source_sha256'] if f.endswith('/axi_file_memory.sv'));derived=(p/'memory_control.sv').read_text()
for name in ['rng','rp','rvalid','rlast','rdlen','rdpos','delay_r']:
 pattern=r'\b'+name+r'\s*<=\s*([^;]+);'
 before=[re.sub(r'\s+','',v) for v in re.findall(pattern,original)];after=[re.sub(r'\s+','',v) for v in re.findall(pattern,derived)];assert before==after,(name,before,after)
for guard in ['if(rst)begin','if(arvalid&&arready)begin','if(rp&&!rvalid)begin',"if(hold_r===1'b1)begin end",'else if(delay_r!=0)','if(rvalid&&rready)begin']:
 assert guard in original and guard in derived
assert 'assign arready=!rst&&!rp&&!rvalid&&rng[2:0]!=0;' in derived
assert not re.search(r'\$(?:fatal|fdisplay|fflush|fwrite|fseek|fread)',derived)
h=(p/'harness.sv').read_text();assert h.count('assert(')==8 and h.count('assume(')==1 and h.count('cover(')==1
for c in m['commands']:
 assert c['exit_code']==0 and sha(p/(c['stage']+'.log'))==c['log_sha256']
 if c['stage']!='prepare':assert 'Status: PASSED' in (p/(c['stage']+'.log')).read_text()
assert 'used but has no driver' not in (p/'prepare.log').read_text()
assert (q/'harness.sv').read_bytes()==(p/'harness.sv').read_bytes();assert (q/'reference.sv').read_bytes()==(p/'reference.sv').read_bytes()
assert (q/'memory_control.sv').read_text()==derived.replace('if(rdpos==rdlen-1)rp<=0;','if(rdpos==rdlen-1)rp<=rp;')
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
assert any(r.get('rst')==0 and r.get('a_valid')==1 and r.get('rready')==1 for f in p.glob('cover*.vcd') for r in wave(f))
assert any(r.get('rst')==0 and r.get('a_rp')==1 and r.get('b_rp')==0 for r in wave(q/'bmc_failure.vcd'))
for root in [B/'ka_memory_control_equivalence_v1',B/'ka_memory_control_equivalence_v2']:assert j(root/'manifest.json')['status']=='failed'
cap=B/'ka_memory_control_equivalence_evidence_v1';cap.mkdir();files={}
for root in [B/'ka_memory_control_equivalence_v1',B/'ka_memory_control_equivalence_v2',p,q]:
 for f in root.rglob('*'):
  if f.is_file():files[str(f.relative_to(B))]=f
for f in list((R/'scripts/research_checks').glob('*memory_control_equivalence*.py'))+[R/'results/ka_axi_read_pending_control_v2_review_20261031.json']:files['repo/'+str(f.relative_to(R))]=f
for f in pr['source_sha256']:
 path=Path(f)
 if not path.is_relative_to(p):files['bound_sources/'+path.parent.name+'/'+path.name]=path
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'source_derived_read_control_miter_inductively_equivalent_fault_control_restored','assertions':8,'assumptions':1,'covers':1,'compared':['arready','rvalid','rlast','rp','rng','rdpos','rdlen','delay_r'],'source_transformation_sha256':sha(p/'projection.json'),'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'scope':'Original-memory-derived sanitized control is formally equal to previous single-beat control projection. Independently checked original read-control assignments/order/guards unchanged. This is a scoped control miter, not full Verilog simulation/file-data/fatal semantics equivalence. Removing file failures extends continuing control traces; no assertion concerning data/status or file errors is accepted.','remaining':['Dual-bank shared memory pending and private reset integration still pending.','AS quiet/drained and config/publication/rearm exclusion still pending.','No full-system functional or physical acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_memory_control_equivalence_v3_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
