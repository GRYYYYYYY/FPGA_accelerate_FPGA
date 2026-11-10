"""Sparse WB+RF correctness and paired actual-value RF incremental ablation."""
from pathlib import Path
import hashlib,json,subprocess,os,re
from make_sparse_records import render as rtl_render
from make_sparse_records_tb import render as tb_render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/sparse_records_20261024';out.mkdir()
 base=ROOT/'results/sparse_writeback_retry_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 gate=base/'source_bound_audit.json';assert json.loads(gate.read_text())['status']=='passed'
 originals=sorted(p for p in (base/'candidate/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==bm['cases']['candidate']['sources'][p.name]
 variant=ROOT/'hardware/variants/sparse_records';rtl=rtl_render();tbs=tb_render()
 for name,s in rtl.items():assert (variant/name).read_text()==s
 for name,s in tbs.items():assert (ROOT/'hardware/tb'/name).read_text()==s
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'baseline_audit_sha256':sha(gate),'cases':{},'scripts':{}}
 for name in ['run_sparse_records.py','make_sparse_records.py','make_sparse_records_tb.py']:
  p=ROOT/'hardware/scripts'/name;m['scripts'][str(p.relative_to(ROOT))]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cases=[('masks','tb_sparse_records_masks.sv','tb_sparse_records_masks','SPARSE_RECORD_MASKS_PASS masks=256 transfers=512 fences=256'),('faults','tb_sparse_records_faults.sv','tb_sparse_records_faults','RESPONSE_FAULT_PASS errors=9 transfers=68 checks=267'),('stalls','tb_sparse_records_stalls.sv','tb_sparse_records_stalls','SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4'),('control','tb_sparse_records_pilot.sv','tb_sparse_records_control','TEST_PASS memory_endpoint'),('candidate','tb_sparse_records_pilot.sv','tb_sparse_records_small','TEST_PASS memory_endpoint')]
  for case,tbname,top,marker in cases:
   paths=([variant/p.name if p.name in rtl else p for p in originals] if case!='control' else originals)+[ROOT/'hardware/tb'/tbname]
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();row={'status':'running','sources':{},'commands':[]};m['cases'][case]=row
   for p in paths:(src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   sim=[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log']
   if case in ('control','candidate'):sim+=bm['cases']['candidate']['commands'][-1]['argv'][6:]
   cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','sparse','--debug','typical','--mt','2']),('simulate',sim)]
   for stage,argv in cmds:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert marker in log and 'Fatal:' not in log and '$finish' in log
   for direction,fields in [('WB',['exports','omitted','masks']),('RF',['beats','omitted','masks'])]:
    pattern=r'SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields)
    match=re.search(pattern,log);assert match;row[direction.lower()+'_counts']={k:int(v) for k,v in zip(fields,match.groups())}
   row['end_ns']=int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
   if case in ('control','candidate'):
    old=(base/'candidate/simulate.log').read_text()
    strip=lambda t,p:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+p+r' (.+)$',t,re.M)]
    for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:assert strip(log,prefix)==strip(old,prefix)
    term=lambda t:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
    counts,oldcounts=term(log),term(old);retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
    assert counts.keys()==oldcounts.keys() and counts['checks']==75194+retries
    assert all(counts[k]==v for k,v in oldcounts.items() if k not in ('checks','gap_cycles','host_stalls'))
    row.update(counts=counts,finish_retries=retries)
    if case=='control':
     assert row['end_ns']==bm['cases']['candidate']['end_ns']
     for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS','SPARSE_WB_COUNTS']:
      assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',old,re.M)
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',row['end_ns'],flush=True)
  m['incremental_time_reduction_fraction']=1-m['cases']['candidate']['end_ns']/m['cases']['control']['end_ns']
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
