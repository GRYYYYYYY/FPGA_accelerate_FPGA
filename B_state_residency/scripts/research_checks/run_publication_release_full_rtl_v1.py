"""One bounded full-RTL early probe, with unchanged conservative memory admission."""
from pathlib import Path
import hashlib,json,subprocess,os,sys,time,shutil
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shadow_terminal_receipt_v1 import record_child_exit,record_exception
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_full_rtl_v1';d=p/'full'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ident(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
assert not (p/'manifest.json').exists();pr=json.loads((p/'preparation.json').read_text());assert pr['status']=='prepared_not_running'
helper=R/'scripts/shadow_terminal_receipt_v1.py';cal=R/'results/shadow_terminal_receipt_v1_calibration_20261031.json';assert json.loads(cal.read_text())['helper_sha256']==sha(helper)
m={'status':'running','stage':'wait_memory','runner_pid':os.getpid(),'runner_start_ticks':ident(os.getpid()),'runner_sha256':sha(Path(__file__)),'preparation_sha256':sha(p/'preparation.json'),'helper_sha256':sha(helper),'memory_policy':pr['memory_policy'],'commands':[]}
def save():
 temp=p/'manifest.pending.json';temp.write_text(json.dumps(m,indent=2)+'\n');temp.replace(p/'manifest.json')
def validate():
 assert sha(p/'preparation.json')==m['preparation_sha256']
 for n,h in pr['sources'].items():assert sha(p/'sources'/n)==h
 assert sha(d/'run.tcl')==pr['run_tcl_sha256']
 assert sha(p/'input_plan.json')==pr['input_plan_sha256']
child=None;save()
try:
 validate();start=None
 while True:
  cg=Path('/sys/fs/cgroup');current=int((cg/'memory.current').read_text());limit=int((cg/'memory.max').read_text());now=time.monotonic()
  if current<=pr['memory_policy']['total_current_max_gib']*1024**3:
   if start is None:start=now
  else:start=None
  m['memory_observation']={'time_utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),'current_bytes':current,'limit_bytes':limit,'stable_seconds':0 if start is None else now-start};save()
  if start is not None and now-start>=pr['memory_policy']['stable_seconds']:break
  time.sleep(pr['memory_policy']['poll_seconds'])
 validate();m['stage']='prepare_fresh_inputs';save();plan=json.loads((p/'input_plan.json').read_text());assert sha(Path(plan['binding']))==plan['binding_sha256'];regions=plan['regions']
 for e in regions.values():assert Path(e['path']).stat().st_size==e['bytes'] and sha(Path(e['path']))==e['sha256']
 for name,key in [('design.bin','design'),('cost.bin','cost_history_prices_nets'),('allocator.bin','owner_allocator')]:shutil.copyfile(regions[key]['path'],d/name)
 with (d/'owners.bin').open('wb') as out:
  for key in ['owners','owner_pool','owner_allocator']:
   with Path(regions[key]['path']).open('rb') as inp:shutil.copyfileobj(inp,out)
 for n in ['snapshot.bin','pool.bin','g3.bin']:shutil.copyfile(d/'owners.bin',d/n)
 with (d/'labels.bin').open('wb') as out:out.truncate(3145728)
 m['fresh_input_sha256']={n:sha(d/n) for n in ['design.bin','cost.bin','allocator.bin','owners.bin','snapshot.bin','pool.bin','g3.bin','labels.bin']};save()
 for stage,argv in zip(['compile','elaborate','simulate'],pr['commands']):
  validate();m['stage']=stage;begin=time.monotonic()
  with (d/(stage+'.stdout.log')).open('w') as log:
   child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);m['active_process']={'pid':child.pid,'start_ticks':ident(child.pid),'argv':argv};save();code=child.wait()
  record_child_exit(m,code);m['commands'].append({'stage':stage,'exit_code':code,'argv':argv,'elapsed_s':time.monotonic()-begin,'stdout_sha256':sha(d/(stage+'.stdout.log'))});save();assert code==0
  print(stage,'observed',flush=True)
 text=(d/'simulate.log').read_text();assert 'Fatal:' not in text and 'ERROR:' not in text
 for marker in pr['expected_markers']:assert text.count(marker)==1
 m.update(status='reproduction_observed',stage='complete',scope=pr['scope'],full_system_functional_netlist_validated=False,physical_gate_open=False)
except BaseException as e:record_exception(m,e,child);raise
finally:save()
