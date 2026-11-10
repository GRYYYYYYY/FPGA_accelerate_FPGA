"""Local v7-bound physical runtime. Never executes legacy evidence roots."""
from pathlib import Path
import hashlib, json, os, socket, subprocess, time
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/B_state_residency_recovery_20261102')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado')
OUTPUT=BASE/'stage_static_cp_physical_v6'
REVIEW=ROOT/'results/stage_static_cp_physical_v6_preparation_review_20261104.json'
TOOLS=['stage_static_cp_physical_common_v6.py','check_stage_static_cp_physical_inputs_v6.py',
       'prepare_stage_static_cp_physical_v6.py','run_stage_static_cp_physical_v6.py',
       'inspect_stage_static_cp_physical_v6.py','audit_stage_static_cp_physical_v6.py',
       'review_stage_static_cp_physical_preparation_v6.py']
def sha(p):
 h=hashlib.sha256()
 with Path(p).open('rb') as f:
  for block in iter(lambda:f.read(1<<20),b''):h.update(block)
 return h.hexdigest()
def read(p):return json.loads(Path(p).read_text())
def identity(pid):
 try:return Path(f'/proc/{pid}/stat').read_text().rsplit(')',1)[1].split()[19]
 except FileNotFoundError:return None

def runtime_environment():
 rp=ROOT/'results/udev_runtime_recovery_20261030.json';r=read(rp)
 assert r['status']=='runtime_controls_restored' and r['audit']['status']=='passed'
 rec=read(ROOT/'results/physical_v6_runtime_recovery_20261104.json')
 assert rec['status']=='actual_restored_sha_verified'
 assert sha(rec['archive'])==rec['archive_sha256']==r['restoration']['archive_sha256']
 for n,h in rec['files'].items():assert sha(Path(rec['restored_root'])/n)==h,n
 a=Path(rec['restored_root'])/'source_bound_audit.json'
 assert sha(a)==r['restoration']['audit_sha256'] and read(a)==r['audit']
 expected=r['audit']['runtime_library_sha256']
 libs=[BIN.parent.parent/'lib/lnx64.o/libtcmalloc.so.4',Path('/lib/x86_64-linux-gnu/libudev.so.1')]
 assert set(expected)==set(map(str,libs))
 for lib in libs:assert sha(lib)==expected[str(lib)]
 assert not os.environ.get('LD_PRELOAD')
 env=os.environ.copy();env['LD_PRELOAD']=':'.join(map(str,libs))
 return env,dict(LD_PRELOAD=env['LD_PRELOAD'],library_sha256=expected,runtime_report_sha256=sha(rp),recovery_report_sha256=sha(ROOT/'results/physical_v6_runtime_recovery_20261104.json'))

def memory_ok(current,limit):return current<=225*(1<<30) and current*4<=limit*3

def memory_admission(record,save):
 stable=None;deadline=time.monotonic()+10800;record['memory_samples']=[]
 record['memory_policy']=dict(absolute_limit_bytes=225*(1<<30),cgroup_fraction=0.75,continuous_seconds=60,sample_interval_s=5)
 while True:
  cg=Path('/sys/fs/cgroup');cur=int((cg/'memory.current').read_text());lim=int((cg/'memory.max').read_text());now=time.monotonic()
  stable=(now if stable is None else stable) if memory_ok(cur,lim) else None
  sample=dict(current_bytes=cur,limit_bytes=lim,monotonic=now,stable_seconds=0 if stable is None else now-stable)
  record['memory_samples'].append(sample);record['memory_admission']=sample;save()
  if sample['stable_seconds']>=60:return
  assert now<deadline,'Memory admission expired; no Vivado launched'
  time.sleep(5)

def audit_memory(record):
 samples=record['memory_samples'];last=samples[-1];assert last==record['memory_admission']
 assert all(b['monotonic']>a['monotonic'] for a,b in zip(samples,samples[1:]))
 start=len(samples)-1
 while start>0 and memory_ok(samples[start-1]['current_bytes'],samples[start-1]['limit_bytes']):start-=1
 valid=samples[start:];assert all(memory_ok(x['current_bytes'],x['limit_bytes']) for x in valid)
 assert last['monotonic']-valid[0]['monotonic']>=60 and last['stable_seconds']>=60
 assert all(b['monotonic']-a['monotonic']<=15 for a,b in zip(valid,valid[1:])), 'Unobserved memory interval'
 return last

def wait_preserving(child,seconds,record,save):
 try:return child.wait(timeout=seconds)
 except subprocess.TimeoutExpired:
  record.setdefault('observation_timeouts',[]).append(dict(pid=child.pid,start_ticks=identity(child.pid),after_seconds=seconds));save()
 while True:
  try:return child.wait(timeout=30)
  except subprocess.TimeoutExpired:pass

def require_review(p):
 r=read(REVIEW);assert r['status']=='physical_v6_preparation_independently_audited_actual_restored'
 assert r['prepared_manifest_sha256']==sha(p/'preparation.json')
 for path,h in r['tool_sha256'].items():assert sha(path)==h,path
 assert sha(r['archive'])==r['archive_sha256']
 return r

def host_identity():
 return dict(hostname=socket.gethostname(),boot_id=Path('/proc/sys/kernel/random/boot_id').read_text().strip(),cgroup_namespace=os.readlink('/proc/self/ns/cgroup'))
