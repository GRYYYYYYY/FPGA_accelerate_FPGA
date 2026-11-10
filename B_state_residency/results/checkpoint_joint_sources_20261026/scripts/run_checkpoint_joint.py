from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources');bench=ROOT/'hardware/variants/checkpoint_stage_v1';capture=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3');bundle=capture/'full_5/bundle';mf=verify(bundle);initial=Path(json.loads((capture/'manifest.json').read_text())['input'])
authority=Path('/tmp/B_state_residency_offer_20261025/authority_rotate_v6/sources')
files=[(authority/n,n)for n in ['checkpoint_authority_reader.sv','owner_state_store.sv','checkpoint_authority_rotator.sv','axi_file_memory.sv']]+[(base/'checkpoint_lease_guard.sv','checkpoint_lease_guard.sv')]+[(bench/n,n)for n in ['recovery_coordinator.sv','config_restore_controller.sv','checkpoint_publish_barrier.sv','tb_joint.sv','build.py','build_tb.py']]+[(Path(__file__),'runner.py')]
m={'status':'running','sources':{},'commands':[],'bundle':str(bundle),'bundle_manifest_sha256':sha(bundle/'manifest.json'),'initial':str(initial),'scope':'Metadata slice: staged native coordinator/config plus dual authority and real checkpoint lease/barrier. Journal stimulus from actual captured six-key delta; no live query/working-owner mutation or path/query/label recovery integration.'}
m['scope']='Metadata slice with native shadow coordinator/config, dual authority, real lease/barrier. Journal interface stimulus uses captured six-key delta; no live routing/working-owner writes or path/query/label recovery integration.'
for p,n in files:shutil.copyfile(p,src/n);m['sources'][n]={'path':str(p),'sha256':sha(src/n)}
for name,primary,allocator in [('old',initial/'owners.bin',initial/'owner_allocator.bin'),('warm',bundle/'owner_primary.bin',bundle/'owner_allocator.bin')]:
 data=primary.read_bytes()+allocator.read_bytes();(out/(name+'.bin')).write_bytes(data);m[name+'_sha256']=sha(out/(name+'.bin'))
import struct
existing=struct.unpack_from('<I',(initial/'owners.bin').read_bytes())[0]-1;assert 0<=existing<mf['net_count'];(out/'existing.hex').write_text(f'00000000\n{existing:08x}\n')
(out/'nodes.hex').write_text(''.join(f'{n:08x}\n'for n,net in __import__('struct').iter_unpack('<2I',(bundle/'journal_absorbed.u32').read_bytes())))
(out/'config_effective.hex').write_text(''.join(f'{w:08x}\n'for w, in struct.iter_unpack('<I',(bundle/'config_effective.bin').read_bytes())))
(out/'run.tcl').write_text('run 20ms\nquit\n')
def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(stage,args):
 t=time.monotonic()
 with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 m['commands'].append({'stage':stage,'argv':list(map(str,args)),'exit_code':r.returncode,'elapsed_s':time.monotonic()-t});save();assert r.returncode==0
try:
 run('compile',[BIN/'xvlog','--sv']+[src/n for n in ['owner_state_store.sv','checkpoint_authority_reader.sv','checkpoint_authority_rotator.sv','checkpoint_lease_guard.sv','recovery_coordinator.sv','config_restore_controller.sv','checkpoint_publish_barrier.sv','axi_file_memory.sv','tb_joint.sv']])
 run('elaborate',[BIN/'xelab','tb_joint','-s','rotate','--debug','typical','--mt','2'])
 run('simulate',[BIN/'xsim','rotate','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','snapshot0='+str(out/'old.bin'),'--testplusarg','snapshot1='+str(out/'warm.bin'),'--testplusarg','snapshotlog='+str(out/'snapshot_axi.txt')])
 log=(out/'simulate.log').read_text();assert 'CHECKPOINT_JOINT_PASS'in log and 'Fatal:'not in log,log[-2200:];m['status']='observed';print(next(l for l in log.splitlines()if l.startswith('CHECKPOINT_JOINT_PASS')))
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
