from pathlib import Path
import sys,json,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();v=ROOT/'hardware/variants/warm_system_v1';base=Path('/tmp/B_state_residency_offer_20261025/checkpoint_commit_v6/sources');bundle=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3/full_5/bundle');mf=verify(bundle)
m=dict(status='running',sources={},commands=[],bundle=str(bundle),bundle_manifest_sha256=sha(bundle/'manifest.json'),scope='Native three-controller restore slice plus receipt join; mutable behavioral label RAM, TB recovery ownership/repair/active-context inputs; not full-system warm fault recovery.')
files=[((ROOT/'hardware/variants/warm_receipt_join_v1/warm_restore_receipt_join.sv' if '--unfixed'in sys.argv and n=='warm_restore_receipt_join.sv' else v/n),n)for n in ['warm_restore_receipt_join.sv','tb_join_context.sv']]+[(base/n,n)for n in ['label_restore_controller.sv','route_commit_controller.sv']]+[(ROOT/'hardware/variants/query_warm_rebase_v1/query_lifecycle.sv','query_lifecycle.sv'),(Path(__file__),'runner.py')]
for f,n in files:shutil.copyfile(f,src/n);m['sources'][n]=dict(path=str(f),sha256=sha(src/n))
for stem in ['paths','query']:(p/(stem+'.hex')).write_text(''.join(f'{w:08x}\n'for w, in struct.iter_unpack('<I',(bundle/(stem+'.bin')).read_bytes())))
(p/'labels.hex').write_text(''.join(f'{n:08x}'+''.join(f'{w:08x}'for w in reversed(words))+'\n'for n,*words in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())))
(p/'run.tcl').write_text('run 2ms\nquit\n')
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv']+[src/n for n in ['query_lifecycle.sv','route_commit_controller.sv','label_restore_controller.sv','warm_restore_receipt_join.sv','tb_join_context.sv']]),('elaborate',[BIN/'xelab','tb_join','-s','join','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','join','--tclbatch','run.tcl','--log','simulate.log','--testplusarg',f'pcrc={mf["path_crc32"]:08x}','--testplusarg',f'qcrc={mf["query_crc32"]:08x}'])]:
  t=time.monotonic()
  with(p/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=p,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append(dict(stage=stage,exit_code=r.returncode,elapsed_s=time.monotonic()-t,argv=list(map(str,args))));save();assert r.returncode==0,stage
 log=(p/'simulate.log').read_text();assert 'WARM_RECEIPT_JOIN_PASS'in log and 'Fatal:'not in log,log[-1800:];m['status']='observed';print(next(x for x in log.splitlines()if x.startswith('WARM_RECEIPT_JOIN_PASS')))
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
