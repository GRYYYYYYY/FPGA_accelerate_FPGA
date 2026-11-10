"""Observe the existing generator, then audit and launch the authorized replay once."""
from pathlib import Path
import hashlib,json,os,subprocess,time
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'results/checkpoint_replay_workflow_20261023'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 OUT.mkdir()
 generator=ROOT/'results/checkpoint_vectors_full_20261023/manifest.json'
 g=json.loads(generator.read_text());pid=g['pid']
 process=Path('/proc')/str(pid)/'cmdline'
 identity=process.read_bytes() if process.exists() else b''
 if g['status']=='running':assert b'make_checkpoint_vectors.py' in identity and b'checkpoint_vectors_full_20261023' in identity
 files=[Path(__file__).resolve(),*[ROOT/'hardware/scripts'/n for n in ['audit_checkpoint_vectors.py','run_checkpoint_stream.py','audit_checkpoint_replay.py']]]
 m={'status':'waiting_for_existing_generator','pid':os.getpid(),'generator_pid':pid,'sources':{str(p):sha(p) for p in files},'commands':[],'goal_completed':False}
 for p in files:(OUT/p.name).write_bytes(p.read_bytes())
 def save():
  tmp=OUT/'manifest.tmp';tmp.write_text(json.dumps(m,indent=2)+'\n');tmp.replace(OUT/'manifest.json')
 def verify_sources():
  for path,digest in m['sources'].items():assert sha(Path(path))==digest
 def run(stage,args):
  verify_sources();m['status']=stage
  with (OUT/(stage+'.log')).open('w') as log:
   proc=subprocess.Popen(args,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
   row={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};m['commands'].append(row);save()
   row['exit_code']=proc.wait();save();assert row['exit_code']==0,stage
 save()
 try:
  while True:
   try:g=json.loads(generator.read_text())
   except json.JSONDecodeError:
    if not process.exists():raise
    time.sleep(1);continue
   m['queries_generated']=len(g['queries_completed']);save()
   if g['status']=='passed' and (generator.parent/'completion_audit.json').exists():break
   assert g['status']=='running','Generator did not pass'
   assert process.exists() and process.read_bytes()==identity,'Original generator no longer live'
   time.sleep(10)
  assert not (ROOT/'results/rtl_checkpoint_stream_full_20261023').exists(),'Replay directory already exists; refusing duplicate'
  run('vector_audit',['python3','hardware/scripts/audit_checkpoint_vectors.py','results/checkpoint_vectors_full_20261023'])
  run('rtl_replay',['python3','hardware/scripts/run_checkpoint_stream.py','results/rtl_checkpoint_stream_full_20261023','--full'])
  run('final_audit',['python3','hardware/scripts/audit_checkpoint_replay.py'])
  m['status']='replay_audited';save();print('WORKFLOW_REPLAY_AUDITED research goal remains open',flush=True)
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
