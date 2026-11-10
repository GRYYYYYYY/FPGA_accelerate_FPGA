"""Compare explicit parent stack against original recursive Router, synthetic graphs."""
from pathlib import Path
import hashlib,json,subprocess,shutil,os,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';base=ROOT/'results/recursion_order_20261025';g=json.loads((base/'source_bound_audit.json').read_text());assert g['status']=='passed' and g['manifest_sha256']==sha(base/'manifest.json');shutil.copytree(base/'sources',src)
 immediate=(src/'immediate.cpp').read_text();a=immediate.index('    void exploreAndExpand(State& st, int rnode) {');b=immediate.index('\n    // ----------------------------------------------------------------- rip up / save',a);old=immediate[a:b]
 new=old.replace('    void exploreAndExpand(State& st, int rnode) {\n        record_expand(rnode);','''    void exploreAndExpand(State& st, int root) {
        struct Frame { int node, next; };
        std::vector<Frame> stack;
        auto enter=[&](int node){ record_expand(node); getChildren(node); stack.push_back({node,0}); };
        enter(root);
        while (!stack.empty()) {
        int rnode=stack.back().node;
''',1)
 new=new.replace('        for (int ki = 0; ki < nk; ki++) {','''        if (st.earlyTermination || stack.back().next >= nk) { stack.pop_back(); continue; }
        int ki=stack.back().next++;
        iterative_child=-1;
        {''',1)
 new=new.replace('            if (st.earlyTermination) break;','''            if (st.earlyTermination) { stack.pop_back(); continue; }
            if (iterative_child >= 0) enter(iterative_child);''',1)
 # One extra scope closes the explicit while loop.
 new=new[:-6]+'        }\n    }\n' if new.endswith('    }\n') else new
 assert new.count('while (!stack.empty())')==1
 iterative=immediate[:a]+new+immediate[b:]
 iterative=iterative.replace('    std::vector<int> order_deferred;','    int iterative_child=-1;\n    std::vector<int> order_deferred;',1).replace('            exploreAndExpand(st, child);','            iterative_child=child;',1)
 (src/'iterative.cpp').write_text(iterative)
 case=(src/'case.cpp').read_text().replace('int main(){','int run_case(int scenario){',1).replace('constexpr int N=5','constexpr int N=64',1)
 case=case.replace('*r.childrenCache[0]={1,2};*r.childrenCache[1]={2};r.ns[0].isLaguna=true;','''
 if(scenario==0){*r.childrenCache[0]={1,2};*r.childrenCache[1]={2};r.ns[0].isLaguna=true;}
 else {
  uint32_t rng=0x9e3779b9u*scenario;
  for(int i=0;i<N;++i){
   r.ns[i].isLaguna=(i%3==0);
   if(scenario==1){if(i+1<N)r.childrenCache[i]->push_back(i+1);r.ns[i].isLaguna=true;}
   else for(int k=0;k<4;++k){rng=rng*1664525u+1013904223u;int child=(rng>>16)%N;if(child!=i)r.childrenCache[i]->push_back(child);}
  }
 }
 if(scenario%2==0 && scenario>0)r.dyn[63].target=1;
 std::printf("CASE %d\\n",scenario);
''')
 case=case.replace('c.sinkRnode=4','c.sinkRnode=63').replace(' std::puts("RECURSION_ORDER_CASE_FINISHED");',' std::puts("RECURSION_ORDER_CASE_FINISHED");return 0;')
 case+='\nint main(){for(int i=0;i<40;++i)run_case(i);}\n';(src/'case.cpp').write_text(case)
 shutil.copyfile(__file__,src/'iterative_runner.py');m={'status':'running','base_audit_sha256':sha(base/'source_bound_audit.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[],'scope':'40 explicit synthetic graphs; original recursive Router vs explicit software parent stack, actual costs/labels/heap; not RTL integration or natural route trace.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);save()
 try:
  for mode in ['immediate','iterative']:
   argv=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),'-DROUTER_SOURCE="'+mode+'.cpp"',str(src/'case.cpp'),'-o',str(out/mode)]
   for stage,args in [('compile',argv),('execute',[str(out/mode)])]:
    with(out/(mode+'_'+stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    m['commands'].append({'mode':mode,'stage':stage,'argv':args,'exit_code':r.returncode});save();assert r.returncode==0,(mode,stage)
  assert (out/'immediate_execute.log').read_bytes()==(out/'iterative_execute.log').read_bytes(),'event/label/queue mismatch'
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('ITERATIVE_RECURSION_PASS cases=40')
if __name__=='__main__':main()
