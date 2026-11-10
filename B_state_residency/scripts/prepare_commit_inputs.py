from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();base=ROOT/'results/cost23_inputs_20261025';bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bg['status']=='passed' and bg['manifest_sha256']==sha(base/'manifest.json')
 src=out/'sources';shutil.copytree(base/'sources',src)
 for n,h in bm['sources'].items():assert sha(src/n)==h
 for name in ['owners.bin','cost.bin','edits.txt','graph_attrs.rrt32']:shutil.copyfile(base/name,out/name);assert sha(out/name)==bm['artifacts'][name]
 cpp=(src/'make_inputs.cpp').read_text();original=(src/'reference/trace.cpp').read_text();a=original.index('        TLD(child).lb = newTotal;');b=original.index('        tl_pushes++;',a);prefix=original[a:b];assert prefix.count('TLD(child)')==3
 (src/'original_push_label_prefix.inc').write_text(prefix)
 cpp=cpp.replace('static std::ofstream* cost_out=nullptr;','',1).replace('struct CandidateOracle : Router {','static std::ofstream* cost_out=nullptr;\nstruct CandidateOracle : Router {',1)
 cpp=cpp.replace('void costGolden(int rnode,int childRnode,int ci,std::ofstream& f)', 'void costGolden(int rnode,int childRnode,int ci,unsigned sequence,std::ofstream& f,bool emit)',1).replace('State st{};st.connIdx=ci;Connection& c=connections[ci];','State st{};st.connIdx=ci;st.sequence=sequence;Connection& c=connections[ci];',1)
 start=cpp.index('        for(auto w:words)f<<');end=cpp.index("        f<<std::dec<<'\\n';",start)+len("        f<<std::dec<<'\\n';")
 cpp=cpp[:start]+'        if(emit){\n'+cpp[start:end]+'        }\n'+prefix.replace('TLD(child)','TLD(childRnode)')+cpp[end:]
 marker='selected.emplace_back(childRNode,lookahead,st.earlyTermination);prefixes.push_back(preparePrefix(rnode,childRNode,c.netIdx));';assert cpp.count(marker)==1;cpp=cpp.replace(marker,marker+'costGolden(rnode,childRNode,st.connIdx,st.sequence,*cost_out,false);',1)
 (src/'make_inputs.cpp').write_text(cpp)
 fixture=src/'post_decision_fixture_sll_v5.inc';s=fixture.read_text();a=s.index('  if(post_sll_parents.count(parent)&&r.type[child]==RouteNodeType::SUPER_LONG_LINE){');b=s.index('\n  search_access::Config cfg',a);forced=s[a:b]
 s=s[:a]+s[b:]
 marker=' std::vector<std::tuple<int,bool,bool>>allowed;'
 pre=''' for(int child:kids){
'''+forced+'''
 }
 auto initial_labels=*Router::tl_sparse;
'''
 s=s.replace(marker,pre+marker,1)
 s=s.replace('r.costGolden(parent,child,ci,*cost_out);','r.costGolden(parent,child,ci,seq,*cost_out,true);',1)
 s=s.replace(' for(auto p:saved_prev)Router::tl_sparse->at(p.first).prev=p.second;', ' auto expected_labels=*Router::tl_sparse;*Router::tl_sparse=initial_labels;',1)
 marker=' check(manual_prefix==r.prefixes);'
 compare=''' auto&actual=*Router::tl_sparse;check(actual.paged&&expected_labels.paged&&actual.PSIZE==expected_labels.PSIZE);
 for(size_t page=0;page<actual.pageEp.size();++page){
  bool ea=expected_labels.pageEp[page]==expected_labels.cur,aa=actual.pageEp[page]==actual.cur;
  if(!ea&&!aa)continue;
  for(int i=0;i<actual.PSIZE;++i){
   Router::NodeDyn e{},a{};
   if(ea)e=expected_labels.pool[size_t(expected_labels.pageSlot[page])*actual.PSIZE+i];
   if(aa)a=actual.pool[size_t(actual.pageSlot[page])*actual.PSIZE+i];
   check(CandidateOracle::raw(e.lb)==CandidateOracle::raw(a.lb)&&CandidateOracle::raw(e.upstream)==CandidateOracle::raw(a.upstream)&&e.prev==a.prev&&e.visited==a.visited&&e.target==a.target);
  }
 }
'''
 s=s.replace(marker,compare+marker,1);fixture.write_text(s)
 shutil.copyfile(__file__,src/'commit_runner.py');pb=ROOT/'results/postprev_inputs_v7_20261025';pm=json.loads((pb/'manifest.json').read_text())
 m={'status':'running','base_manifest_sha256':sha(base/'manifest.json'),'base_gate_sha256':sha(base/'source_bound_audit.json'),'owner_layout':pm['owner_layout'],'cost_layout':pm['cost_layout'],'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[],'scope':'Original arithmetic and verbatim push label prefix, both manual access machine and original candidate control receive actual lb/upstream/visited commits from identical full sparse-label snapshots; compare all live page label words after each parent. Heap/recursive scheduling not performed; scripted query contexts and explicit geometry stress, not full route.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out),str(out/'edits.txt')])]:
   start=time.monotonic()
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  for n in ['initial_design.bin','expected_design.bin']:assert sha(out/n)==bm['artifacts'][n],n
  coverage=json.loads((out/'decision_coverage.json').read_text());rows=[s.split()for s in(out/'cost_vectors.txt').read_text().splitlines()];assert len(rows)==coverage['allowed'] and len(rows)>0 and all(len(v)==30 for v in rows)
  assert (out/'vectors.txt').read_text().rstrip().endswith('Q 1 2 5')
  m.update(status='passed',coverage=coverage)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('COMMIT_INPUTS_PASS',m['coverage'])
if __name__=='__main__':main()
