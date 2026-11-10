from pathlib import Path
import json,hashlib,shutil,subprocess,sys,time,importlib.util
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();m={'status':'preparing','sources':{},'build':[],'cases':{},'scope':'Generation-bound owner snapshot authority component, immutable real prepared primary/pool/allocator images. Only GET requests. Not yet a full checkpoint or integrated recovery-coordinator producer.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 base=ROOT/'results/route_checkpoint_normal_v2/sources';bench=ROOT/'hardware/variants/checkpoint_authority_v1'
 for p in [bench/'checkpoint_authority_reader.sv',bench/'tb_checkpoint_authority.sv',base/'access_owner_v3_20261024/owners/owner_state_store.sv',base/'axi_file_memory.sv',ROOT/'scripts/prepare_checkpoint_authority_vectors.py',Path(__file__)]:
  shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(src/p.name)}
 sp=importlib.util.spec_from_file_location('authority_vectors',src/'prepare_checkpoint_authority_vectors.py');b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);b.ROOT=ROOT
 for i,name in enumerate(['warm_q2_codec_v1','warm_iter2_codec_v1']):
  fixture=b.prepare(ROOT/'results'/name,out/name,101+i,0x100000001+i);m['cases'][name]={'status':'prepared','fixture':fixture,'commands':[]};save()
 def run(d,stage,argv,record):
  argv=list(map(str,argv));start=time.monotonic()
  with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  record.append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,(d,stage)
 try:
  build=out/'build';build.mkdir();m['status']='running';save()
  run(build,'compile',[BIN/'xvlog','--sv',src/'owner_state_store.sv',src/'checkpoint_authority_reader.sv',src/'axi_file_memory.sv',src/'tb_checkpoint_authority.sv'],m['build'])
  run(build,'elaborate',[BIN/'xelab','tb_checkpoint_authority','-s','authority','--debug','typical','--mt','2'],m['build'])
  for name,cm in m['cases'].items():
   d=out/name;f=cm['fixture'];(d/'xsim.dir').symlink_to(build/'xsim.dir',target_is_directory=True);(d/'run.tcl').write_text('run 100ms\nquit\n')
   args={'snapshot0':d/'primary.bin','snapshot1':d/'pool.bin','snapshot2':d/'allocator.bin','snapshotlog':d/'snapshot_axi.txt','vectors':d/'vectors.txt','events':d/'events.txt','nodes':f['nodes'],'capacity':f['capacity'],'checkpoint':f['checkpoint'],'generation':f"{f['generation']:016x}",'primary':f"{f['primary_base']:016x}",'pool':f"{f['pool_base']:016x}",'allocator':f"{f['allocator_base']:016x}",'primarybytes':f['primary_bytes'],'poolbytes':f['pool_bytes']}
   argv=[BIN/'xsim','authority','--tclbatch','run.tcl','--log','simulate.log']
   for k,v in args.items():argv+=['--testplusarg',str(k)+'='+str(v)]
   cm['status']='running';save();run(d,'simulate',argv,cm['commands']);(d/'xsim.dir').unlink();log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('CHECKPOINT_AUTHORITY_PASS ')]
   assert len(hits)==1 and 'Fatal:'not in log and '$finish called'in log,log[-1800:]
   for n,h in f['artifacts'].items():assert sha(d/n)==h,(name,n,'immutable snapshot/vector changed')
   cm.update(status='passed',result=hits[0],artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()});save();print(name,hits[0],flush=True)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
