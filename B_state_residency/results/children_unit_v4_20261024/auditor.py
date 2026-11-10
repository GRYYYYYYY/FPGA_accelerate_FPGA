"""Bind original-function semantics tests and the first-touch replacement boundary."""
from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_children_router import generate,filter_span

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/children_unit_v4_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 original=ROOT/'results/frontier_real_20261024/original_trace.cpp';s=original.read_text();assert sha(original)==m['original_source_sha256']
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest
 for path,key in [('hardware/search/children_machine.hpp','helper_sha256'),('adapters/build_children_router.py','generator_sha256'),('scripts/verify_children_unit.py','runner_sha256')]:
  assert sha(ROOT/path)==sha(out/Path(path).name)==m[key]
 assert sha(out/'test_children_machine.cpp')==sha(ROOT/'hardware/search/test_children_machine.cpp')
 assert sha(out/'RouteNodeType.hpp')==sha(ROOT/'results/exclusion_real_20261024/include/RouteNodeType.hpp')
 modified,_=generate(s,'#include <fstream>');start,end=filter_span(s);newend=modified.index('        if (occLocking) {',start)
 assert s[:start]==modified[:start] and s[end:]==modified[newend:] and s.count('\n')==modified.count('\n')
 a=s.index('    const std::vector<int>& getChildren(int id) {');endmarker='    // ----------------------------------------------------------- RouteNodeGraph.isAccessible'
 assert (out/'original_children.inc').read_text()==s[a:s.index(endmarker,a)]
 assert (out/'candidate_children.inc').read_text()==modified[a:modified.index(endmarker,a)]
 a=s.index('    bool isPartOfExistingRoute(int parent, int child) const {');b=s.index('    // ----------------------------------------------------------------- getChildren',a)
 assert (out/'original_exclusion.inc').read_text()==s[a:b]
 a=s.index('    inline bool canBeDeadEnd(int id) const {');b=s.index('    int getOccupancy(int id) const {',a)
 assert (out/'original_dead.inc').read_text()==s[a:b]
 assert [c['stage']for c in m['commands']]==['build','verify'] and all(c['exit_code']==0 for c in m['commands'])
 log=(out/'verify.log').read_text();assert log.strip()==m['result'];counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',log)}
 assert counts=={'cases':93728,'cached':93728,'empty':66841,'created_dropped':8760,'protocol':1}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'helper_sha256':m['helper_sha256'],'counts':counts,'original_cache_fetch_publish_unchanged':True,'scope':m['scope']}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
