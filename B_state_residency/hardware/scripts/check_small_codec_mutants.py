"""Negative RTL experiments; never modify baseline RTL or testbench."""
from pathlib import Path
import subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/rtl_small_codec_mutants_20261023';out.mkdir()
 rtl=ROOT/'hardware/rtl/scratch_page_codec_small.sv';tb=ROOT/'hardware/tb/tb_scratch_page_codec_small_edges.sv'
 specs=[('ignore_commit','bad || !commit_ok','bad','decoded record'),('ignore_tail',' || page[1535:1288]!=0','','invalid record'),('ignore_cancel','else if(cancel && state!=IDLE)','else if(1\'b0)','watchdog')]
 m={'status':'running','pid':os.getpid(),'source_hashes':{str(p):sha(p) for p in [rtl,tb,Path(__file__)]},'mutants':[]}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  for name,old,new,_ in specs:
   d=out/name;d.mkdir();s=rtl.read_text();assert s.count(old)==1;s=s.replace(old,new)
   (d/rtl.name).write_text(s);(d/tb.name).write_bytes(tb.read_bytes());(d/'simulate.tcl').write_text('run 2ms\nquit\n')
   row={'name':name,'replacement':[old,new],'commands':[]};m['mutants'].append(row);save()
   cmds=[('compile',[BIN/'xvlog','--sv',rtl.name,tb.name]),('elaborate',[BIN/'xelab','tb_scratch_page_codec_small_edges','-s','mutant','--mt','2']),('simulate',[BIN/'xsim','mutant','--tclbatch','simulate.tcl','--log','simulate.log'])]
   for stage,cmd in cmds:
    with (d/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(list(map(str,cmd)),cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['commands'].append({'stage':stage,'exit_code':r.returncode});save()
    if stage!='simulate':assert r.returncode==0
   log=(d/'simulate.log').read_text();fatals=[s for s in log.splitlines() if 'Fatal:' in s]
   assert fatals and 'SMALL_CODEC_EDGES_PASS' not in log
   row.update(status='detected',fatal=fatals[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.sv','.log','.tcl']});save();print(name,fatals[0],flush=True)
  for p,h in m['source_hashes'].items():assert sha(Path(p))==h
  m['status']='passed';save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
