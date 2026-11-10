"""Isolated 64-bit backing-base configuration and full endpoint integration."""
from pathlib import Path
import json,hashlib,os,subprocess
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/address64_endpoint_v2_20261024';out.mkdir();m={'status':'running','pid':os.getpid(),'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  parent=ROOT/'results/record_epoch6_pilot_20261024';pm=json.loads((parent/'manifest.json').read_text());assert pm['status']=='passed'
  frozen=parent/'pilot/sources';rtl=[p for p in frozen.glob('*.sv') if not p.name.startswith('tb_')]
  for p in rtl:assert sha(p)==next(h for n,h in pm['cases']['pilot']['sources'].items() if Path(n).name==p.name)
  variant=ROOT/'hardware/variants/address64';base=variant/'backing_base_config.sv';wrapper=variant/'memory_scratch_endpoint_address64.sv'
  for case,tb,paths,top,markers in [('config',ROOT/'hardware/tb/tb_backing_base_config.sv',[base],'tb_backing_base_config',['BASE_CONFIG_PASS cases=4 invalid_alignment=1 overflow=1 high_address=1 exact_end=1 locked=1 reset=1']),('endpoint',ROOT/'hardware/tb/tb_address64_endpoint.sv',rtl+[base,wrapper],'tb_address64_endpoint',['ADDRESS64_ENDPOINT_PASS base=0000001234567000','SMALL_STALLS_PASS cases=8 blocked_cycles=800','SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4'])]:
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();paths=paths+[tb]
   row={'status':'running','sources':{},'commands':[],'parent_sha256':sha(parent/'manifest.json')};m['cases'][case]=row
   for p in paths:(src/p.name).write_bytes(p.read_bytes());row['sources'][str(p)]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   commands=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','address64','--debug','typical','--mt','2']),('simulate',[str(BIN/'xsim'),'address64','--tclbatch','run.tcl','--log','simulate.log'])]
   for stage,argv in commands:
    with (d/(stage+'.stdout.log')).open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish' in log
   assert all(marker in log for marker in markers),case
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
