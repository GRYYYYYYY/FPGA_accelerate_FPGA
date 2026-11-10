"""Freeze and verify first-touch collector/controller with actual HLS RTL and independent service vectors."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 hls=ROOT/'results/children_hls_20261024';gate=read(hls/'source_bound_audit.json');assert gate['status']=='passed' and gate['manifest_sha256']==sha(hls/'manifest.json')
 m={'status':'running','pid':os.getpid(),'sources':{},'gates':{},'commands':[],'cases':{},'scope':'Actual first-touch HLS+collector+build controller RTL. Independent original-function service-event oracle; service replies still modeled, no graph/cache/pager integration or whole-router/board claim.'}
 def save():
  t=out/'manifest.tmp';t.write_text(json.dumps(m,indent=2)+'\n');t.replace(out/'manifest.json')
 def freeze(p,name):
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][name]={'path':str(p),'sha256':sha(p)};return q
 for bits in [32,3]:
  for name,digest in gate['cases'][str(bits)]['generated_rtl_artifacts'].items():
   p=hls/f'gen{bits}/children_step/solution1/syn/verilog'/name;assert sha(p)==digest;freeze(p,f'hls{bits}/'+name)
 for p in sorted((ROOT/'hardware/variants/children_engine_v1').iterdir()):
  if p.is_file():freeze(p,'engine/'+p.name)
 for p in (hls/'rearchitect/v1/src').iterdir():
  if p.is_file():freeze(p,'oracle/'+p.name)
 for p in (hls/'rearchitect/v1/tb').iterdir():
  if p.is_file():freeze(p,'oracle/'+('original_testbench.cpp'if p.name=='testbench.cpp'else p.name))
 for p in [hls/'manifest.json',hls/'source_bound_audit.json',ROOT/'results/children_reset_20261024/source_bound_audit.json',ROOT/'results/children_hls_synthesis_20261024/final_audit.json']:
  assert read(p)['status']=='passed';m['gates'][str(p)]=sha(p)
 freeze(Path(__file__),'runner.py');save()
 def run(stage,args,d,rows):
  row={'stage':stage,'argv':list(map(str,args))};rows.append(row);save();t=time.monotonic()
  with (d/(stage+'.stdout.log')).open('w')as log:
   proc=subprocess.Popen(row['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save();row['exit_code']=proc.wait();row['elapsed_s']=time.monotonic()-t;save()
  assert row['exit_code']==0,(d,stage)
 try:
  run('oracle_build',['g++','-std=c++17','-O2','-I'+str(src/'oracle'),src/'engine/make_vectors.cpp',src/'oracle/kernel_hls.cpp','-o',out/'make_vectors'],out,m['commands'])
  run('oracle_run',[out/'make_vectors',out/'vectors.txt'],out,m['commands'])
  assert (out/'oracle_run.stdout.log').read_text()=='CHILDREN_VECTORS_PASS contexts=93728 services=813439 emissions=46896\n'
  m['oracle']={name:sha(out/name)for name in ['make_vectors','vectors.txt','oracle_run.stdout.log']};save()
  for case,define,bits in [('collector',None,32),('gen3','GEN3',3),('pilot','PILOT',32),('full',None,32)]:
   d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','define':define,'generation_bits':bits,'commands':[]};save()
   engine=src/'engine';rtl=[engine/'children_hls_call.sv']
   if case=='collector':rtl.append(engine/'tb_children_hls_call.sv');top='tb_children_hls_call'
   else:
    rtl+=sorted((src/f'hls{bits}').glob('*.v'))+[engine/'children_build_controller.sv',engine/'children_build_engine.sv',engine/'tb_children_build_engine.sv'];top='tb_children_build_engine'
   (d/'run.tcl').write_text('run 1000ms\nquit\n')
   run('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl,d,cm['commands'])
   run('elaborate',[BIN/'xelab',top,'-s','children','--debug','typical','--mt','2'],d,cm['commands'])
   run('simulate',[BIN/'xsim','children','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','fixture='+str(out/'vectors.txt')],d,cm['commands'])
   log=(d/'simulate.log').read_text();marker='CHILDREN_CALL_PASS 'if case=='collector'else'CHILDREN_ENGINE_GEN3_PASS 'if case=='gen3'else'CHILDREN_ENGINE_PASS '
   hits=[s for s in log.splitlines()if s.startswith(marker)];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,(case,log[-1800:])
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in('.log','.tcl')});save();print(case,hits[0],flush=True)
  for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
  for p,digest in m['gates'].items():assert sha(Path(p))==digest
  m['status']='passed';save()
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
