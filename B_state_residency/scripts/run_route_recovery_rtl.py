from pathlib import Path
import json,hashlib,shutil,subprocess,time,sys,struct,mmap
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/route_join_rtl_v1';bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed';inp=Path(bm['input']);graph=ROOT/'results/graph_image_20261024'
 m=dict(status='running',sources={},cases={},commands=[],input=str(inp),base_audit_sha256=sha(base/'source_bound_audit.json'),scope='Actual pager/owner AXI faults from imported real q1 final labels; same-instance cold reset after drain, journal GET/DEC authority repair, new epoch label reload and route recommit; TB coordinator, no search rerun.')
 rtl=[]
 for name in bm['rtl']:
  if Path(name).name.startswith('tb_'):continue
  p=src/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile((ROOT/'hardware/variants/route_commit_join_drain_v2/route_commit_host_adapter.sv')if Path(name).name=='route_commit_host_adapter.sv'else(base/'sources'/name),p);assert Path(name).name=='route_commit_host_adapter.sv'or sha(p)==bm['sources'][name]['sha256'];m['sources'][name]=sha(p);rtl.append(p)
 for p,name in [(ROOT/'hardware/variants/route_recovery_v1/tb_route_recovery.sv','tb_route_recovery.sv'),(Path(__file__),'runner.py')]:shutil.copyfile(p,src/name);m['sources'][name]=sha(src/name)
 shutil.copyfile(ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv',src/'axi_drain_watch.sv');m['sources']['axi_drain_watch.sv']=sha(src/'axi_drain_watch.sv');rtl.append(src/'axi_drain_watch.sv')
 rtl.append(src/'tb_route_recovery.sv')
 for name in bm['sources']:
  if name.endswith('.dat'):
   p=src/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/name,p);m['sources'][name]=sha(p)
 # Reuse real query1 search-final native values over the already audited union.
 ids=[int(l.split()[0])for l in(base/'imports.txt').read_text().splitlines()];cpu=ROOT/'results/natural_query_v2';m['capture_audit_sha256']=sha(cpu/'source_bound_audit.json')
 with(cpu/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as snap:
  (out/'imports.txt').write_text(''.join(str(i)+' '+' '.join(f'{v:08x}'for v in (lambda a:[a[0],a[1],a[3],a[4],a[5]])(struct.unpack_from('<11I',snap,i*44)))+'\n'for i in ids))
 m['imports_sha256']=sha(out/'imports.txt')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def run(stage,argv,d,record):
  argv=list(map(str,argv));t=time.monotonic()
  with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=300)
  record.append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,(d,stage)
 save()
 try:
  for mode,define in [('full',None),('pressure','PRESSURE')]:
   build=out/(mode+'_build');build.mkdir()
   for p in src.rglob('*.dat'):shutil.copyfile(p,build/p.name)
   run(mode+'_compile',[BIN/'xvlog','--sv']+(['--define',define]if define else[])+rtl,build,m['commands']);run(mode+'_elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2'],build,m['commands'])
   (build/'run.tcl').write_text('run 30ms\nquit\n')
   for case in range(1,6):
    d=out/(mode+'_'+str(case));d.mkdir();rec=m['cases'][d.name]=dict(status='running',commands=[],fault_case=case,capacity=mode);save()
    for n in ['design.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
    (d/'owners.bin').write_bytes((inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes())
    with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
    params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':inp/'rows.bin','tables1':inp/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','cost0':d/'cost.bin','costlog':d/'cost_axi.txt','qstate0':inp/'connections.bin','qstatelog':d/'qstate_axi.txt','costvectors':inp/'cost_vectors.txt','finallabels':base/'finals.txt','imports':out/'imports.txt','candidates':base/'candidates.txt','polls':base/'polls.txt','faultcase':case}
    argv=[BIN/'xsim','joined','--tclbatch','run.tcl','--log',d/'simulate.log']
    for k,v in params.items():argv+=['--testplusarg',str(k)+'='+str(v)]
    run('simulate',argv,build,rec['commands']);shutil.copyfile(build/'natural_trace.txt',d/'natural_trace.txt');shutil.copyfile(build/'simulate.stdout.log',d/'simulate.stdout.log')
    log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('ROUTE_RECOVERY_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log
    rec.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()});save();print(d.name,hits[0],flush=True)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
