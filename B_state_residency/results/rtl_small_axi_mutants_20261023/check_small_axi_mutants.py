"""Negative RTL experiments; never modify baseline RTL or testbench."""
from pathlib import Path
import subprocess,json,hashlib,os
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/rtl_small_axi_mutants_20261023';out.mkdir()
 rtl=ROOT/'hardware/rtl/scratch_page_axi_small.sv';tb=ROOT/'hardware/tb/tb_small_codec_axi.sv';codec=ROOT/'hardware/rtl/scratch_page_codec_small.sv';parent=ROOT/'results/rtl_small_codec_axi_20261023'
 assert json.loads((parent/'manifest.json').read_text())['status']=='passed'
 specs=[('truncate_cookie','done_cookie<=req_cookie','done_cookie<={8\'b0,req_cookie[63:0]}','cookie'),('cross_4KiB','(room<remaining)?room[5:0]:remaining','remaining','burst'),('skip_error_drain',"else begin position<=position+1'b1;state<=READ_DRAIN;end","else begin state<=IDLE;done_valid<=1;end",'undrained')]

 m={'status':'running','pid':os.getpid(),'source_hashes':{str(p):sha(p) for p in [rtl,tb,codec,Path(__file__),parent/'pages.hex',parent/'records.hex']},'mutants':[]}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 def save():
  p=out/'manifest.tmp';p.write_text(json.dumps(m,indent=2)+'\n');p.replace(out/'manifest.json')
 save()
 try:
  for name,old,new,_ in specs:
   d=out/name;d.mkdir();s=rtl.read_text();assert s.count(old)==1;s=s.replace(old,new)
   (d/codec.name).write_bytes(codec.read_bytes());(d/rtl.name).write_text(s);(d/tb.name).write_bytes(tb.read_bytes());(d/'simulate.tcl').write_text('run 2ms\nquit\n')
   row={'name':name,'replacement':[old,new],'commands':[]};m['mutants'].append(row);save()
   cmds=[('compile',[BIN/'xvlog','--sv',rtl.name,codec.name,tb.name]),('elaborate',[BIN/'xelab','tb_small_codec_axi','-s','mutant','--mt','2']),('simulate',[BIN/'xsim','mutant','--tclbatch','simulate.tcl','--log','simulate.log','--testplusarg','PAGES='+str(parent/'pages.hex'),'--testplusarg','RECORDS='+str(parent/'records.hex')])]
   for stage,cmd in cmds:
    with (d/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(list(map(str,cmd)),cwd=d,stdout=f,stderr=subprocess.STDOUT)
    row['commands'].append({'stage':stage,'exit_code':r.returncode});save()
    if stage!='simulate':assert r.returncode==0
   log=(d/'simulate.log').read_text();fatals=[s for s in log.splitlines() if 'Fatal:' in s]
   assert fatals and 'SMALL_CODEC_AXI_PASS' not in log
   row.update(status='detected',fatal=fatals[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.sv','.log','.tcl']});save();print(name,fatals[0],flush=True)
  for p,h in m['source_hashes'].items():assert sha(Path(p))==h
  m['status']='passed';save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
