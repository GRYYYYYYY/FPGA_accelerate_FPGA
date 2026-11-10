"""Independent empty-response-FIFO bypass ablation; frozen default stays intact."""
from pathlib import Path
import hashlib,json,subprocess,re,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_response_full_20261024';out.mkdir();variant=ROOT/'hardware/variants/record_response_fallthrough'
 m={'status':'running','pid':os.getpid(),'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  base=ROOT/'results/rtl_small_checkpoint_stream_full_20261023';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
  assert sha(base/'manifest.json')==json.loads((base/'completion_audit.json').read_text())['manifest_sha256']
  m['gates']={}
  for name in ['record_response_fallthrough_20261024','record_response_faults_20261024','response_fallthrough_faults_control_v2_20261024','record_response_gate_20261024']:
   path=ROOT/'results'/name/'manifest.json';gate=json.loads(path.read_text());assert gate['status']=='passed',name
   m['gates'][name]=sha(path)
  frozen=out/Path(__file__).name;frozen.write_bytes(Path(__file__).read_bytes());m['runner_sha256']=sha(frozen);save()

  baseline=[Path(x) for x in bm['commands'][0]['argv'] if x.endswith('.sv')]
  rtl=[p for p in baseline if not p.name.startswith('tb_')]
  for p in rtl:assert sha(p)==next(h for n,h in bm['sources'].items() if Path(n).name==p.name)
  for case,tb,top in [('fifo',ROOT/'hardware/tb/tb_record_response_fallthrough_fifo.sv','tb_record_response_fallthrough_fifo'),('multipage',ROOT/'hardware/tb/tb_small_endpoint_multipage.sv','tb_small_endpoint_multipage'),('stalls',ROOT/'hardware/tb/tb_small_endpoint_32slots_stalls.sv','tb_small_endpoint_32slots_stalls'),('pilot',next(p for p in baseline if p.name.startswith('tb_')),next(p for p in baseline if p.name.startswith('tb_')).stem)]:
   if case!='pilot':continue
   if case=='pilot':top=next(step['argv'][1] for step in bm['commands'] if step['stage']=='elaborate')
   d=out/case;d.mkdir();src=d/'sources';src.mkdir()
   paths=([p if p.name!='queued_scratch_endpoint_small.sv' else variant/p.name for p in rtl] if case!='fifo' else [])+[variant/'response_fallthrough_fifo.sv',tb]
   row={'status':'running','commands':[],'sources':{},'baseline_sha256':sha(base/'manifest.json')};m['cases'][case]=row
   for p in paths:(src/p.name).write_bytes(p.read_bytes());row['sources'][str(p)]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   args=[str(BIN/'xsim'),'ablation','--tclbatch','run.tcl','--log','simulate.log']
   if case=='pilot':args+=next(s['argv'][6:] for s in bm['commands'] if s['stage']=='simulate')
   commands=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','ablation','--debug','typical','--mt','2']),('simulate',args)]
   for stage,argv in commands:
    with (d/(stage+'.stdout.log')).open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
   if case=='fifo':assert 'RESPONSE_FIFO_PASS depths=1,3,4' in log
   elif case=='multipage':assert 'SMALL_MULTIPAGE_PASS pages=4 fields=5 checkpoints=8 transfers=36 checks=221 tag_wraps=4' in log
   elif case=='stalls':
    assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log
    assert 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
   else:
    # Changed latency shifts periodic backpressure. Compare semantic receipts,
    # retaining every non-time field and all functional terminal counters.
    for prefix,key in [('STREAM_QUERY_DONE','query_receipts'),('STREAM_CHECKPOINT_DONE','checkpoint_receipts')]:
     strip=lambda s:re.sub(r' ?time_ps=\d+','',s)
     assert [strip(x) for x in re.findall('^'+prefix+r' (.+)$',log,re.M)]==[strip(x) for x in bm[key]]
    counts={k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',log,re.M)[1])}
    assert set(counts)==set(bm['counts'])
    assert all(counts[k]==v for k,v in bm['counts'].items() if k not in ('gap_cycles','host_stalls'))
    row['counts']=counts;row['baseline_end_ns']=bm['end_ns'];row['end_ns']=int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
