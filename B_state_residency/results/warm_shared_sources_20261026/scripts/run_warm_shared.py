"""Full proven commit/GET/q2 scenarios with rebase default-disabled."""
from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/checkpoint_commit_v6');bm=json.loads((base/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text());assert ba['status']=='passed'and ba['manifest_sha256']==sha(base/'manifest.json')
m=dict(status='running',base=str(base),sources={},rtl=bm['rtl'],cases={},scope='Unchanged warm production RTL; inject q2 B error on selected real shared resource, multi-entry G2 journal repair, full restore and q2 retry.')
def copy(f,n):
 (src/n).parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(f,src/n);m['sources'][n]=dict(path=str(f),sha256=sha(src/n))
for n,h in bm['sources'].items():
 assert sha(base/'sources'/n)==h['sha256'];copy((ROOT/'hardware/variants/warm_system_v1'/n) if n in ['residency_system.sv','search_residency_system.sv','query_residency_system.sv'] else ROOT/'hardware/variants/query_warm_rebase_v1/query_lifecycle.sv' if n=='query_lifecycle.sv' else base/'sources'/n,n)
copy(ROOT/'hardware/variants/warm_system_v1/warm_restore_receipt_join.sv','warm_restore_receipt_join.sv');copy(ROOT/'hardware/variants/warm_system_v1/build.py','warm_build.py');m['rtl']=bm['rtl']+['warm_restore_receipt_join.sv'];copy(Path(__file__),'regression_runner.py');copy(ROOT/'hardware/variants/warm_system_v1/build_tb.py','warm_build_tb.py');copy(ROOT/'hardware/variants/warm_shared_v1/build_tb.py','shared_build_tb.py');
(src/'tb_query_fault.sv').write_text((ROOT/'hardware/variants/warm_shared_v1/tb_shared.sv').read_text());m['sources']['tb_query_fault.sv']=dict(path=str(ROOT/'hardware/variants/warm_shared_v1/tb_shared.sv'),sha256=sha(src/'tb_query_fault.sv'));inp=Path(bm['input'])
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(d,stage,args,c):
 t=time.monotonic()
 with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 c['commands'].append(dict(stage=stage,exit_code=r.returncode,elapsed_s=time.monotonic()-t,argv=list(map(str,args))));save();assert r.returncode==0,stage
fault_node=int(next((x.split('=',1)[1]for x in sys.argv if x.startswith('--fault-node=')),'263946'));assert fault_node in [554512,263946];m['fault_node']=fault_node;m['warm_base']='/tmp/B_state_residency_offer_20261025/warm_system_v2'
wm=json.loads((Path(m['warm_base'])/'manifest.json').read_text());assert json.loads((Path(m['warm_base'])/'source_bound_audit.json').read_text())['status']=='passed'
for n,h in m['sources'].items():
 if n not in ['tb_query_fault.sv','regression_runner.py','shared_build_tb.py']:assert h['sha256']==wm['sources'][n]['sha256'],n
try:
 for name,define in [('full_5',None),('pressure_5','PRESSURE')]:
  if '--full-only'in sys.argv and name!='full_5':continue
  d=p/name;d.mkdir();c=m['cases'][name]=dict(status='running',commands=[]);
  bundle=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3')/name/'bundle';mf=__import__('verify_rtl_bundle').verify(bundle);c['bundle']=str(bundle);c['bundle_manifest_sha256']=sha(bundle/'manifest.json');
  import struct
  (d/'warm_imports.txt').write_text(''.join(str(n)+' '+' '.join(f'{w:08x}'for w in words)+'\n'for n,*words in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())));save()
  run(d,'compile',[BIN/'xvlog','--sv','--define','BUNDLE_TRACE','--define','QC_NO_LOSS']+(['--define',define]if define else[])+[src/n for n in m['rtl']],c)
  run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','normal','--debug','typical','--mt','2'],c)
  for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
  with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
  shutil.copyfile(inp/'owners.bin',d/'primary.bin');shutil.copyfile(inp/'owner_allocator.bin',d/'allocator.bin');shutil.copyfile(base/name/'pool.bin',d/'pool.bin')
  with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
  for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
  (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','normal','--tclbatch','run.tcl','--log','simulate.log'];old=bm['cases'][name]['commands'][-1]['argv']
  for i,x in enumerate(old):
   if x!='--testplusarg':continue
   k,v=old[i+1].split('=',1)
   if k in ['design0','owners0','cost0','labels0','snapshot0','snapshot1','snapshot2']or k.endswith('log'):v=str(d/Path(v).name)
   args+=['--testplusarg',k+'='+v]
  args+=['--testplusarg','warmfaultnode='+str(fault_node)];args+=['--testplusarg','warmimports='+str(d/'warm_imports.txt'),'--testplusarg',f'warmpcrc={mf["path_crc32"]:08x}','--testplusarg',f'warmqcrc={mf["query_crc32"]:08x}'];run(d,'simulate',args,c);log=(d/'simulate.log').read_text();assert 'JOINT_SYSTEM_COMMIT_PASS'in log and 'WARM_RESTORE_OBSERVED'in log and 'Fatal:'not in log;assert 'QUERY_FAULT_OBSERVED case=5 outcome=recovered_retry'in log;c['status']='observed';save();print(name,'observed',flush=True)
 m['status']='observed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
