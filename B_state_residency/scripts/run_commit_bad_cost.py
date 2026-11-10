from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';baseline=len(sys.argv)>2 and sys.argv[2]=='v1';base=Path('/tmp/B_state_residency_commit_20261025/pilot_v1'if baseline else'/tmp/B_state_residency_commit_20261025/pilot_v2');bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed';shutil.copytree(base/'sources',src)
 for name,item in bm['sources'].items():assert sha(src/name)==item['sha256']
 # Use the same directed-error TB for old and guarded top; normal assertions are unchanged unless guard_mode is supplied.
 if baseline:shutil.copyfile(ROOT/'hardware/variants/candidate_commit_v2/tb_candidate_commit.sv',src/'tb_candidate_commit.sv')
 m={'status':'running','baseline_expected_failure':baseline,'base_manifest_sha256':sha(base/'manifest.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'rtl':bm['rtl'],'cases':{},'scope':'Actual joined pipeline with forced bad full-design identity or forced nonzero cost status before commit acceptance. Must assert fault and accept zero cost-label commits. Previous prev/CLEAR/design preparation may have occurred; not AXI fault/drain/reload proof.'}
 shutil.copyfile(__file__,out/'runner.py');m['runner_sha256']=sha(out/'runner.py')
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 inp=ROOT/'results/commit_inputs_20261025';save()
 try:
  for mode in ([1]if baseline else[1,2]):
   d=out/('mode'+str(mode));d.mkdir();cm=m['cases'][str(mode)]={'status':'running','commands':[]}
   for n in ['design','owners','cost']:
    p=inp/('initial_design.bin'if n=='design'else n+'.bin');subprocess.run(['cp','--sparse=always',str(p),str(d/(n+'.bin'))],check=True)
   (d/'labels.bin').open('wb').truncate(3145728);(d/'run.tcl').write_text('run 1000ms\nquit\n')
   for p in(src/'frontier').glob('*.dat'):shutil.copyfile(p,d/p.name)
   args=[str(a).replace(str(base/'pilot'),str(d))for a in bm['cases']['pilot']['commands'][2]['argv']]+['--testplusarg','guard_mode='+str(mode)]
   for stage,argv in [('compile',[BIN/'xvlog','--sv']+[src/n for n in bm['rtl']]),('elaborate',[BIN/'xelab','tb_candidate_commit','-s','candidate','--debug','typical','--mt','2']),('simulate',args)]:
    start=time.monotonic()
    with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,argv)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    cm['commands'].append({'stage':stage,'argv':list(map(str,argv)),'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
   log=(d/'simulate.log').read_text()
   if baseline:assert 'Fatal: bad cost was admitted'in log and 'COMMIT_BAD_COST_GUARD_PASS'not in log;cm['status']='expected_failure'
   else:assert f'COMMIT_BAD_COST_GUARD_PASS mode={mode} accepted=0'in log and 'Fatal:'not in log and '$finish called'in log;cm['status']='passed'
   cm['artifacts']={p.name:sha(p)for p in d.iterdir()if p.is_file()and p.suffix in ['.log','.txt','.bin','.tcl']};save()
  m['status']='expected_failure'if baseline else'passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
 print(m['status'])
if __name__=='__main__':main()
