"""Two bounded XSim attempts: original rejection control and isolated interlock."""
from pathlib import Path
import json,os,re,shutil,subprocess,sys,time
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,BIN,sha,read,identity,host_identity,memory_admission
P=BASE/'publication_start_interlock_slice_v1'

def main():
 assert not P.exists();P.mkdir()
 source=BASE/'stage_static_cp_synth_v1/sources';variant=R/'hardware/variants/publication_start_interlock_v1';candidate=read(variant/'manifest.json')
 for p,h in candidate['evidence_sha256'].items():assert sha(p)==h
 assert sha(variant/'candidate/query_residency_system.sv')==candidate['candidate_sha256']
 tb=R/'hardware/variants/publication_start_interlock_slice_v1/tb_interlock.sv';text=tb.read_text()
 assert 'assign command_valid=jp_start||ap_valid||cp_valid||qc_cp_valid;' in text
 assert candidate['exact_reversible_replacement']['after']=='.command_valid(jp_start||ap_valid||cp_valid||qc_cp_valid)'
 assert not os.environ.get('LD_PRELOAD')
 for role in ['original','candidate']:
  d=P/role;d.mkdir()
  for n in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv']:shutil.copyfile(source/n,d/n)
  shutil.copyfile(tb,d/'tb_interlock.sv')
  (d/'run.tcl').write_text('run 20 us\nquit\n')
 inputs={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file()}
 evidence={str(p):sha(p) for p in [tb,variant/'manifest.json',variant/'candidate/query_residency_system.sv',source/'checkpoint_lease_guard.sv',source/'checkpoint_publish_barrier.sv',R/'scripts/stage_static_cp_physical_common_v6.py',R/'results/stage_static_cp_physical_v6_20261104.json']}
 m=dict(status='running',stage='wait_memory',runner_pid=os.getpid(),runner_start_ticks=identity(os.getpid()),runner_sha256=sha(__file__),**host_identity(),inputs=inputs,evidence_sha256=evidence,commands=[],candidate_accepted=False,production_rtl_modified=False,scope='Actual lease guard and publication barrier RTL slice, modeled surrounding conditions and fixed metadata. Not full query integration, arbitrary-input proof, caller contract proof, synthesis or production repair.')
 def save():
  q=P/'manifest.pending.json';q.write_text(json.dumps(m,indent=2,sort_keys=True)+'\n');q.replace(P/'manifest.json')
 def validate():
  for n,h in inputs.items():assert sha(P/n)==h
  for p,h in evidence.items():assert sha(p)==h
 save()
 try:
  memory_admission(m,save);validate()
  for role in ['original','candidate']:
   d=P/role
   cmd=[[str(BIN.parent/'xvlog'),'--sv']+(['-d','ORIGINAL_WIRING'] if role=='original' else [])+['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv','tb_interlock.sv'],
    [str(BIN.parent/'xelab'),'tb_interlock','-s','interlock','--debug','typical','--mt','2'],
    [str(BIN.parent/'xsim'),'interlock','--tclbatch','run.tcl','--log','simulate.log']]
   for stage,argv in zip(['compile','elaborate','simulate'],cmd):
    validate();m['stage']=role+'_'+stage;save();start=time.monotonic()
    with (d/(stage+'.stdout.log')).open('x') as log:
     child=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);ticks=identity(child.pid)
     m['active_process']=dict(pid=child.pid,start_ticks=ticks,argv=argv);save();code=child.wait()
    m.pop('active_process');m['commands'].append(dict(role=role,stage=stage,argv=argv,pid=child.pid,start_ticks=ticks,exit_code=code,elapsed_s=time.monotonic()-start,stdout_sha256=sha(d/(stage+'.stdout.log'))));save();assert code==0
   text=(d/'simulate.log').read_text()
   if role=='original':
    assert text.count('Fatal:')==1 and 'INTERLOCK_CHECK SIMULTANEOUS_RELEASE_NOT_BLOCKED' in text and 'INTERLOCK_SLICE_PASS' not in text
   else:
    assert 'Fatal:' not in text and 'ERROR:' not in text and text.count('INTERLOCK_SLICE_PASS')==1
    assert len(re.findall(r'^INTERLOCK_CASE id=',text,re.M))==10
   print(role,'observed',flush=True)
  validate();m.update(status='observed',stage='complete',artifact_sha256={str(f.relative_to(P)):sha(f) for f in P.rglob('*') if f.is_file() and f.name not in ['manifest.json','manifest.pending.json']})
 except BaseException as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
