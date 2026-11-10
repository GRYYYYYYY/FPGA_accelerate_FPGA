"""Wait on an existing experiment, audit it, archive it, and test restoration."""
from pathlib import Path
import json,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def main():
 name,auditor=sys.argv[1:3];p=ROOT/'results'/name;deadline=time.monotonic()+3600
 while True:
  try:m=json.loads((p/'manifest.json').read_text())
  except json.JSONDecodeError:time.sleep(1);continue
  if m['status'] not in ['running','prepared']:break
  assert time.monotonic()<deadline,'observation limit; existing process not terminated'
  time.sleep(10)
 assert m['status'] in ['observed','passed'],m['status']
 if 'fault' in name:assert all(v.get('outcome')=='recovered_retry' for v in m['cases'].values()),'failed/stalled cases retained, no archive pass'
 def run(script,*args):
  r=subprocess.run([sys.executable,str(ROOT/'scripts'/script),*map(str,args)],capture_output=True,text=True)
  assert r.returncode==0,(script,r.stdout[-2000:],r.stderr[-2000:]);print(script,'passed',flush=True)
 run(auditor,p)
 if 'normal' in name:run('compare_search_retire_normal.py',p)
 run('archive_offer_result.py',p)
 run('verify_search_retire_restore.py',name,auditor)
 print('FINALIZATION_PASSED',name,flush=True)
if __name__=='__main__':main()
