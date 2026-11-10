"""Compare streaming first-touch semantics to verbatim original getChildren."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_children_router import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/children_unit_v4_20261024';out.mkdir()
 original=ROOT/'results/frontier_real_20261024/original_trace.cpp';s=original.read_text()
 modified,_=generate(s,'#include <fstream>')
 a=s.index('    const std::vector<int>& getChildren(int id) {');b=s.index('    // ----------------------------------------------------------- RouteNodeGraph.isAccessible',a)
 x=s.index('    bool isPartOfExistingRoute(int parent, int child) const {');y=s.index('    // ----------------------------------------------------------------- getChildren',x)
 d=s.index('    inline bool canBeDeadEnd(int id) const {');e=s.index('    int getOccupancy(int id) const {',d)
 mb=modified.index('    // ----------------------------------------------------------- RouteNodeGraph.isAccessible',a)
 artifacts={'original_children.inc':s[a:b],'candidate_children.inc':modified[a:mb],'original_exclusion.inc':s[x:y],'original_dead.inc':s[d:e]}
 for name,text in artifacts.items():(out/name).write_text(text)
 for p in [ROOT/'hardware/search/children_machine.hpp',ROOT/'hardware/search/test_children_machine.cpp',ROOT/'results/exclusion_real_20261024/include/RouteNodeType.hpp',ROOT/'adapters/build_children_router.py',Path(__file__)]:
  (out/p.name).write_bytes(p.read_bytes())
 m={'status':'running','original_source_sha256':sha(original),'helper_sha256':sha(ROOT/'hardware/search/children_machine.hpp'),'generator_sha256':sha(ROOT/'adapters/build_children_router.py'),'runner_sha256':sha(Path(__file__)),'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,args in [('build',['g++','-std=c++17','-O2','-I'+str(out),str(out/'test_children_machine.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify')])]:
   with (out/(stage+'.log')).open('w') as log:r=subprocess.run(args,stdout=log,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode});save();assert r.returncode==0
  log=(out/'verify.log').read_text();assert 'CHILDREN_UNIT_PASS cases=93728 cached=93728' in log
  m.update(status='passed',result=log.strip(),artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'},scope='Original complete getChildren function versus first-touch request helper; serial simulated lazy/nonlazy and lock variants, dynamic created, pruning, duplicates, empty cache, cache reuse and phase guards. No concurrency or hardware claim.');save();print(log,end='')
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
