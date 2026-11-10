"""Fresh RTL bootstrap from committed reference bundles; never mutate capture."""
from pathlib import Path
import sys,json,shutil,subprocess,time,struct,zlib
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify

def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 base=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3');bm=json.loads((base/'manifest.json').read_text());bench=ROOT/'hardware/variants/cold_stream_abort_v1'
 m={'status':'running','base':str(base),'sources':{},'rtl':[],'cases':{},'scope':'Fresh cold reset, warm DDR bundle, native label reconstruction/CRC plus real path/query imports and old-sequence rejection; not runtime rotation or board proof.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for n,h in bm['sources'].items():
  if n in ['query_residency_system.sv','tb_query_fault.sv'] or n not in bm['rtl'] and not n.endswith('.dat'):continue
  assert sha(base/'sources'/n)==h['sha256'];p=src/n;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/n,p);m['sources'][n]={'path':str(base/'sources'/n),'sha256':sha(p)}
 for n in ['query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv','build.py','build_tb.py']:
  shutil.copyfile(bench/n,src/n);m['sources'][n]={'path':str(bench/n),'sha256':sha(src/n)}
 shutil.copyfile(__file__,src/'runner.py');m['sources']['runner.py']={'path':str(Path(__file__).resolve()),'sha256':sha(src/'runner.py')}
 m['rtl']=[n for n in bm['rtl'] if n not in ['tb_query_fault.sv','tb_directory_observer.sv']]+['boot_restore_gate.sv','tb_cold_boot.sv'];save()
 def run(d,stage,args):
  start=time.monotonic()
  with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  rec={'stage':stage,'exit_code':r.returncode,'argv':list(map(str,args)),'elapsed_s':time.monotonic()-start};m['cases'][d.name]['commands'].append(rec);save();assert r.returncode==0,(d,stage)
 try:
  builds={}
  for mode,define in [('full_path',None),('full_query',None),('pressure_path','PRESSURE'),('pressure_query','PRESSURE')]:
   capacity=mode.split('_')[0]
   if '--full-only' in sys.argv and capacity!='full':continue
   bundle=base/(capacity+'_5')/'bundle';manifest=verify(bundle)
   d=out/mode;d.mkdir();m['cases'][mode]={'commands':[],'bundle':str(bundle),'bundle_manifest_sha256':sha(bundle/'manifest.json'),'status':'running'};save()
   if capacity not in builds:
    run(d,'compile',[BIN/'xvlog','--sv','--define','QC_NO_LOSS']+(['--define',define]if define else[])+[src/n for n in m['rtl']])
    run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','cold','--debug','typical','--mt','2'])
    builds[capacity]=d
   else:(d/'xsim.dir').symlink_to(builds[capacity]/'xsim.dir',target_is_directory=True)
   for n in ['design.bin','cost.bin']:shutil.copyfile(bundle/n,d/n)
   with(d/'owners.bin').open('wb')as f:
    f.write((bundle/'owner_primary.bin').read_bytes());f.write((bundle/'owner_allocator.bin').read_bytes())
   with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
   for n in ['owner_primary.bin','owner_pool.bin','owner_allocator.bin']:shutil.copyfile(bundle/n,d/n)
   for n in ['paths','query','config_effective']:
    data=(bundle/(n+'.bin')).read_bytes();(d/(n+'.hex')).write_text(''.join(f'{w:08x}\n'for w, in struct.iter_unpack('<I',data)))
   labels=(bundle/'labels.records').read_bytes();(d/'imports.txt').write_text(''.join(str(row[0])+' '+ ' '.join(f'{w:08x}'for w in row[1:])+'\n'for row in struct.iter_unpack('<6I',labels)))
   for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
   (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','cold','--tclbatch','run.tcl','--log','simulate.log'];old=bm['cases'][capacity+'_5']['commands'][-1]['argv']
   for i,x in enumerate(old):
    if x!='--testplusarg':continue
    k,v=old[i+1].split('=',1)
    if k in ['faultcase','directorylog']:continue
    if k=='snapshot0':v=str(d/'owner_primary.bin')
    elif k=='snapshot1':v=str(d/'owner_pool.bin')
    elif k=='snapshot2':v=str(d/'owner_allocator.bin')
    elif k=='imports':v=str(d/'imports.txt')
    elif k in ['design0','owners0','cost0','labels0']or k.endswith('log'):v=str(d/Path(v).name)
    args+=['--testplusarg',k+'='+v]
   for k,v in {'labelcrc':zlib.crc32(labels),'pathcrc':manifest['path_crc32'],'querycrc':manifest['query_crc32']}.items():args+=['--testplusarg',f'{k}={v:08x}']
   args+=['--testplusarg','interrupt_kind='+('1'if mode.endswith('_path')else'2')]
   run(d,'simulate',args)
   if(d/'xsim.dir').is_symlink():(d/'xsim.dir').unlink()
   log=(d/'simulate.log').read_text();assert 'COLD_BOOT_PASS 'in log and 'Fatal:'not in log,log[-2500:]
   m['cases'][mode]['status']='observed';save();print(mode,[x for x in log.splitlines()if x.startswith('COLD_BOOT_PASS')],flush=True)
  m['status']='observed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
