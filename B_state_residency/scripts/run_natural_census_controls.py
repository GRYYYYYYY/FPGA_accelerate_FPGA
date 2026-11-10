from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve();m={'status':'running','base_manifest_sha256':sha(base/'manifest.json'),'control_sha256':sha(out/'control.cpp'),'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 for n,h in bm['sources'].items():assert sha(base/'sources'/n)==h
 m['base_sources']=bm['sources'];shutil.copyfile(__file__,out/'runner.py');m['runner_sha256']=sha(out/'runner.py');save()
 try:
  argv=['g++','-std=c++17','-O3','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread','-I'+str(base/'sources'),'-I'+str(base/'sources/include'),str(out/'control.cpp'),'-o',str(out/'control')]
  stages=[('compile',argv,{})]+[(mode,[str(out/'control'),value],{'B_RECURSION_CENSUS':str(out/(mode+'.txt'))})for mode,value in [('negative','0'),('positive','1')]]
  for name,argv,extra in stages:
   env={k:v for k,v in os.environ.items()if not k.startswith(('RW_','B_'))};env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);env.update(extra)
   with(out/(name+'.log')).open('w')as f:r=subprocess.run(argv,env=env,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':name,'argv':argv,'environment':extra,'exit_code':r.returncode});save();assert r.returncode==0
  def row(name):
   lines=(out/(name+'.txt')).read_text().splitlines();assert len(lines)==2;return dict(zip(lines[0].split(),map(int,lines[1].split())))
  p,n=row('positive'),row('negative');assert [p[k]for k in ['expansions','pushes','lookahead','lookahead_with_siblings','max_depth','first_parent','first_child','first_position','first_remaining','first_degree']]==[2,2,1,1,2,0,1,0,1,2]
  assert [n[k]for k in ['expansions','pushes','lookahead','lookahead_with_siblings','max_depth']]==[1,2,0,0,1]
  original=(ROOT/'results/recursion_order_20261025/immediate_execute.log').read_text().splitlines();expected=[l for l in original if l.startswith(('L ','Q ','RECURSION_ORDER_CASE_FINISHED'))];assert [l for l in(out/'positive.log').read_text().splitlines()if not l.startswith('RECURSION_CENSUS_FINISHED')]==expected
  m.update(status='passed',positive=p,negative=n)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('NATURAL_CENSUS_CONTROLS_PASS')
if __name__=='__main__':main()
