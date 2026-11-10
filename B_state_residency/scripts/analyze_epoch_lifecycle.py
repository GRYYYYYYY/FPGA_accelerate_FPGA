"""Census real attempts; model directory clears under explicit per-attempt recycle."""
from pathlib import Path
from collections import Counter
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/epoch_lifecycle_20261024';out.mkdir()
 src=ROOT/'results/real_trace_20261022T165136Z';audit=json.loads((src/'completion_audit.json').read_text());assert audit['status']=='passed'
 analysis_path=src/'trace_analysis.json';assert sha(analysis_path)==audit['file_hashes_at_completion'][str(analysis_path)]
 prior=json.loads(analysis_path.read_text());raw=src/'trace_0.jsonl';digest=hashlib.sha256();iterations=Counter();connections=set();nets=set();runs=Counter();last=None;run_length=0;groups=0;count=accesses=routed=aborted=0
 with raw.open('rb') as f:
  for line in f:
   digest.update(line);row=json.loads(line);assert row['record']=='attempt'
   count+=1;assert row['attempt']==count
   iterations[row['iteration']]+=1;connections.add(row['connection_index']);nets.add(row['net_index']);accesses+=row['label_accesses'];routed+=row['routed'];aborted+=row['aborted']
   key=(row['iteration'],row['net_index'])
   if key!=last:
    if run_length:runs[run_length]+=1
    groups+=1;run_length=0;last=key
   run_length+=1
 if run_length:runs[run_length]+=1
 assert digest.hexdigest()==audit['file_hashes_at_completion'][str(raw)]
 assert count==prior['counts']['attempts'] and accesses==prior['all_attempt_label_accesses']
 assert {str(k):v for k,v in sorted(iterations.items())}==prior['iterations']
 assert count==570286 and len(connections)==180326 and aborted==0 and routed==count
 directory=ROOT/'hardware/rtl/backing_frame_directory_small.sv';text=directory.read_text();assert 'if(&epoch)' in text and 'epoch<=1;clear_index<=0;clear_response<=1' in text
 oracle=ROOT/'hardware/scripts/make_small_checkpoint_vectors.py';assert 'o.emit(FENCE,expect=OK);o.emit(FINISH,peer=1,empty=1,expect=OK)' in oracle.read_text()
 wrap=ROOT/'results/rtl_small_directory_capacity_epoch6_20261023/final_audit.json';wa=json.loads(wrap.read_text());assert wa['status']=='passed' and wa['observed_clear_cycles']==786432 and wa['clear_passes_including_reset']==3
 slots=1<<18;rows=[]
 for label,n in [('selected_38',38),('first_iteration',iterations[1]),('all_recorded_attempts',count)]:
  for bits in [6,8,12,16,20,32]:
   period=(1<<bits)-1;wraps=n//period
   rows.append({'scenario':label,'recycles_assumed':n,'epoch_bits':bits,'period':period,'wraps':wraps,'wrap_clear_cycles':wraps*slots,'wrap_clear_model_ms_at_10ns':wraps*slots/100000,'clear_cycles_including_one_cold_start':(1+wraps)*slots,'index_payload_bytes':slots*(18+bits)//8})
 result={'status':'real_census_plus_conditional_model','census':{'attempts':count,'unique_connections':len(connections),'unique_nets':len(nets),'iterations':dict(sorted(iterations.items())),'label_accesses':accesses,'routed':routed,'aborted':aborted,'contiguous_iteration_net_groups':groups,'contiguous_run_length_histogram':dict(sorted(runs.items()))},'rows':rows,'assumption':'One successful full directory recycle per recorded routing attempt, one continuously running instance; mirrors existing oracle per-query FINISH policy. No complete FPGA routing run was executed.','limitations':['CLEAR_INDEX work only; excludes drain, fence, routing, host and other service costs.','Do not compare model milliseconds to CPU routing time as a speedup.','Net grouping is census only, not a valid implemented shared-distance lifecycle.','Wider epoch resource figures need synthesis; payload bytes are not BRAM counts.'],'sources':{str(p):sha(p) for p in [src/'completion_audit.json',analysis_path,directory,oracle,wrap,Path(__file__).resolve()]},'trace_sha256':digest.hexdigest()}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 print('census',count,'unique_connections',len(connections),'net_groups',groups)
 for r in rows:
  if r['scenario']=='all_recorded_attempts':print(r)
if __name__=='__main__':main()
