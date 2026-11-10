"""Observe the single frozen recovery run; audit once, never restart HLS."""
from pathlib import Path
import json,os,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/'results/frontier_hls_relative_project_20261024'
receipt=out/'audit_watch.json'
state={'status':'waiting','pid':os.getpid(),'policy':'observe existing flow; audit once; no restart'}
def save():receipt.write_text(json.dumps(state,indent=2)+'\n')
save()
while True:
 m=json.loads((out/'manifest.json').read_text())
 if m['status'] in ['passed','failed']:
  state['flow_status']=m['status']
  if m['status']=='passed':
   with (out/'audit.stdout.log').open('w') as log:
    result=subprocess.run([sys.executable,str(ROOT/'scripts/audit_frontier_hls.py')],cwd=ROOT,stdout=log,stderr=subprocess.STDOUT)
   state['audit_exit_code']=result.returncode
   state['status']='audited' if result.returncode==0 else 'audit_failed'
  else:state['status']='flow_failed'
  save();break
 try:os.kill(m['pid'],0)
 except ProcessLookupError:
  state['status']='owner_exited_without_terminal_receipt';save();break
 time.sleep(15)
