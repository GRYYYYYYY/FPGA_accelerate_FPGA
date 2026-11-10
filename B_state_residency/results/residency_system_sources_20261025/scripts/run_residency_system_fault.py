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
 m=dict(status='running',sources={},cases={},commands=[],input=str(inp),base_audit_sha256=sha(base/'source_bound_audit.json'),scope='Actual pager/owner AXI faults from imported real q1 final labels; same-instance cold reset after drain, journal GET/DEC authority repair, new epoch label reload and route recommit; synthesizable journal/reset/two-pass owner coordinator with real services; Hardware OPEN/probe/stream write/CHECKPOINT/readback labels callback, Buffered normal/admin/route ownership and parallel recovery callback fabric, seven AXI drain observers; Hardware resident descriptor and six-lane configuration; CPU authority; no search rerun.')
 rtl=[]
 for name in bm['rtl']:
  if Path(name).name.startswith('tb_'):continue
  p=src/name;p.parent.mkdir(parents=True,exist_ok=True);replacement=ROOT/'hardware/variants/transaction_fence_join_v1/backend'/Path(name).name;shutil.copyfile(replacement if replacement.exists()else(ROOT/'hardware/variants/recovery_join_v1/route_commit_host_adapter.sv')if Path(name).name=='route_commit_host_adapter.sv'else(base/'sources'/name),p);assert replacement.exists()or Path(name).name=='route_commit_host_adapter.sv'or sha(p)==bm['sources'][name]['sha256'];m['sources'][name]=sha(p);rtl.append(p)
 for p,name in [(ROOT/'hardware/variants/residency_system_v1/tb_system_fault.sv','tb_system_fault.sv'),(Path(__file__),'runner.py')]:shutil.copyfile(p,src/name);m['sources'][name]=sha(src/name)
 shutil.copyfile(ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv',src/'axi_drain_watch.sv');m['sources']['axi_drain_watch.sv']=sha(src/'axi_drain_watch.sv');rtl.append(src/'axi_drain_watch.sv')
 shutil.copyfile(ROOT/'hardware/variants/recovery_coordinator_v1/recovery_coordinator.sv',src/'recovery_coordinator.sv');m['sources']['recovery_coordinator.sv']=sha(src/'recovery_coordinator.sv');rtl.append(src/'recovery_coordinator.sv')
 shutil.copyfile(ROOT/'hardware/variants/label_restore_v1/label_restore_controller.sv',src/'label_restore_controller.sv');m['sources']['label_restore_controller.sv']=sha(src/'label_restore_controller.sv');rtl.append(src/'label_restore_controller.sv')
 shutil.copyfile(ROOT/'hardware/variants/config_restore_v1/config_restore_controller.sv',src/'config_restore_controller.sv');m['sources']['config_restore_controller.sv']=sha(src/'config_restore_controller.sv');rtl.append(src/'config_restore_controller.sv')
 shutil.copyfile(ROOT/'hardware/variants/transaction_fence_static_v2/transaction_fence.sv',src/'transaction_fence.sv');m['sources']['transaction_fence.sv']=sha(src/'transaction_fence.sv');rtl.append(src/'transaction_fence.sv')
 shutil.copyfile(ROOT/'hardware/variants/residency_system_v1/residency_system.sv',src/'residency_system.sv');m['sources']['residency_system.sv']=sha(src/'residency_system.sv');rtl.append(src/'residency_system.sv')
 rtl.append(src/'tb_system_fault.sv')
 for name in bm['sources']:
  if name.endswith('.dat'):
   p=src/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/name,p);m['sources'][name]=sha(p)
 # Reuse real query1 search-final native values over the already audited union.
 ids=[int(l.split()[0])for l in(base/'imports.txt').read_text().splitlines()];cpu=ROOT/'results/natural_query_v2';m['capture_audit_sha256']=sha(cpu/'source_bound_audit.json')
 with(cpu/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as snap:
  (out/'imports.txt').write_text(''.join(str(i)+' '+' '.join(f'{v:08x}'for v in (lambda a:[a[0],a[1],a[3],a[4],a[5]])(struct.unpack_from('<11I',snap,i*44)))+'\n'for i in ids))
 # CPU-derived authority for six real internal nodes at checkpoints 17 and 18.
 q2=ROOT/'results/followup_q2_v1';authority=[]
 with(cpu/'search_final_nodes.u32').open('rb')as f,(cpu/'initial_nodes.u32').open('rb')as g,(q2/'initial_nodes.u32').open('rb')as h,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as final,mmap.mmap(g.fileno(),0,access=mmap.ACCESS_READ)as before,mmap.mmap(h.fileno(),0,access=mmap.ACCESS_READ)as after:
  node=struct.unpack_from('<I',final,150697*44+12)[0]
  while node!=65185:
   a=struct.unpack_from('<11I',before,node*44);b=struct.unpack_from('<11I',after,node*44)
   authority.append(f'{node} 2717 {a[7]if a[6]==2717 else 0} {a[8]} {b[7]if b[6]==2717 else 0} {b[8]}\n');node=struct.unpack_from('<I',final,node*44+12)[0]
 assert len(authority)==6;(out/'authority.txt').write_text(''.join(authority));m['authority_sha256']=sha(out/'authority.txt');m['authority_after_audit_sha256']=sha(q2/'source_bound_audit.json')
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
    params={'graph0':graph/'offsets.u32le','graph1':graph/'edges.u32le','graph2':graph/'nodes.rrt32','graphlog':d/'graph_axi.txt','design0':d/'design.bin','designlog':d/'design_axi.txt','tables0':inp/'rows.bin','tables1':inp/'columns.bin','tableslog':d/'table_axi.txt','labels0':d/'labels.bin','labelslog':d/'label_axi.txt','owners0':d/'owners.bin','ownerslog':d/'owner_axi.txt','cost0':d/'cost.bin','costlog':d/'cost_axi.txt','qstate0':inp/'connections.bin','qstatelog':d/'qstate_axi.txt','costvectors':inp/'cost_vectors.txt','finallabels':base/'finals.txt','imports':out/'imports.txt','candidates':base/'candidates.txt','polls':base/'polls.txt','faultcase':case,'authority':out/'authority.txt'}
    argv=[BIN/'xsim','joined','--tclbatch','run.tcl','--log',d/'simulate.log']
    for k,v in params.items():argv+=['--testplusarg',str(k)+'='+str(v)]
    run('simulate',argv,build,rec['commands']);shutil.copyfile(build/'natural_trace.txt',d/'natural_trace.txt');shutil.copyfile(build/'simulate.stdout.log',d/'simulate.stdout.log')
    log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('TRANSACTION_FENCE_JOIN_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log
    rec.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()});save();print(d.name,hits[0],flush=True)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
