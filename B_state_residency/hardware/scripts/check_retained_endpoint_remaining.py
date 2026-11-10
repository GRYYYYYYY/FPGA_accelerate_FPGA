"""Isolated checkpoint coordinator mutations, all with the frozen pilot checker."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[2];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir()
 parent=ROOT/'results/rtl_retained_endpoint_pilot_20261023';src=parent/'sources';pm=json.loads((parent/'manifest.json').read_text())
 assert sha(parent/'manifest.json')=='e6c446cd38f6fdaf9e9385bddabfaa55aee7e2ad9555b6e9a02934c7c95ab0fe'
 for path,digest in pm['sources'].items():assert sha(src/Path(path).name)==digest
 original=(src/'memory_scratch_endpoint_retained.sv').read_text()
 variants={
  'ignore_live_slots':('bound_mask!=0 || page_leases!=0','page_leases!=0','host mismatch'),
  'skip_query_resume':('else state<=CP_QUERY_SEND;','else begin fence_open<=0;rsp_valid<=1;state<=IDLE;end','host mismatch'),
  'clear_backing_directory':("state==CP_MEMORY_SEND?3'd5:","state==CP_MEMORY_SEND?3'd3:",'checkpoint result'),
  'ignore_query_exclusivity':('!query_seen || !query_exclusive','!query_seen','host mismatch'),
 }
 variants={'ignore_query_exclusivity':variants['ignore_query_exclusivity']}
 m={'status':'running','parent_manifest_sha256':sha(parent/'manifest.json'),'source_sha256':sha(Path(__file__)),'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for name,(before,after,expected) in variants.items():
   assert original.count(before)==1
   d=out/name;d.mkdir();(d/'mutated.sv').write_text(original.replace(before,after));(d/'run.tcl').write_text('run 2s\nquit\n')
   row={'status':'running','before':before,'after':after,'commands':[]};m['cases'][name]=row;save()
   rtl=[p for p in src.glob('*.sv') if p.name!='memory_scratch_endpoint_retained.sv']+[d/'mutated.sv']
   commands=[('compile',[BIN/'xvlog','--sv',*rtl]),('elaborate',[BIN/'xelab','tb_retained_endpoint','-s','negative_tb','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','negative_tb','--tclbatch','run.tcl','--log','simulate.log'])]
   for stage,cmd in commands:
    args=list(map(str,cmd))
    with (d/(stage+'.stdout.log')).open('w') as log:
     proc=subprocess.Popen(args,cwd=d,stdout=log,stderr=subprocess.STDOUT);receipt={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};row['commands'].append(receipt);save();receipt['exit_code']=proc.wait();save()
    assert stage=='simulate' or receipt['exit_code']==0
   text=(d/'simulate.log').read_text();fatal=[l for l in text.splitlines() if l.startswith('Fatal:')]
   assert fatal and expected in fatal[0] and 'RETAINED_ENDPOINT_PASS' not in text,(name,text[-1000:])
   row.update(status='detected',first_failure=fatal[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save();print(name,fatal[0],flush=True)
  m['status']='passed';save();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
