"""Append pressure case to frozen observed full-only run; never rerun full."""
from pathlib import Path
import json,sys,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
from verify_rtl_bundle import verify
p=Path(sys.argv[1]).resolve();src=p/'sources';m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'and set(m['cases'])=={'full_5'}and m['cases']['full_5']['status']=='observed'
for n,h in m['sources'].items():assert sha(src/n)==h['sha256']
shutil.copyfile(__file__,src/'pressure_runner.py');m['sources']['pressure_runner.py']=dict(path=str(Path(__file__).resolve()),sha256=sha(src/'pressure_runner.py'))
(p/'full_only_manifest.json').write_text((p/'manifest.json').read_text());m['status']='running'
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());inp=Path(bm['input']);name='pressure_5';d=p/name;d.mkdir();bundle=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3')/name/'bundle';mf=verify(bundle);c=m['cases'][name]=dict(status='running',commands=[],bundle=str(bundle),bundle_manifest_sha256=sha(bundle/'manifest.json'))
def save():(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def run(stage,args):
 t=time.monotonic()
 with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
 c['commands'].append(dict(stage=stage,exit_code=r.returncode,elapsed_s=time.monotonic()-t,argv=list(map(str,args))));save();assert r.returncode==0,stage
save()
try:
 run('compile',[BIN/'xvlog','--sv','--define','BUNDLE_TRACE','--define','QC_NO_LOSS','--define','PRESSURE']+[src/n for n in m['rtl']]);run('elaborate',[BIN/'xelab','tb_candidate_offer','-s','normal','--debug','typical','--mt','2'])
 for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
 with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
 shutil.copyfile(inp/'owners.bin',d/'primary.bin');shutil.copyfile(inp/'owner_allocator.bin',d/'allocator.bin');shutil.copyfile(base/name/'pool.bin',d/'pool.bin')
 with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
 for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
 (d/'warm_imports.txt').write_text(''.join(str(n)+' '+' '.join(f'{w:08x}'for w in words)+'\n'for n,*words in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())))
 (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','normal','--tclbatch','run.tcl','--log','simulate.log'];old=m['cases']['full_5']['commands'][-1]['argv']
 for i,x in enumerate(old):
  if x!='--testplusarg':continue
  k,v=old[i+1].split('=',1)
  if k in ['design0','owners0','cost0','labels0','snapshot0','snapshot1','snapshot2','warmimports']or k.endswith('log'):v=str(d/Path(v).name)
  if k=='warmpcrc':v=f'{mf["path_crc32"]:08x}'
  if k=='warmqcrc':v=f'{mf["query_crc32"]:08x}'
  args+=['--testplusarg',k+'='+v]
 run('simulate',args);log=(d/'simulate.log').read_text();assert 'WARM_RESTORE_OBSERVED'in log and 'JOINT_SYSTEM_COMMIT_PASS'in log and 'Fatal:'not in log,log[-1800:];c['status']='observed';m['status']='observed';print('pressure observed',flush=True)
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
