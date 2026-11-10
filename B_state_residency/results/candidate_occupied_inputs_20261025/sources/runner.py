"""Build actual-CSR expansion fixtures with CPU decision prefixes; no RTL claim."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/expansion_inputs_20261024'
 dm=json.loads((dep/'manifest.json').read_text());gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
 for n,d in dm['sources'].items():assert sha(dep/'sources'/n)==d
 shutil.copytree(dep/'sources/reference',src/'reference')
 original=(src/'reference/trace.cpp').read_text();start=original.index('    void exploreAndExpand(State& st, int rnode) {');end=original.index('    // ----------------------------------------------------------------- rip up / save',start)
 method=original[start:end].replace('void exploreAndExpand(','void golden(').replace('evaluateCostAndPush(st, rnode, childRNode, lookahead);','selected.emplace_back(childRNode,lookahead,st.earlyTermination);')
 derived='\n#include <tuple>\nstruct CandidateOracle : Router {\nstd::vector<std::tuple<int,bool,bool>> selected;\n'+method+'\n};\n'
 helper=ROOT/'hardware/variants/candidate_pipeline_v1/decision_fixture.inc';shutil.copyfile(helper,src/'decision_fixture.inc');shutil.copyfile(ROOT/'hardware/hls/search_access/v2/access_machine.hpp',src/'access_machine.hpp')
 s=(dep/'sources/make_inputs.cpp').read_text();anchor='int main(int argc,char**argv){';assert s.count(anchor)==1
 s=s.replace(anchor,derived+'\n#include "decision_fixture.inc"\n'+anchor).replace('Router r;r.load','CandidateOracle r;r.load')
 old='for(int j=0;j<r.ns[parent].childCount;++j)if(masks[parent]&(uint32_t(1)<<j))vec<<"C "<<j<<\' \'<<r.childIds[r.ns[parent].childStart+j]<<\'\\n\';'
 assert s.count(old)==1;s=s.replace(old,old+'\n  decisions(r,vec,parent,result,requests);')
 s=s.replace(' std::ofstream meta(out+"/coverage.json");',' std::ofstream dc(out+"/decision_coverage.json");dc<<"{\\\"decisions\\\":"<<total_decisions<<",\\\"allowed\\\":"<<total_allowed<<",\\\"early\\\":"<<total_early<<",\\\"pruned\\\":"<<total_pruned<<"}\\n";\n std::ofstream meta(out+"/coverage.json");')
 (src/'make_inputs.cpp').write_text(s);shutil.copyfile(__file__,src/'runner.py')
 m={'status':'running','scope':'Actual CSR/CPU getChildren and candidate decisions with actual initial owners; scripted query labels/targets; original decision body cost call replaced by recording, no cost/push/route execution or RTL proof','input_manifest_sha256':sha(dep/'manifest.json'),'input_rrt_sha256':sha(ROOT/'data/derived/logicnets_jscl.rrt'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out)])]:
   t=time.monotonic()
   with (out/(stage+'.log')).open('w')as f:code=subprocess.call(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':code,'elapsed_s':time.monotonic()-t});save();assert code==0,stage
  assert 'EXPANSION_INPUTS_PASS 'in(out/'execute.log').read_text();m.update(status='passed',coverage=json.loads((out/'decision_coverage.json').read_text()),artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'});save();print(json.dumps(m['coverage']),flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
