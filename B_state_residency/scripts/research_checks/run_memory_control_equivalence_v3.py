"""Run the explicitly scoped AXI memory/reader control projection."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from shadow_terminal_receipt_v1 import record_child_exit,record_exception
B=Path('/tmp/B_state_residency_offer_20261025');R=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def identity(pid):return Path('/proc',str(pid),'stat').read_text().rsplit(')',1)[1].split()[19]
p=B/'ka_memory_control_equivalence_v3';assert not (p/'manifest.json').exists();pr=json.loads((p/'projection.json').read_text());assert sha(p/'harness.sv')==pr['harness_sha256']
for f,h in pr['source_sha256'].items():assert sha(Path(f))==h
helper=R/'scripts/shadow_terminal_receipt_v1.py';cal=R/'results/shadow_terminal_receipt_v1_calibration_20261031.json';assert json.loads(cal.read_text())['helper_sha256']==sha(helper)
m={'status':'running','runner_pid':os.getpid(),'runner_start_ticks':identity(os.getpid()),'runner_sha256':sha(Path(__file__)),'projection_sha256':sha(p/'projection.json'),'harness_sha256':sha(p/'harness.sv'),'helper_sha256':sha(helper),'commands':[]}
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
env=os.environ.copy();tools=B/'ka_formal_packages_v1';env.update(PYTHONPATH=str(tools),XDG_CACHE_HOME=str(B/'ka_formal_cache_v1'),PATH=str(tools/'bin')+':'+env['PATH'])
(p/'prepare.ys').write_text('read_verilog -formal -sv memory_control.sv reference.sv harness.sv\nprep -top ka_memory_control_equivalence\nasync2sync\nchformal -lower\ndffunmap\nwrite_smt2 -wires design.smt2\n')
smt=[sys.executable,str(tools/'bin/yowasp-yosys-smtbmc'),'-s','z3'];jobs=[('prepare',[sys.executable,str(tools/'bin/yowasp-yosys'),'-s','prepare.ys']),('bmc',smt+['-t','10','--dump-vcd','bmc_failure.vcd','design.smt2']),('induction',smt+['-i','-t','10','--dump-vcd','induction_failure.vcd','design.smt2']),('cover',smt+['-c','-t','35','--dump-vcd','cover%.vcd','design.smt2'])];child=None;save()
try:
 for stage,argv in jobs:
  m['stage']=stage;start=time.monotonic()
  with (p/(stage+'.log')).open('w') as log:
   child=subprocess.Popen(argv,cwd=p,env=env,stdout=log,stderr=subprocess.STDOUT);m['active_process']={'pid':child.pid,'start_ticks':identity(child.pid),'argv':argv};save();code=child.wait()
  record_child_exit(m,code);m['commands'].append({'stage':stage,'exit_code':code,'argv':argv,'elapsed_s':time.monotonic()-start,'log_sha256':sha(p/(stage+'.log'))});save();assert code==0
  if stage!='prepare':assert 'Status: PASSED' in (p/(stage+'.log')).read_text()
  print(stage,'observed',flush=True)
 m.update(status='observed',stage='complete')
except BaseException as e:record_exception(m,e,child);raise
finally:save()
