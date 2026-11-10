"""Frozen-source sparse WB tests, fault regression and actual-value pilot."""
from pathlib import Path
import argparse,hashlib,json,subprocess,os,re
from make_sparse_writeback import render as rtl_render
from make_sparse_writeback_tb import render as tb_render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--output',default='sparse_writeback_20261024');args=parser.parse_args()
 out=ROOT/'results'/args.output;out.mkdir()
 base=ROOT/'results/record_epoch16_pilot_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items()}
 originals=sorted(p for p in (base/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==expected[p.name]
 variant=ROOT/'hardware/variants/sparse_writeback';rtl=rtl_render();tbs=tb_render()
 for name,s in rtl.items():assert (variant/name).read_text()==s
 for name,s in tbs.items():assert (ROOT/'hardware/tb'/name).read_text()==s
 paths=[variant/p.name if p.name in rtl else p for p in originals]
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'cases':{},'scripts':{str(Path(__file__).relative_to(ROOT)):sha(Path(__file__))}}
 for name in ['make_sparse_writeback.py','make_sparse_writeback_tb.py']:
  p=ROOT/'hardware/scripts'/name;m['scripts'][str(p.relative_to(ROOT))]=sha(p)
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cases=[('masks','tb_sparse_writeback_masks.sv','tb_sparse_writeback_masks','SPARSE_WB_MASKS_PASS masks=256 transfers=512 fences=256'),('faults','tb_sparse_writeback_faults.sv','tb_response_faults','RESPONSE_FAULT_PASS errors=9'),('pilot','tb_sparse_writeback_pilot.sv','tb_sparse_writeback_checkpoint_stream_small','TEST_PASS memory_endpoint')]
  for case,tbname,top,marker in cases:
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();tb=ROOT/'hardware/tb'/tbname
   row={'status':'running','sources':{},'commands':[]};m['cases'][case]=row
   for p in paths+[tb]:(src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   sim=[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log']
   if case=='pilot':sim+=bm['cases']['pilot']['commands'][-1]['argv'][6:]
   commands=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths+[tb]]]),('elaborate',[str(BIN/'xelab'),top,'-s','sparse','--debug','typical','--mt','2']),('simulate',sim)]
   for stage,argv in commands:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert marker in log and 'Fatal:' not in log and '$finish' in log
   counts=re.search(r'SPARSE_WB_COUNTS exports=(\d+) omitted=(\d+) masks=(\d+)',log);assert counts
   row['sparse_counts']={k:int(v) for k,v in zip(['exports','omitted','masks'],counts.groups())}
   row['end_ns']=int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
   if case=='pilot':
    old=(base/'pilot/simulate.log').read_text()
    strip=lambda s:re.sub(r' ?time_ps=\d+','',s)
    for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
     assert [strip(x) for x in re.findall('^'+prefix+r' (.+)$',log,re.M)]==[strip(x) for x in re.findall('^'+prefix+r' (.+)$',old,re.M)]
    terminal=lambda x:{k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',x,re.M)[1])}
    newc,oldc=terminal(log),terminal(old);assert set(newc)==set(oldc)
    assert all(newc[k]==v for k,v in oldc.items() if k not in ('gap_cycles','host_stalls'))
    row['counts']=newc;row['baseline_end_ns']=bm['cases']['pilot']['end_ns'];row['time_reduction_fraction']=1-row['end_ns']/row['baseline_end_ns']
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',row.get('time_reduction_fraction',''),flush=True)
  m['status']='passed';save()
 except Exception as e:
  m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
