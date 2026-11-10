"""Run bounded 4-query lifecycle contract against both directory epochs."""
from pathlib import Path
import hashlib,json,subprocess,os
from make_query_lifetime_tb import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/query_lifetime_20261024';out.mkdir()
 base=ROOT/'results/record_epoch16_pilot_20261024'
 bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 rtl=sorted(p for p in (base/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_'))
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items()}
 for p in rtl:assert sha(p)==expected[p.name]
 tb=ROOT/'hardware/tb/tb_query_lifetime.sv';assert tb.read_text()==render()
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'runner_sha256':sha(Path(__file__)),'generator_sha256':sha(ROOT/'hardware/scripts/make_query_lifetime_tb.py'),'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for bits in (6,16):
   d=out/str(bits);d.mkdir();src=d/'sources';src.mkdir()
   row={'status':'running','sources':{},'commands':[]};m['cases'][str(bits)]=row
   for p in rtl+[tb]:
    (src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in rtl+[tb]]]),('elaborate',[str(BIN/'xelab'),f'tb_query_lifetime{bits}','-s','lifetime','--debug','typical','--mt','2']),('simulate',[str(BIN/'xsim'),'lifetime','--tclbatch','run.tcl','--log','simulate.log'])]
   for stage,argv in cmds:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(bits,stage)
   log=(d/'simulate.log').read_text()
   assert 'Fatal:' not in log and '$finish' in log
   marker=f'LIFETIME_DOMAINS_PASS epoch_bits={bits} retained_query_ids=4 transfers=8 full_recycles=1 checkpoint_rejections=2 namespace_exhaustions=2 '
   assert marker in log
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(bits,'passed',flush=True)
  m['status']='passed';save()
 except Exception as e:
  m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
