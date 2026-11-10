"""Coherent real iteration2 input through current query/search/route hierarchy."""
from pathlib import Path
import sys,json,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/warm_retry_system_v2');bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
binding=ROOT/'results/followup_iter2_inputs_20261025.json';bind=json.loads(binding.read_text());assert bind['status']=='passed'
assert '--minimal'not in sys.argv
for q,h in bind['audits'].items():assert sha(Path(q)/'source_bound_audit.json')==h
for r in bind['regions'].values():assert sha(Path(r['path']))==r['sha256']
model=Path('/tmp/B_state_residency_offer_20261025/multi_owner_capacity_fixed_v1');assert json.loads((model/'source_bound_audit.json').read_text())['status']=='passed'
m=dict(status='running',base=str(base),binding=str(binding),binding_sha256=sha(binding),sources={},rtl=bm['rtl'],cases={},scope='Real iteration2 G1 warm fault recovery after shared owner-B error:822 native labels/path/query receipts, attempt4 replay, full CPU oracle/commit/ripup. Default512 restore parameter preserved, this instance1024. No G2 publication or board claim.')
def copy(p,n):
 (src/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,src/n);m['sources'][n]=dict(path=str(p),sha256=sha(src/n))
for n,h in bm['sources'].items():
 assert sha(base/'sources'/n)==h['sha256'];copy(ROOT/'hardware/variants/iter2_warm_v1/tb_warm.sv'if n=='tb_query_fault.sv'else ROOT/'hardware/variants/iter2_warm_v1'/n if n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv']else model/'sources/recovery_coordinator.sv'if n=='recovery_coordinator.sv'else base/'sources'/n,n)
copy(Path(__file__),'runner.py');copy(ROOT/'hardware/variants/iter2_warm_v1/build.py','warm_build.py');copy(ROOT/'hardware/variants/iter2_warm_v1/build_tb.py','iter2_build_tb.py')
if '--minimal'in sys.argv:
 import runpy
 code=runpy.run_path(str(src/'iter2_build_tb.py'))['make'](True);(src/'tb_query_fault.sv').write_text(code);m['sources']['tb_query_fault.sv']['sha256']=sha(src/'tb_query_fault.sv');m['scope']='Diagnostic only: source/sink labels only; stop at first causal error, not full query proof.'
oracle=Path('/tmp/B_state_residency_offer_20261025/followup_iter2_oracle_v1');oldrtl=Path('/tmp/B_state_residency_offer_20261025/followup_iter2_rtl_v1');assert json.loads((oldrtl/'source_bound_audit.json').read_text())['status']=='passed'
for n in ['imports.txt','finals.txt','candidates.txt','polls.txt']:shutil.copyfile(oldrtl/n,out/n)
m['scoreboards']={n:sha(out/n)for n in ['imports.txt','finals.txt','candidates.txt','polls.txt']}
def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(d,stage,args,c):
 args=list(map(str,args));t=time.monotonic()
 with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 c['commands'].append(dict(stage=stage,argv=args,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
reg=bind['regions'];inp=Path('/tmp/B_state_residency_offer_20261025/followup_iter2_cost_v1');graph=ROOT/'results/graph_image_20261024'
try:
 for name,define in [('full',None),('pressure','PRESSURE')]:
  if '--full-only'in sys.argv and name!='full':continue
  if '--pressure-only'in sys.argv and name!='pressure':continue
  d=out/name;d.mkdir();c=m['cases'][name]=dict(status='running',commands=[]);save()
  for n,k in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(Path(reg[k]['path']),d/n)
  with(d/'owners.bin').open('wb')as f:
   for k in ['owners','owner_pool','owner_allocator']:f.write(Path(reg[k]['path']).read_bytes())
  shutil.copyfile(d/'owners.bin',d/'snapshot.bin');shutil.copyfile(d/'owners.bin',d/'pool.bin');shutil.copyfile(Path(reg['owner_allocator']['path']),d/'allocator.bin')
  with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
  for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
  run(d,'compile',[BIN/'xvlog','--sv','--define','QC_NO_LOSS']+(['--define',define]if define else[])+[src/n for n in m['rtl']],c)
  run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','iter2','--debug','typical','--mt','2'],c)
  (d/'run.tcl').write_text('run 30ms\nquit\n')
  args=dict(graph0=graph/'offsets.u32le',graph1=graph/'edges.u32le',graph2=graph/'nodes.rrt32',graphlog=d/'graph_axi.txt',design0=d/'design.bin',designlog=d/'design_axi.txt',tables0=Path(reg['rows']['path']),tables1=Path(reg['columns']['path']),tableslog=d/'table_axi.txt',labels0=d/'labels.bin',labelslog=d/'label_axi.txt',owners0=d/'owners.bin',ownerslog=d/'owner_axi.txt',cost0=d/'cost.bin',costlog=d/'cost_axi.txt',qstate0=Path(reg['connections']['path']),qstatelog=d/'qstate_axi.txt',costvectors=inp/'cost_vectors.txt',finallabels=out/'finals.txt',imports=out/'imports.txt',candidates=out/'candidates.txt',polls=out/'polls.txt',snapshot0=d/'snapshot.bin',snapshot1=d/'pool.bin',snapshot2=d/'allocator.bin',snapshotlog=d/'snapshot_axi.txt',authority=ROOT/'results/transaction_fence_static_join_rtl_v1/authority.txt')
  cmd=[BIN/'xsim','iter2','--tclbatch','run.tcl','--log','simulate.log']
  for k,v in args.items():cmd+=['--testplusarg',k+'='+str(v)]
  run(d,'simulate',cmd,c);log=(d/'simulate.log').read_text();assert 'ITER2_WARM_PASS polls=171 expands=170 candidates=849 costs=421'in log and 'Fatal:'not in log and '$finish called'in log;c['status']='observed';save();print(name,'observed',flush=True)
 m['status']='observed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
