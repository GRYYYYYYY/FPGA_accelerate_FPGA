"""Actual CPU ordered prev/coordinate/center prefix, keeping original candidate control flow."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,time,os
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';dep=ROOT/'results/candidate_occupied_inputs_v2_20261025'
 dm=json.loads((dep/'manifest.json').read_text());dg=json.loads((dep/'source_bound_audit.json').read_text());assert dg['status']=='passed'and dg['manifest_sha256']==sha(dep/'manifest.json')
 shutil.copytree(dep/'sources',src)
 for n,h in dm['sources'].items():assert sha(src/n)==h
 for name in ['owners.bin','cost.bin','edits.txt']:
  shutil.copyfile(dep/name,out/name);assert sha(out/name)==dm['artifacts'][name]
 cpp=(src/'make_inputs.cpp').read_text();cpp=cpp.replace('#include <tuple>','#include <tuple>\n#include <array>\n#include <map>\n#include <cstring>',1)
 helper='''
std::vector<std::array<uint32_t,7>> prefixes;
std::array<uint32_t,7> preparePrefix(int parent,int child,int net){
 int old=Router::tl_sparse->at(child).prev;
 Router::tl_sparse->at(child).prev=parent;
 float upstream=Router::tl_sparse->at(parent).upstream;
 int x=useHotExpand?hot[child].endX:getEndTileXCoordinate(child);
 int y=searchEndY(child);const auto&nw=nets[net];
 float distance=std::abs(x-nw.xCenter)+std::abs(y-nw.yCenter);
 uint32_t u,d;std::memcpy(&u,&upstream,4);std::memcpy(&d,&distance,4);
 return {uint32_t(parent),uint32_t(child),uint32_t(x),uint32_t(y),u,d,uint32_t(old)};
}
'''
 marker='std::vector<std::tuple<int,bool,bool>> selected;';assert cpp.count(marker)==1;cpp=cpp.replace(marker,marker+helper,1)
 marker='selected.emplace_back(childRNode,lookahead,st.earlyTermination);';assert cpp.count(marker)==1;cpp=cpp.replace(marker,marker+'prefixes.push_back(preparePrefix(rnode,childRNode,c.netIdx));',1)
 cpp=cpp.replace('#include "decision_fixture.inc"','static std::ofstream* prefix_out=nullptr;\nstatic std::set<int> post_sll_parents;\n#include "post_decision_fixture_sll.inc"',1)
 cpp=cpp.replace(' Router::SparseLabels labels;',' std::ofstream prefix_file(out+"/post_vectors.txt");prefix_out=&prefix_file;\n Router::SparseLabels labels;',1)
 # Seed nonzero upstream via the same explicit label interface used by hardware.
 old='else labels.at(node).visited=value;';assert old in cpp;cpp=cpp.replace(old,'else if(field==1)std::memcpy(&labels.at(node).upstream,&value,4);else labels.at(node).visited=value;',1)
 marker='label(p,3,i+17);';assert cpp.count(marker)==1;cpp=cpp.replace(marker,marker+'label(p,1,0x3f800000u+uint32_t(i)*0x10000u);',1)
 marker='label(p,3,99);';assert cpp.count(marker)==1;cpp=cpp.replace(marker,marker+'label(p,1,0x40000000u+uint32_t(i)*0x10000u);',1)
 target_code='''
 size_t reversed=0,forward=0;std::ofstream targeted(out+"/sll_targets.txt");
 for(size_t p=0;p<n&&(reversed<4||forward<4);++p){
  for(int k=0;k<r.ns[p].childCount;++k){int child=r.childIds[r.ns[p].childStart+k];
   if(r.type[child]!=RouteNodeType::SUPER_LONG_LINE)continue;
   bool reverse=r.ns[p].endY==r.ns[child].endY;
   if((reverse?reversed:forward)>=4||!post_sll_parents.insert(p).second)continue;
   parents.insert(p);(reverse?reversed:forward)++;
   targeted<<p<<' '<<child<<' '<<reverse<<std::endl;break;
  }
 }
 targeted.flush();check(reversed+forward>0);
'''
 cpp=cpp.replace(' std::mt19937 rng(20261025);',target_code+' std::mt19937 rng(20261025);',1)
 cpp=cpp.replace(' std::vector<int> ordered(parents.begin(),parents.end());',' std::vector<int> ordered(parents.begin(),parents.end());std::stable_partition(ordered.begin(),ordered.end(),[](int p){return post_sll_parents.count(p)!=0;});',1)
 cpp=cpp.replace(' auto expand=[&](int parent,bool prune){',' auto expand=[&](int parent,bool prune){if(post_sll_parents.count(parent))prune=false;',1)
 cpp=cpp.replace('created_delta.assign(n,0);','created_delta.assign(n,0);r.hasLaguna=true;',1)
 (src/'make_inputs.cpp').write_text(cpp);shutil.copyfile(ROOT/'hardware/variants/candidate_postprev_v1/post_decision_fixture_sll.inc',src/'post_decision_fixture_sll.inc');shutil.copyfile(__file__,src/'postprev_runner.py')
 m={'status':'running','scope':'Original CPU candidate control flow with ordered prev-write/read-prefix hook replacing full cost/push; scripted upstream labels and occupied initial state; not full route or recursive lookahead.',
 'force_has_laguna_for_SLL_stress':True,'base_gate_sha256':sha(dep/'source_bound_audit.json'),'base_manifest_sha256':sha(dep/'manifest.json'),'owner_layout':dm['owner_layout'],'cost_layout':dm['cost_layout'],
 'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out),str(out/'edits.txt')])]:
   start=time.monotonic()
   with (out/(stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  for name in ['initial_design.bin','expected_design.bin']:assert (out/name).stat().st_size==145424192
  text=(out/'vectors.txt').read_text();cov=json.loads((out/'decision_coverage.json').read_text());assert sum(s.startswith('E ')for s in text.splitlines())==json.loads((out/'coverage.json').read_text())['expansions']>=1212 and text.rstrip().endswith('Q 1 2 5')
  assert len((out/'post_vectors.txt').read_text().splitlines())==cov['allowed']
  assert 'EXPANSION_INPUTS_PASS'in(out/'execute.log').read_text();m.update(status='passed',coverage=cov)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print(m['coverage'])
if __name__=='__main__':main()
