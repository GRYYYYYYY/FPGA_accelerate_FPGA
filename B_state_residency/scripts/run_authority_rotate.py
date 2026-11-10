from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources');bench=ROOT/'hardware/variants/authority_rotate_v1';capture=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3');bundle=capture/'full_5/bundle';mf=verify(bundle);initial=Path(json.loads((capture/'manifest.json').read_text())['input'])
files=[(base/'checkpoint_authority_reader.sv','checkpoint_authority_reader.sv'),(base/'access_owner_v3_20261024/owners/owner_state_store.sv','owner_state_store.sv'),(base/'axi_file_memory.sv','axi_file_memory.sv')]+[(bench/n,n)for n in ['checkpoint_authority_rotator.sv','tb_rotate.sv','build.py','build_tb.py']]+[(Path(__file__),'runner.py')]
m={'status':'running','sources':{},'commands':[],'bundle':str(bundle),'bundle_manifest_sha256':sha(bundle/'manifest.json'),'initial':str(initial),'scope':'Two immutable authority reader banks, real full initial/warm owner images and native codec GETs; staged configuration, atomic selector publish, discard/abort/failure/rearm. Component only; no coordinator journal/config/label/query transaction integration.'}
for p,n in files:shutil.copyfile(p,src/n);m['sources'][n]={'path':str(p),'sha256':sha(src/n)}
for name,primary,allocator in [('old',initial/'owners.bin',initial/'owner_allocator.bin'),('warm',bundle/'owner_primary.bin',bundle/'owner_allocator.bin')]:
 data=primary.read_bytes()+allocator.read_bytes();(out/(name+'.bin')).write_bytes(data);m[name+'_sha256']=sha(out/(name+'.bin'))
import struct
existing=struct.unpack_from('<I',(initial/'owners.bin').read_bytes())[0]-1;assert 0<=existing<mf['net_count'];(out/'existing.hex').write_text(f'00000000\n{existing:08x}\n')
(out/'nodes.hex').write_text(''.join(f'{n:08x}\n'for n,net in __import__('struct').iter_unpack('<2I',(bundle/'journal_absorbed.u32').read_bytes())))
(out/'run.tcl').write_text('run 20ms\nquit\n')
def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(stage,args):
 t=time.monotonic()
 with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
 m['commands'].append({'stage':stage,'argv':list(map(str,args)),'exit_code':r.returncode,'elapsed_s':time.monotonic()-t});save();assert r.returncode==0
try:
 run('compile',[BIN/'xvlog','--sv']+[src/n for n in ['owner_state_store.sv','checkpoint_authority_reader.sv','checkpoint_authority_rotator.sv','axi_file_memory.sv','tb_rotate.sv']])
 run('elaborate',[BIN/'xelab','tb_rotate','-s','rotate','--debug','typical','--mt','2'])
 run('simulate',[BIN/'xsim','rotate','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','snapshot0='+str(out/'old.bin'),'--testplusarg','snapshot1='+str(out/'warm.bin'),'--testplusarg','snapshotlog='+str(out/'snapshot_axi.txt')])
 log=(out/'simulate.log').read_text();assert 'AUTHORITY_ROTATE_PASS'in log and 'Fatal:'not in log,log[-2200:];m['status']='observed';print(next(l for l in log.splitlines()if l.startswith('AUTHORITY_ROTATE_PASS')))
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
