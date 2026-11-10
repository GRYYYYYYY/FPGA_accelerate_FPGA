"""Exact-bit and access-order differential against verbatim original Router cost functions."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_search_cost_router import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def extract(s):
 spans=[('    float getNodeCostSearch(', '    inline void incUserSlot('),('    float getNodeCost(', '    // §alpha probe:'),('    void evaluateCostAndPush(', '    void exploreAndExpand(')]
 return '\n'.join(s[s.index(a):s.index(b,s.index(a))] for a,b in spans)
def main():
 out=ROOT/'results/search_cost_unit_20261024';out.mkdir()
 base=ROOT/'results/children_real_20261024';original=base/'sources/trace.cpp';s=original.read_text()
 generated,_=generate(s,'#include <fstream>');assert s.count('\n')==generated.count('\n')
 (out/'original_cost.inc').write_text(extract(s));(out/'candidate_cost.inc').write_text(extract(generated))
 paths=[ROOT/'hardware/search/search_cost.hpp',ROOT/'hardware/search/test_search_cost.cpp',ROOT/'adapters/build_search_cost_router.py',Path(__file__)]
 for p in paths:(out/p.name).write_bytes(p.read_bytes())
 m={'status':'running','original_source_sha256':sha(original),'baseline_gate_sha256':sha(base/'source_bound_audit.json'),'helper_sha256':sha(paths[0]),'generator_sha256':sha(paths[2]),'runner_sha256':sha(Path(__file__)),'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  # UBSan checks the fixture's executed integer geometry too; original sentinel-overflow cases are outside this fixture.
  for stage,cmd in [('build',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(out),str(out/'test_search_cost.cpp'),'-o',str(out/'verify')]),('verify',[str(out/'verify')])]:
   with (out/(stage+'.log')).open('w') as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=120)
   m['commands'].append({'stage':stage,'argv':cmd,'exit_code':r.returncode});save();assert r.returncode==0
  log=(out/'verify.log').read_text();assert 'SEARCH_COST_UNIT_PASS cases=262144' in log
  m.update(status='passed',result=log.strip(),artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='manifest.json'});save();print(log,end='')
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
