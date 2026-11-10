from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();base=ROOT/'results/postprev_inputs_v7_20261025';bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bg['status']=='passed' and bg['manifest_sha256']==sha(base/'manifest.json')
 src=out/'sources';shutil.copytree(base/'sources',src)
 for n,h in bm['sources'].items():assert sha(src/n)==h
 for n in ['owners.bin','cost.bin','edits.txt','graph_attrs.rrt32']:shutil.copyfile(base/n,out/n);assert sha(out/n)==bm['artifacts'][n]
 cpp=(src/'make_inputs.cpp').read_text();reference=(src/'reference/trace.cpp').read_text()
 a=reference.index('    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {');b=reference.index('\n    void exploreAndExpand',a)
 method=reference[a:b];assert method.count('push(st, childRnode, newPartial, newTotal, lookahead);')==1
 ia=reference.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');ib=reference.index('        st.earlyTermination = false;',ia);init=reference[ia:ib]
 newhead='''    void costGolden(int rnode,int childRnode,int ci,std::ofstream& f){
        State st{};st.connIdx=ci;Connection& c=connections[ci];
'''+init
 method=method.replace('    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {\n        Connection& c = connections[st.connIdx];',newhead,1)
 record='''uint32_t words[23]={raw(st.shareWeight),uint32_t(countSourceUses),raw(ns[childRnode].baseCost),raw(dyn[childRnode].hist),raw(presentCongestionCosts[getOccupancy(childRnode)-(countSourceUses!=0)]),uint32_t(nets[c.netIdx].connectionsSize),raw(std::abs(childX-nets[c.netIdx].xCenter)+std::abs(childY-nets[c.netIdx].yCenter)),uint32_t(nets[c.netIdx].doubleHpwl),raw(TLD(rnode).upstream),raw(st.rnodeWLWeight),uint32_t(ns[childRnode].length),raw(st.estWlWeight),uint32_t(distanceToSink),uint32_t(lmkReady),raw(lmkInvScale)};
        if(lmkReady)throw std::runtime_error("unexpected landmark-active profile");
        float nc=getNodeCostSearch(childRnode,c,countSourceUses,sharingFactor);
        uint32_t result[5]={raw(sharingFactor),raw(nc),raw(newPartial),raw(hBase),raw(newTotal)};
        for(auto w:words)f<<' '<<std::hex<<std::setw(8)<<std::setfill('0')<<w;
        for(auto w:result)f<<' '<<std::hex<<std::setw(8)<<std::setfill('0')<<w;
        f<<std::dec<<'\\n';
'''
 method=method.replace('push(st, childRnode, newPartial, newTotal, lookahead);',record,1)
 (src/'original_cost_method.inc').write_text(reference[a:b]);(src/'original_state_initializer.inc').write_text(init)
 cpp=cpp.replace('struct CandidateOracle : Router {', 'struct CandidateOracle : Router {\nstatic uint32_t raw(float f){uint32_t u;std::memcpy(&u,&f,4);return u;}\n'+method,1)
 cpp=cpp.replace('static std::ofstream* prefix_out=nullptr;','static std::ofstream* cost_out=nullptr;\nstatic std::ofstream* prefix_out=nullptr;',1)
 cpp=cpp.replace('CandidateOracle r;r.load(argv[1]);','CandidateOracle r;r.load(argv[1]);r.wlWeight=r.cfg.wirelengthWeight;',1)
 cpp=cpp.replace(' std::ofstream prefix_file(out+"/post_vectors.txt");', ' std::ofstream cost_file(out+"/cost_vectors.txt");cost_out=&cost_file;\n std::ofstream prefix_file(out+"/post_vectors.txt");',1)
 cpp=cpp.replace(' std::ofstream dc(out+"/decision_coverage.json");',' cost_file.flush();if(!cost_file)throw std::runtime_error("cost write failure");\n std::ofstream dc(out+"/decision_coverage.json");',1)
 (src/'make_inputs.cpp').write_text(cpp)
 fixture=src/'post_decision_fixture_sll_v5.inc';s=fixture.read_text();needle='auto p=r.preparePrefix(parent,child,c.netIdx);manual_prefix.push_back(p);';assert s.count(needle)==1;s=s.replace(needle,needle+'*cost_out<<request<<\' \'<<ordinal;r.costGolden(parent,child,ci,*cost_out);',1);fixture.write_text(s)
 shutil.copyfile(__file__,src/'cost23_runner.py');m={'status':'running','base_manifest_sha256':sha(base/'manifest.json'),'base_gate_sha256':sha(base/'source_bound_audit.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[],'scope':'Original evaluateCostAndPush body and real State initializer; only push replaced by logging. No lb/upstream/visited commit or recursive push. Same previous CPU candidate/prefix replay and explicit geometry stress.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out),str(out/'edits.txt')])]:
   start=time.monotonic()
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  for n in ['vectors.txt','post_vectors.txt','initial_design.bin','expected_design.bin']:assert sha(out/n)==bm['artifacts'][n],n
  rows=[s.split()for s in(out/'cost_vectors.txt').read_text().splitlines()];assert len(rows)==713 and all(len(s)==30 for s in rows)
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('COST23_INPUTS_PASS',len(rows))
if __name__=='__main__':main()
