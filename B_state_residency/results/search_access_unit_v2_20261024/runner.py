from pathlib import Path
import hashlib,json,shutil,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_search_access_router import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(s):
 parts=[]
 for a,b in [('    bool graphIsAccessible(', '    // ----------------------------------------------------------------- cost'),('    void exploreAndExpand(', '    // ----------------------------------------------------------------- rip up / save')]:
  start=s.index(a);end=s.index(b,start);parts.append('#line '+str(s[:start].count('\n')+1)+' "frozen_router.cpp"\n'+s[start:end])
 return '\n'.join(parts)
def main():
 out=ROOT/'results/search_access_unit_v2_20261024';out.mkdir();src=out/'sources';shutil.copytree(ROOT/'hardware/hls/search_access/v2',src)
 base=ROOT/'results/search_geometry_real_v2_20261024';source=base/'sources/trace.cpp';s=source.read_text();candidate,_=generate(s,'#include <fstream>')
 assert s.count('\n')==candidate.count('\n')
 (src/'original_access.inc').write_text(extract(s));cand=extract(candidate).replace('search_access::State as=search_access::start();','search_access::State as=record_start(ac);').replace('search_access::accept(ac,as,value)','record_accept(ac,as,value)');(src/'candidate_access.inc').write_text(cand)
 coords=''
 for a,b in [('    int searchEndY(', '    inline int searchCountUser('),('    int getEndTileYCoordinate(', '    // ----------------------------------------------------------------- isExcluded')]:
  start=s.index(a);end=s.index(b,start);chunk=s[start:end].replace('intYToSLRIndex','slrTable');coords+='#line '+str(s[:start].count('\n')+1)+' "frozen_router.cpp"\n'+chunk+'\n'
 (src/'coordinates.inc').write_text(coords);(src/'RouteNodeType.hpp').write_bytes((base/'include/RouteNodeType.hpp').read_bytes());(out/'generator.py').write_bytes((ROOT/'adapters/build_search_access_router.py').read_bytes());(out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'running','source_path':str(source),'source_sha256':sha(source),'baseline_gate_sha256':sha(base/'source_bound_audit.json'),'generator_sha256':sha(out/'generator.py'),'runner_sha256':sha(Path(__file__)),'sources':{p.name:sha(p)for p in src.iterdir()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,cmd in [('build',['g++','-std=c++17','-O2','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(src),str(src/'test_access_machine.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify')])]:
   with (out/(stage+'.log')).open('w')as f:r=subprocess.run(cmd,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
   m['commands'].append({'stage':stage,'argv':cmd,'exit_code':r.returncode});save();assert r.returncode==0,stage
  assert 'ACCESS_UNIT_PASS cases=46656 ' in (out/'verify.log').read_text();m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='manifest.json'};save()
 print('ACCESS_UNIT_COMPLETE')
if __name__=='__main__':main()
