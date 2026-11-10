"""Full-query owner-B error, real snapshot authority/label recovery and retry."""
from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha

def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/query_checkpoint_join_v3');bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['manifest_sha256']==sha(base/'manifest.json');inp=Path(bm['input']);bench=ROOT/'hardware/variants/bundle_capture_v1';authority_fault=False;no_loss=True;bypass='--bypass'in sys.argv[2:]
 m={'status':'running','base':str(base),'base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'input':str(inp),'sources':{},'rtl':[],'builds':{},'cases':{},'expected_cases':['full_5','pressure_5'],'checkpoint_inactive':False,'query_checkpoint_join':False,'bundle_capture':True,'diagnostic_loss':not no_loss,'checkpoint_bypass':bypass,'authority_fault':authority_fault,'scope':'Healthy quiescent real-system capture under held lease, pending generation query export plus saved-path stream and actual working DDR/label records/context. Host packaging follows simulator retirement. Not yet cold restore or running-authority rotation.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def copy(p,n):
  q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':sha(q)}
 for n,h in bm['sources'].items():
  assert sha(base/'sources'/n)==h['sha256']
  if n in ['runner.py','build_tb.py','tb_query_fault.sv','cp_build.py','cp_reference.sv']:continue
  p=bench/n if(bench/n).is_file()else base/'sources'/n;copy(p,n)
 copy(bench/'tb_query_fault.sv','tb_query_fault.sv');copy(bench/'tb_directory_observer.sv','tb_directory_observer.sv')
 for p,n in [(bench/'build.py','capture_build.py'),(bench/'build_tb.py','capture_tb_build.py'),(Path(__file__),'runner.py')]:copy(p,n)
 m['rtl']=[n for n in bm['rtl']if not Path(n).name.startswith('tb_')]+['tb_directory_observer.sv','tb_query_fault.sv'];save()
 def run(d,stage,argv,record):
  argv=list(map(str,argv));start=time.monotonic()
  with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  record.append({'stage':stage,'argv':argv,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,(d,stage)
 try:
  for mode,define in [('full',None),('pressure','PRESSURE')]:
   build=out/('build_'+mode);build.mkdir();br=m['builds'][mode]={'commands':[]};run(build,'compile',[BIN/'xvlog','--sv','--define','BUNDLE_TRACE']+(['--define',define]if define else[])+(['--define','QC_NO_LOSS']if no_loss else[])+(['--define','QCP_BYPASS']if bypass else[])+[src/n for n in m['rtl']],br['commands']);run(build,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','joined','--debug','typical','--mt','2'],br['commands'])
   name=mode+'_5';d=out/name;d.mkdir();(d/'xsim.dir').symlink_to(build/'xsim.dir',target_is_directory=True);cm=m['cases'][name]={'status':'running','faultcase':5,'mode':mode,'commands':[]};save()
   for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
   with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
   shutil.copyfile(inp/'owners.bin',d/'primary.bin');shutil.copyfile(inp/'owner_allocator.bin',d/'allocator.bin')
   with(d/'pool.bin').open('wb'):pass
   with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
   for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
   (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','joined','--tclbatch','run.tcl','--log','simulate.log'];old=bm['cases'][name]['commands'][-1]['argv']
   for i,x in enumerate(old):
    if x!='--testplusarg':continue
    k,v=old[i+1].split('=',1)
    if k.startswith('snapshot'):continue
    if k in ['design0','owners0','cost0','labels0']or k.endswith('log'):v=str(d/Path(v).name)
    args+=['--testplusarg',k+'='+v]
   for k,v in {'snapshot0':d/'primary.bin','snapshot1':d/'pool.bin','snapshot2':d/'allocator.bin','snapshotlog':d/'snapshot_axi.txt','directorylog':d/'directory.txt'}.items():args+=['--testplusarg',k+'='+str(v)]
   if authority_fault:args+=['--testplusarg','authorityfault=1']
   run(d,'simulate',args,cm['commands']);(d/'xsim.dir').unlink();log=(d/'simulate.log').read_text();hits=[l for l in log.splitlines()if l.startswith('QUERY_FAULT_OBSERVED ')];assert len(hits)==1 and 'Fatal:'not in log and 'outcome=recovered_retry'in hits[0],log[-2000:]
   cm.update(status='observed',result=hits[0],outcome='recovered_retry',artifacts={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.bin','.log','.txt','.tcl']});save();print(name,hits[0],flush=True)
  m['status']='observed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
