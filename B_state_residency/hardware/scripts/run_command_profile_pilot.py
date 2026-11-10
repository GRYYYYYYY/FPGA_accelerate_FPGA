"""Replay frozen pilots with passive observers and exact receipt equivalence."""
from pathlib import Path
import json,hashlib,subprocess,re
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 prepared=ROOT/'results/command_profile_observers_20261024';spec=json.loads((prepared/'manifest.json').read_text())
 out=ROOT/'results/command_profile_pilot_20261024';out.mkdir()
 m={'status':'running','cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for label,base in [('small','rtl_small_checkpoint_stream_pilot_v3_20261023')]:
   bp=ROOT/'results'/base; bm=json.loads((bp/'manifest.json').read_text());assert bm['status']=='passed'
   assert sha(bp/'manifest.json')==json.loads((bp/'completion_audit.json').read_text())['manifest_sha256']
   d=out/label;d.mkdir();(d/'sources').mkdir();s=spec['sources'][label];tb=prepared/s['output'];assert sha(tb)==s['output_sha256']
   orig=Path(s['input']).stem;new=tb.stem
   row={'status':'running','baseline_sha256':sha(bp/'manifest.json'),'observer_sha256':sha(tb),'commands':[]};m['cases'][label]=row;save()
   (d/'run.tcl').write_bytes((bp/'run.tcl').read_bytes())
   for step in bm['commands']:
    args=[]
    for arg in step['argv']:
     p=Path(arg)
     if p.suffix=='.sv':
      if p.stem==orig:src=tb
      else:
       src=p;matches=[h for name,h in bm['sources'].items() if Path(name).name==p.name];assert len(matches)==1 and sha(src)==matches[0]
      target=d/'sources'/src.name;target.write_bytes(src.read_bytes());args.append(str(target))
     else:args.append(arg.replace(orig,new))
    with (d/(step['stage']+'.stdout.log')).open('w') as f:
     proc=subprocess.Popen(args,cwd=d,stdout=f,stderr=subprocess.STDOUT);r={'stage':step['stage'],'pid':proc.pid,'argv':args};row['commands'].append(r);save();r['exit_code']=proc.wait();save();assert r['exit_code']==0
   log=(d/'simulate.log').read_text();assert 'Fatal:' not in log
   for prefix,key in [('STREAM_QUERY_DONE','query_receipts'),('STREAM_CHECKPOINT_DONE','checkpoint_receipts')]:assert re.findall('^'+prefix+r' (.+)$',log,re.M)==bm[key]
   assert int(re.search(r'\$finish called at time : (\d+) ns',log)[1])==bm['end_ns']
   counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])};assert counts==bm['counts']
   obs=re.findall(r'^INIT_DIRECTORY_READY (.+)$',log,re.M);assert len(obs)==1
   row.update(status='passed',observer=obs[0],end_ns=bm['end_ns'],log_sha256=sha(d/'simulate.log'));save()
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
