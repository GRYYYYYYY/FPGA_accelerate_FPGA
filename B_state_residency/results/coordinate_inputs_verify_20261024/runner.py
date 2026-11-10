from pathlib import Path
import hashlib,json,shutil,subprocess,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 inp=ROOT/'results/coordinate_inputs_20261024';im=json.loads((inp/'manifest.json').read_text());assert im['status']=='prepared'
 out=ROOT/'results/coordinate_inputs_verify_20261024';out.mkdir();src=out/'sources';src.mkdir();graph=ROOT/'results/graph_image_20261024'
 shutil.copytree(graph/'reference',src/'reference');(src/'verify.cpp').write_bytes((ROOT/'adapters/verify_coordinate_inputs.cpp').read_bytes());(out/'runner.py').write_bytes(Path(__file__).read_bytes())
 for n,d in im['artifacts'].items():assert sha(inp/n)==d
 m={'status':'running','input_manifest_sha256':sha(inp/'manifest.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'runner_sha256':sha(Path(__file__)),'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,cmd in [('build',['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'verify.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(inp)])]:
   start=time.monotonic()
   with (out/(stage+'.log')).open('w')as f:p=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':cmd,'exit_code':p.returncode,'elapsed_s':time.monotonic()-start});save();assert p.returncode==0
  log=(out/'verify.log').read_text();assert 'COORDINATE_INPUTS_PASS' in log and log.count('PREV_DEFAULT_NEGATIVE hot=')==2
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='manifest.json'};save()
 print(log)
if __name__=='__main__':main()
