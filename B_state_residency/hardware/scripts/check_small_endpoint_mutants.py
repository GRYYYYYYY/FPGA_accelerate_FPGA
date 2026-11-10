"""Matched-debug mutations against the complete 32-slot stall regression."""
from pathlib import Path
import subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[2];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 parent=ROOT/'results/rtl_small_endpoint_stalls_20261023';pm=json.loads((parent/'manifest.json').read_text());assert pm['status']=='passed'
 out=ROOT/'results/rtl_small_endpoint_mutants_20261023';out.mkdir()
 files=[Path(n) for n in pm['sources'] if n.endswith('.sv')]
 for p in files:assert sha(p)==pm['sources'][str(p)]
 target='memory_scratch_endpoint_small.sv'
 specs=[('ignore_binding','bound_mask!=0 || ','','host'),('skip_drain','CP_DRAIN:if(cp_drained)','CP_DRAIN:if(1\'b1)','blocked prerequisite'),('skip_query_resume','else state<=CP_QUERY_SEND;','else begin fence_open<=0;rsp_valid<=1;state<=IDLE;end','host')]
 m={'status':'running','pid':os.getpid(),'parent_sha256':sha(parent/'manifest.json'),'source_hashes':{str(p):sha(p) for p in files},'mutants':[]}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  for name,old,new,expected in specs:
   d=out/name;d.mkdir()
   for p in files:
    s=p.read_text()
    if p.name==target:assert s.count(old)==1;s=s.replace(old,new)
    (d/p.name).write_text(s)
   (d/'simulate.tcl').write_text('run 2ms\nquit\n');row={'name':name,'mutation':[old,new],'commands':[]};m['mutants'].append(row);save()
   cmds=[('compile',[BIN/'xvlog','--sv',*[p.name for p in files]]),('elaborate',[BIN/'xelab','tb_small_endpoint_32slots_stalls','-s','mutant','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','mutant','--tclbatch','simulate.tcl','--log','simulate.log'])]
   for stage,args in cmds:
    with (d/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['commands'].append({'stage':stage,'exit_code':r.returncode});save()
    if stage!='simulate':assert r.returncode==0
   log=(d/'simulate.log').read_text();fatal=[s for s in log.splitlines() if 'Fatal:' in s]
   assert len(fatal)==1 and 'watchdog' not in fatal[0] and 'SMALL_32SLOTS_PASS' not in log
   row.update(status='detected',fatal=fatal[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.sv','.log','.tcl']});save();print(name,fatal[0],flush=True)
  for p,h in m['source_hashes'].items():assert sha(Path(p))==h
  m['status']='passed';save();(out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
