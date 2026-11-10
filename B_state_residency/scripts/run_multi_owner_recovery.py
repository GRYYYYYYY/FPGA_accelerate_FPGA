"""Real full overflow pool, same-node different-net journal recovery component."""
from pathlib import Path
import sys,json,shutil,subprocess,time,struct
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/authority_recovery_v2');bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
fixed='--fixed'in sys.argv;negative='--expect-failure'in sys.argv
m=dict(status='running',base=str(base),sources={},commands=[],fixed=fixed,expected_failure=negative,scope='Real iteration2 full pool and shared-node mutation/recovery component, same node three dirty net keys and duplicate journal. Native owner/authority/coordinator; reconfigure and labels callbacks modeled, not full routing system.')
def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
def copy(p,n):shutil.copyfile(p,src/n);m['sources'][n]=dict(path=str(p),sha256=sha(src/n))
for n in ['owner_state_store.sv','checkpoint_authority_reader.sv','axi_file_memory.sv']:copy(base/'sources'/n,n)
copy(ROOT/'hardware/variants/multi_owner_recovery_v1/recovery_coordinator.sv'if fixed else Path('/tmp/B_state_residency_offer_20261025/warm_retry_system_v2/sources/recovery_coordinator.sv'),'recovery_coordinator.sv')
for p,n in [(ROOT/'hardware/variants/multi_owner_recovery_v1/tb_multi_owner.sv','tb_multi_owner.sv'),(ROOT/'hardware/variants/multi_owner_recovery_v1/build_tb.py','build_tb.py'),(Path(__file__),'runner.py')]:copy(p,n)
if fixed:copy(ROOT/'hardware/variants/multi_owner_recovery_v1/build.py','build.py')
codec=ROOT/'results/warm_iter2_codec_v1';cm=json.loads((codec/'manifest.json').read_text());ca=json.loads((codec/'source_bound_audit.json').read_text());assert ca['status']=='passed'and ca['manifest_sha256']==sha(codec/'manifest.json')
for n,h in cm['artifacts'].items():assert sha(codec/n)==h,n
layout=json.loads((codec/'layout.json').read_text());N=layout['nodes'];C=layout['owner_pool_capacity'];pb=(N*16+63)//64*64;poolb=(C*16+63)//64*64
for a,b in [('owners.bin','primary.bin'),('owner_pool.bin','pool.bin'),('owner_allocator.bin','allocator.bin')]:shutil.copyfile(codec/a,out/b)
assert struct.unpack('<4I',(out/'allocator.bin').read_bytes()[:16])==(C,0,C,0)
node=208292;rows=(out/'primary.bin').read_bytes();a=struct.unpack_from('<4I',rows,node*16);pool=(out/'pool.bin').read_bytes();b=struct.unpack_from('<4I',pool,(a[2]-1)*16);assert a[:3]==(6633,0x20001,1)and b[:3]==(17602,2,0)
mut=[(2,node,6632,1,2,0,1),(1,node,0,0,1,1,2),(1,node,17601,2,2,3,2),(1,node,17601,3,2,4,2)]
(out/'mutations.txt').write_text(''.join(str(i)+' '+' '.join(map(str,[r[1],r[2],r[0],*r[3:]]))+'\n'for i,r in enumerate(mut)))
with(out/'live.bin').open('wb')as f:
 for n in ['primary.bin','pool.bin','allocator.bin']:f.write((out/n).read_bytes())
m['fixture']=dict(codec=str(codec),codec_audit_sha256=sha(codec/'source_bound_audit.json'),nodes=N,capacity=C,primary_bytes=pb,pool_bytes=poolb,node=node,owners={'6632':1,'17601':2},mutations=mut,input_hashes={n:sha(out/n)for n in ['primary.bin','pool.bin','allocator.bin','mutations.txt']});save()
(out/'run.tcl').write_text('run 20ms\nquit\n')
args=dict(live0=out/'live.bin',livelog=out/'live_axi.txt',mutations=out/'mutations.txt',snapshot0=out/'primary.bin',snapshot1=out/'pool.bin',snapshot2=out/'allocator.bin',snapshotlog=out/'snapshot_axi.txt',events=out/'events.txt',nodes=N,capacity=C,checkpoint=102,generation='0000000100000002',primary='91fffff000',pool=f'{0x91fffff000+pb:x}',allocator=f'{0x91fffff000+pb+poolb:x}',primarybytes=pb,poolbytes=poolb,expectfailure=int(negative))
cmd=[BIN/'xsim','multi','--tclbatch','run.tcl','--log','simulate.log']
for k,v in args.items():cmd+=['--testplusarg',str(k)+'='+str(v)]
try:
 for stage,argv in [('compile',[BIN/'xvlog','--sv',src/'owner_state_store.sv',src/'checkpoint_authority_reader.sv',src/'recovery_coordinator.sv',src/'axi_file_memory.sv',src/'tb_multi_owner.sv']),('elaborate',[BIN/'xelab','tb_authority_recovery','-s','multi','--debug','typical','--mt','2']),('simulate',cmd)]:
  argv=list(map(str,argv));start=time.monotonic()
  with(out/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start));save();assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert ('MULTI_OWNER_CAPACITY_REPRO'if negative else 'MULTI_OWNER_RECOVERY_PASS')in log and 'Fatal:'not in log and '$finish called'in log
 m['status']='observed'
except Exception as e:m.update(status='failed',error=repr(e));raise
finally:save()
print(m['status'],flush=True)
