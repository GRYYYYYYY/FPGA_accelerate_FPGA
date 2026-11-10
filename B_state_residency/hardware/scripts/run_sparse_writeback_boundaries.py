"""Run standalone adversarial mask/COMPLETE contract and composed stalls."""
from pathlib import Path
import hashlib,json,subprocess,os
from make_sparse_writeback_tb import adapt
from make_sparse_writeback import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/sparse_writeback_boundaries_20261024';out.mkdir()
 base=ROOT/'results/record_epoch16_pilot_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 expected={Path(k).name:v for k,v in bm['cases']['pilot']['sources'].items()}
 rtl=sorted(p for p in (base/'pilot/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in rtl:assert sha(p)==expected[p.name]
 variants=render()
 for name,s in variants.items():assert (ROOT/'hardware/variants/sparse_writeback'/name).read_text()==s
 paths=[ROOT/'hardware/variants/sparse_writeback'/p.name if p.name in variants else p for p in rtl]
 stalls=(ROOT/'hardware/tb/tb_record_epoch16_stalls.sv').read_text().replace('tb_record_epoch16_stalls','tb_sparse_writeback_stalls')
 generated=adapt(stalls)
 tbout=out/'tb_sparse_writeback_stalls.sv';tbout.write_text(generated)
 m={'status':'running','pid':os.getpid(),'baseline_manifest_sha256':sha(base/'manifest.json'),'cases':{},'scripts':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'hardware/scripts/make_sparse_writeback.py',ROOT/'hardware/scripts/make_sparse_writeback_tb.py']},'stalls_original_sha256':sha(ROOT/'hardware/tb/tb_record_epoch16_stalls.sv')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for case,tb,top,marker in [('controller',ROOT/'hardware/tb/tb_sparse_writeback_boundaries.sv','tb_sparse_writeback_boundaries','SPARSE_WB_BOUNDARIES_PASS checks=22'),('stalls',tbout,'tb_sparse_writeback_stalls','SMALL_STALLS_PASS cases=8 blocked_cycles=800')]:
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();row={'status':'running','commands':[],'sources':{}};m['cases'][case]=row
   for p in paths+[tb]:(src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths+[tb]]]),('elaborate',[str(BIN/'xelab'),top,'-s','sparse','--debug','typical','--mt','2']),('simulate',[str(BIN/'xsim'),'sparse','--tclbatch','run.tcl','--log','simulate.log'])]
   for stage,argv in cmds:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert marker in log and 'Fatal:' not in log and '$finish' in log
   if case=='stalls':assert 'SMALL_32SLOTS_PASS pages=32 fields=5 checkpoints=8 transfers=288 checks=1778 tag_wraps=4' in log
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
