from pathlib import Path
import hashlib,json,os,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';base=ROOT/'results/expansion_20261024';bm=read(base/'manifest.json');gate=read(base/'source_bound_audit.json');assert gate['status']=='passed'and gate['manifest_sha256']==sha(base/'manifest.json')
 shutil.copytree(base/'sources',src);oracle=Path(bm['oracle']);graph=Path(bm['graph'])
 m={'status':'running','pid':os.getpid(),'base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'sources':{name:spec['sha256']for name,spec in bm['sources'].items()},'new_sources':{},'groups':{},'cases':{}}
 for p in (ROOT/'hardware/variants/expansion_boundaries_v1').iterdir():
  if p.is_file():shutil.copyfile(p,src/p.name);m['new_sources'][p.name]={'path':str(p),'sha256':sha(p)}
 shutil.copyfile(__file__,src/'boundary_runner.py');m['new_sources']['boundary_runner.py']={'path':str(Path(__file__).resolve()),'sha256':sha(Path(__file__))}
 rtl=[src/n for n in bm['rtl']if not Path(n).name.startswith('tb_')]+[src/'tb_node_expansion_fault.sv']
 def save():
  q=out/'manifest.tmp';q.write_text(json.dumps(m,indent=2)+'\n');q.replace(out/'manifest.json')
 save()
 def run(stage,args,cwd,logdir,rows):
  row={'stage':stage,'argv':list(map(str,args)),'cwd':str(cwd)};rows.append(row);save();t=time.monotonic()
  with (logdir/(stage+'.stdout.log')).open('w')as f:
   p=subprocess.Popen(row['argv'],cwd=cwd,stdout=f,stderr=subprocess.STDOUT);row['pid']=p.pid;save();row['exit_code']=p.wait();row['elapsed_s']=time.monotonic()-t;save()
  assert row['exit_code']==0,(stage,logdir)
 try:
  for group,define,scenarios in [('errors',None,range(13)),('token','TOKEN_LIMIT',[13]),('owner','OWNER_LIMIT',[14])]:
   work=out/group;work.mkdir();gm=m['groups'][group]={'commands':[],'define':define};save()
   run('compile',[BIN/'xvlog','--sv']+(['--define',define]if define else [])+rtl,work,work,gm['commands'])
   run('elaborate',[BIN/'xelab','tb_node_expansion_fault','-s','boundary','--debug','typical','--mt','2'],work,work,gm['commands'])
   gm['artifacts']={p.name:sha(p)for p in work.iterdir()if p.is_file()and p.suffix=='.log'};save()
   for scenario in scenarios:
    d=out/f'case{scenario:02}';d.mkdir();cm=m['cases'][str(scenario)]={'status':'running','commands':[]};save()
    shutil.copyfile(oracle/'initial_design.bin',d/'design.bin')
    with (d/'labels.bin').open('wb')as f:f.truncate(49152)
    (d/'run.tcl').write_text('run 100ms\nquit\n')
    args=[BIN/'xsim','boundary','--tclbatch',d/'run.tcl','--log',d/'simulate.log']
    params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','scenario':scenario}
    for key,value in params.items():args+=['--testplusarg',key+'='+str(value)]
    run('simulate',args,work,d,cm['commands']);log=(d/'simulate.log').read_text();lines=[s for s in log.splitlines()if s.startswith('EXPANSION_BOUNDARY_PASS ')]
    assert len(lines)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,(scenario,log[-2500:])
    cm.update(status='passed',result=lines[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()});save();print(lines[0],flush=True)
  for name,digest in m['sources'].items():assert sha(src/name)==digest
  for name,spec in m['new_sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
  assert sha(base/'manifest.json')==m['base_manifest_sha256']and sha(base/'source_bound_audit.json')==m['base_audit_sha256']
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
