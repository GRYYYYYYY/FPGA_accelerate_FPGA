from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_geometry_unit_v3_20261024';out.mkdir();src=out/'sources';shutil.copytree(ROOT/'hardware/hls/search_geometry/v1',src)
 original=ROOT/'results/search_cost_exact_real_20261024/sources/trace.cpp';s=original.read_text()
 a=s.index('        int deltaX = std::abs(childX - sinkX);',s.index('    void evaluateCostAndPush('));b=s.index('        float hBase =',a)
 (src/'original_geometry.inc').write_text(s[a:b]);(out/'make_vectors.py').write_bytes((ROOT/'scripts/make_search_geometry_vectors.py').read_bytes());(out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'running','original_source':str(original),'original_source_sha256':sha(original),'runner_sha256':sha(Path(__file__)),'sources':{p.name:sha(p)for p in src.iterdir()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  cmds=[('vectors',[sys.executable,str(out/'make_vectors.py'),str(out/'vectors.txt')]),('build',['g++','-std=c++14','-O2','-fsanitize=undefined','-fno-sanitize-recover=all',str(src/'kernel.cpp'),str(src/'testbench.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify')]),('probe_build',['g++','-std=c++14','-O0','-fsanitize=undefined','-fno-sanitize-recover=all',str(src/'kernel.cpp'),str(src/'testbench.cpp'),'-o',str(out/'probe')]),('original_ub_probe',[str(out/'probe'),'--probe-ub'])]
  for stage,cmd in cmds:
   with (out/(stage+'.log')).open('w') as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
   m['commands'].append({'stage':stage,'argv':cmd,'exit_code':r.returncode});save()
   if stage=='original_ub_probe':assert r.returncode!=0 and "signed integer overflow: 1 + 2147483647" in (out/(stage+'.log')).read_text()
   else:assert r.returncode==0,stage
  assert 'GEOMETRY_PASS cases=9496 defined_original=8192 errors=0' in (out/'verify.log').read_text()
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file() and p.name!='manifest.json'};save()
 print('GEOMETRY_UNIT_PASS')
if __name__=='__main__':main()
