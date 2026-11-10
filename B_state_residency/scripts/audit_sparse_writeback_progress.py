"""Read-only prefix check of the original live sparse-WB full replay."""
from pathlib import Path
import hashlib,json,re,os,datetime
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 run=ROOT/'results/sparse_writeback_cycle64_full_20261024';m=json.loads((run/'manifest.json').read_text());assert m['status']=='running'
 pid=m['pid'];os.kill(pid,0)
 cmd=Path(f'/proc/{pid}/cmdline').read_bytes().replace(b'\0',b' ').decode();assert 'run_sparse_writeback_cycle64.py' in cmd and '--full' in cmd
 for name,digest in m['sources'].items():assert sha(run/'sources'/name)==digest
 step=m['commands'][-1];assert step['stage']=='simulate' and 'exit_code' not in step
 os.kill(step['pid'],0)
 old=(ROOT/m['baseline']/'pilot/simulate.log').read_text();log=(run/'simulate.log').read_text();assert 'Fatal:' not in log and 'TEST_PASS memory_endpoint' not in log
 counts={}
 for prefix,label in [('STREAM_QUERY_DONE','queries'),('STREAM_CHECKPOINT_DONE','checkpoints')]:
  # Match complete lines only, tolerating an incomplete current log suffix.
  extract=lambda t:[re.sub(r' ?time_ps=\d+','',s) for s in re.findall('^'+prefix+r' (.+)\n',t,re.M)]
  current,baseline=extract(log),extract(old);assert current==baseline[:len(current)]
  counts[label]=len(current)
 result={'status':'live_prefix_verified','runner_pid':pid,'simulator_wrapper_pid':step['pid'],'observed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'completed_prefix':counts,'compiled_sources':m['sources'],'scope':'Completed non-time receipts match native16 full prefix; no final performance or completion claim.'}
 stamp=datetime.datetime.now(datetime.timezone.utc).strftime('%Y%m%dT%H%M%SZ')
 out=ROOT/'results'/('sparse_writeback_progress_'+stamp);out.mkdir();(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':result['status'],'runner_pid':pid,'prefix':counts,'output':str(out)},indent=2))
if __name__=='__main__':main()
