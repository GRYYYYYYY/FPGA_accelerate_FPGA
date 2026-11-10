"""Single downstream submission after completed epoch16 functional/physical gates."""
from pathlib import Path
import json,hashlib,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_epoch16_full_workflow_20261024';out.mkdir()
 m={'status':'checking_gates','pid':os.getpid(),'commands':[],'gates':{},'policy':'one full attempt plus terminal audit/comparison; no auto restart'}
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  for name in ['record_epoch16_pilot_20261024','record_epoch16_wrap_20261024','record_epoch16_stalls_20261024','record_epoch16_faults_20261024','record_epoch6_full_20261024']:
   p=ROOT/'results'/name/'manifest.json';g=json.loads(p.read_text());assert g['status']=='passed',name;m['gates'][name]=sha(p)
  p=ROOT/'results/record_epoch16_timing_20261024/final_audit.json';g=json.loads(p.read_text());assert g['status']=='evidence_verified' and g['internal_constraints_met_in_this_model'];m['physical_audit_sha256']=sha(p)
  assert not (ROOT/'results/record_epoch16_full_20261024').exists(),'Existing downstream output; inspect, never duplicate'
  names=['run_record_epoch16_full.py','audit_record_epoch16_full.py','compare_record_epoch16_queries.py'];m['frozen_scripts']={}
  for name in names:(out/name).write_bytes((ROOT/'hardware/scripts'/name).read_bytes());m['frozen_scripts'][name]=sha(out/name)
  m['status']='running_full';save()
  for name in names:
   assert sha(out/name)==m['frozen_scripts'][name]
   argv=[sys.executable,str(out/name)]
   with (out/(name+'.stdout.log')).open('w') as f:
    proc=subprocess.Popen(argv,cwd=ROOT,stdout=f,stderr=subprocess.STDOUT);row={'script':name,'argv':argv,'pid':proc.pid};m['commands'].append(row);save();row['exit_code']=proc.wait();save();assert row['exit_code']==0,name
  m['status']='full_replay_audited';save()
 except Exception as e:m.update(status='stopped_requires_inspection',error=repr(e));save();raise
if __name__=='__main__':main()
