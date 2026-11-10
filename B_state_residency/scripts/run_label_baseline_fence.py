"""Coherent real iteration2 input through current query/search/route hierarchy."""
from pathlib import Path
import sys,json,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
assert '--disabled'not in sys.argv,'Use the separately audited disabled pair runner'
assert '--negative'not in sys.argv or '--abort'in sys.argv,'Negative mode requires abort stimulus'
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/label_source_crc_full_v2');bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
binding=ROOT/'results/followup_iter2_inputs_20261025.json';bind=json.loads(binding.read_text());assert bind['status']=='passed'
for q,h in bind['audits'].items():assert sha(Path(q)/'source_bound_audit.json')==h
for r in bind['regions'].values():assert sha(Path(r['path']))==r['sha256']
model=Path('/tmp/B_state_residency_offer_20261025/multi_owner_capacity_fixed_v1');assert json.loads((model/'source_bound_audit.json').read_text())['status']=='passed'
m=dict(status='running',base=str(base),binding=str(binding),binding_sha256=sha(binding),sources={},rtl=bm['rtl'],cases={},scope='Real iteration2 prepared input and full32bit sequence180327, current native query/search/backtrace/owner commit/ripup with real multi-net/full pool. Initial generation1 binding and native read-only pool queries; no G2 publication/warm restore yet.')
def copy(p,n):
 (src/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,src/n);m['sources'][n]=dict(path=str(p),sha256=sha(src/n))
from importlib.machinery import SourceFileLoader
feature=SourceFileLoader('baseline_system_builder',str(ROOT/'hardware/variants/label_baseline_system_v1/build.py')).load_module();FILES=list(feature.make())
for n,h in bm['sources'].items():
 assert sha(base/'sources'/n)==h['sha256'];copy(ROOT/'hardware/variants/label_baseline_fence_v1/tb_pair.sv'if n=='tb_query_fault.sv'else ROOT/'hardware/variants/label_baseline_fence_v1'/n if n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv'] else ROOT/'hardware/variants/label_baseline_fence_v1/axi_file_memory.sv' if n=='axi_file_memory.sv' else ROOT/'hardware/variants/label_baseline_system_v1'/n if n in FILES else model/'sources/recovery_coordinator.sv'if n=='recovery_coordinator.sv'else base/'sources'/n,n)
copy(ROOT/'hardware/variants/label_baseline_v1/label_baseline_reader.sv','label_baseline_reader.sv');m['rtl']=['label_baseline_reader.sv']+m['rtl'];copy(ROOT/'hardware/variants/label_baseline_system_v1/build.py','baseline_build.py');copy(ROOT/'hardware/variants/label_baseline_fence_v1/build.py','fence_build.py');copy(ROOT/'hardware/variants/label_baseline_fence_v1/baseline_retirement_guard.sv','baseline_retirement_guard.sv');m['rtl']=['baseline_retirement_guard.sv']+m['rtl'];copy(Path(__file__),'runner.py');copy(ROOT/'hardware/variants/label_baseline_fence_v1/build_tb.py','iter2_build_tb.py')
if '--disabled'in sys.argv:
 import runpy
 (src/'tb_query_fault.sv').write_text(runpy.run_path(str(ROOT/'hardware/variants/label_baseline_system_v1/build_tb.py'))['make_disabled']());m['sources']['tb_query_fault.sv']['sha256']=sha(src/'tb_query_fault.sv');m['disabled']=True
oracle=Path('/tmp/B_state_residency_offer_20261025/followup_iter2_oracle_v1');oldrtl=Path('/tmp/B_state_residency_offer_20261025/followup_iter2_rtl_v1');assert json.loads((oldrtl/'source_bound_audit.json').read_text())['status']=='passed'
for n in ['imports.txt','finals.txt','candidates.txt','polls.txt']:shutil.copyfile(oldrtl/n,out/n)
m['scoreboards']={n:sha(out/n)for n in ['imports.txt','finals.txt','candidates.txt','polls.txt']}
nextbase=out.parent/'followup_iter2_next_v1';nextcost=out.parent/'followup_iter2_next_cost_v1'
for root in [nextbase,nextcost,out.parent/'followup_iter2_next_oracle_v1']:assert json.loads((root/'source_bound_audit.json').read_text())['status']=='passed'
rows=[t.split()for t in(nextbase/'events.txt').read_text().splitlines()]
(out/'polls2.txt').write_text(''.join(' '.join(t[1:4])+'\n'for t in rows if t[0]=='P'))
(out/'candidates2.txt').write_text(''.join(' '.join([t[1],t[2],t[3],str(int(i+1<len(rows)and rows[i+1][0]=='W')),t[8]])+'\n'for i,t in enumerate(rows)if t[0]=='C'))
ids=[int(line.split()[0])for line in(out/'imports.txt').read_text().splitlines()]
with(nextbase/'search_final_nodes.u32').open('rb')as f,(out/'finals2.txt').open('w')as g:
 for node in ids:
  f.seek(node*44);u=struct.unpack('<11I',f.read(44));v=[u[0],u[1],u[3],u[4],u[5]]
  if node==67922:v[4]=0
  g.write(str(node)+' '+ ' '.join(f'{x:08x}'for x in v)+'\n')
m['next_scoreboards']={n:sha(out/n)for n in ['polls2.txt','candidates2.txt','finals2.txt']}

def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(d,stage,args,c):
 args=list(map(str,args));t=time.monotonic()
 with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(args,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 c['commands'].append(dict(stage=stage,argv=args,exit_code=r.returncode,elapsed_s=time.monotonic()-t));save();assert r.returncode==0,stage
m['negative']='--negative'in sys.argv
if m['negative']:
 q=src/'residency_system.sv';t=q.read_text().replace('&&(!ENABLE_BASELINE||baseline_retired)','').replace('(!ENABLE_BASELINE||baseline_retired)&&','');q.write_text(t);m['sources']['residency_system.sv']['sha256']=sha(q)
m['abort_case']='--abort'in sys.argv
m['scope']=('Expected unsafe old-drain counterexample at accepted baseline AR; no routing success claim.'if m['negative']else'Query SOURCE_CHECK abort with actual ninth AXI retirement and held status7, no recovery command.'if m['abort_case']else'Two complete no-preload natural queries with enabled ninth-port retirement guard, compared against prior audited baseline.')
image=out.parent/'label_baseline_image_v1';im=json.loads((image/'manifest.json').read_text());assert json.loads((image/'source_bound_audit.json').read_text())['status']=='passed';assert sha(image/'baseline.bin')==im['baseline_sha256'];m['baseline_image']=str(image);m['baseline_manifest_sha256']=sha(image/'manifest.json')
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
  run(d,'compile',[BIN/'xvlog','--sv','--define','QC_NO_LOSS']+(['--define','BASE_ABORT_DELAY']if '--abort'in sys.argv else[])+(['--define',define]if define else[])+[src/n for n in m['rtl']],c)
  run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','iter2','--debug','typical','--mt','2'],c)
  (d/'run.tcl').write_text('run 30ms\nquit\n')
  args=dict(graph0=graph/'offsets.u32le',graph1=graph/'edges.u32le',graph2=graph/'nodes.rrt32',graphlog=d/'graph_axi.txt',design0=d/'design.bin',designlog=d/'design_axi.txt',tables0=Path(reg['rows']['path']),tables1=Path(reg['columns']['path']),tableslog=d/'table_axi.txt',labels0=d/'labels.bin',labelslog=d/'label_axi.txt',owners0=d/'owners.bin',ownerslog=d/'owner_axi.txt',cost0=d/'cost.bin',costlog=d/'cost_axi.txt',qstate0=Path(reg['connections']['path']),qstatelog=d/'qstate_axi.txt',costvectors=inp/'cost_vectors.txt',finallabels=out/'finals.txt',candidates=out/'candidates.txt',polls=out/'polls.txt',snapshot0=d/'snapshot.bin',snapshot1=d/'pool.bin',snapshot2=d/'allocator.bin',snapshotlog=d/'snapshot_axi.txt',authority=ROOT/'results/transaction_fence_static_join_rtl_v1/authority.txt')
  if '--disabled'in sys.argv:args['imports']=out/'imports.txt'
  if '--abort'in sys.argv:args['baselineabort']=1
  args.update(baseline0=image/'baseline.bin',baselinelog=d/'baseline_axi.txt')
  args.update(cost2=nextcost/'cost_vectors.txt',candidates2=out/'candidates2.txt',polls2=out/'polls2.txt',finals2=out/'finals2.txt')
  cmd=[BIN/'xsim','iter2','--tclbatch','run.tcl','--log','simulate.log']
  for k,v in args.items():cmd+=['--testplusarg',k+'='+str(v)]
  run(d,'simulate',cmd,c);log=(d/'simulate.log').read_text();assert (('Fatal: premature baseline retirement'in log and 'BASELINE_ABORT_PASS'not in log)if m['negative']else(('BASELINE_ABORT_PASS'if '--abort'in sys.argv else'ITER2_PAIR_PASS polls=114 expands=113 candidates=564 costs=302')in log and 'Fatal:'not in log))and '$finish called'in log;c['status']='observed';save();print(name,'observed',flush=True)
 m['status']='observed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
