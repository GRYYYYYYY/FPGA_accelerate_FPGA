from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=ROOT/'results/commit_inputs_20261025';bm=json.loads((base/'manifest.json').read_text());bg=json.loads((base/'source_bound_audit.json').read_text());assert bg['status']=='passed' and bg['manifest_sha256']==sha(base/'manifest.json')
 shutil.copytree(base/'sources/reference',src/'reference');reference=(src/'reference/trace.cpp').read_text()
 header='''#include <cstdio>\n#include <cstdint>\n#include <cstring>\nstatic uint32_t raw_bits(float f){uint32_t b;std::memcpy(&b,&f,4);return b;}\nstatic void record_expand(int n){std::printf("E %d\\n",n);}\nstatic void record_push(int n,float p,float t,bool l,int seq){std::printf("P %d %08x %08x %d %d\\n",n,raw_bits(p),raw_bits(t),int(l),seq);}\nstatic void record_skip(int p,int c){std::printf("S %d %d\\n",p,c);}\n'''
 observed=reference.replace('    void push(State& st, int child, float newPartial, float newTotal, bool lookahead) {', '    std::vector<int> order_deferred;\n    void push(State& st, int child, float newPartial, float newTotal, bool lookahead) {',1)
 observed=observed.replace('        TLD(child).visited = st.sequence;','        TLD(child).visited = st.sequence;\n        record_push(child,newPartial,newTotal,lookahead,st.sequence);',1)
 observed=observed.replace('    void exploreAndExpand(State& st, int rnode) {','    void exploreAndExpand(State& st, int rnode) {\n        record_expand(rnode);',1)
 a=observed.index('    void exploreAndExpand(State& st, int rnode) {');b=observed.index('\n    ',observed.index('\n    }',a)+6) if False else len(observed)
 suffix=observed[a:];assert 'if (TLD(childRNode).visited == seq) continue;'in suffix
 suffix=suffix.replace('if (TLD(childRNode).visited == seq) continue;','if (TLD(childRNode).visited == seq) { record_skip(rnode,childRNode); continue; }',1);observed=observed[:a]+suffix
 (src/'immediate.cpp').write_text(header+observed)
 needle='            exploreAndExpand(st, child);';assert observed.count(needle)==1
 (src/'deferred.cpp').write_text(header+observed.replace(needle,'            order_deferred.push_back(child);',1))
 cpp=r'''#define main original_router_main
#include ROUTER_SOURCE
#undef main
#include <stdexcept>
int main(){
 Router r;r.cfg={};r.cfg.shareExponent=2.0f;r.cfg.wirelengthWeight=0.8f;r.directedness=1.0f;r.batchDirect=1.0f;constexpr int N=5;r.ns.resize(N);r.nc.resize(N);r.dyn.resize(N);r.type.assign(N,RouteNodeType::NON_LOCAL);r.childrenCache.assign(N,nullptr);r.created.assign(N,1);r.deadEnd.assign(N,0);r.isSinkNode.assign(N,0);
 r.ownerNet.assign(N,-1);r.ownerCnt.assign(N,0);r.occCnt.assign(N,0);r.userOverflow.assign(N,nullptr);r.useHotExpand=false;r.occLocking=false;r.doPrefetch=false;r.pruneDeadEnd=false;r.hasLaguna=true;r.cfg.useBoundingBox=false;r.cfg.useUTurnNodes=true;
 for(int i=0;i<N;++i){r.ns[i]={};r.ns[i].tileAddr=i;r.ns[i].baseCost=1.0f;r.ns[i].length=1;r.ns[i].beginX=r.ns[i].endX=i;r.ns[i].beginY=r.ns[i].endY=0;r.nc[i]={};r.nc[i].type=RouteNodeType::NON_LOCAL;r.nc[i].createdAtInit=true;r.dyn[i]={0.0f,0.0f,1.0f,-1,0,0};r.childrenCache[i]=new std::vector<int>();}
 *r.childrenCache[0]={1,2};*r.childrenCache[1]={2};r.ns[0].isLaguna=true;
 r.nets.resize(1);r.nets[0]={0.0f,0.0f,10,1,0};r.connections.resize(1);auto&c=r.connections[0];c.netIdx=0;c.sourceRnode=0;c.sinkRnode=4;c.crossSLRnorth=c.crossSLRsouth=false;c.xMinBB=-10;c.xMaxBB=10;c.yMinBB=-10;c.yMaxBB=10;
 for(float&v:r.presentCongestionCosts)v=1.0f;
 Router::tl_sparse=nullptr;Router::tl_dyn=r.dyn.data();r.wlWeight=r.cfg.wirelengthWeight;r.lmkReady=false;r.lmkInvScale=0;
 std::vector<Router::DaryPQ::E>storage;Router::DaryPQ queue(storage,8);Router::State st{};st.queue=&queue;st.connIdx=0;st.sequence=77;
'''
 ia=reference.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');ib=reference.index('        st.earlyTermination = false;',ia);initializer=reference[ia:ib].replace('cfg.shareExponent','r.cfg.shareExponent').replace('wlWeight','r.wlWeight').replace('* directedness','* r.directedness').replace('if (tl_wid','if (Router::tl_wid').replace('batchDirect','r.batchDirect').replace('fillLmkT(st, c.sinkRnode)','r.fillLmkT(st, c.sinkRnode)')
 cpp+=initializer+r'''
 r.exploreAndExpand(st,0);
 for(size_t i=0;i<r.order_deferred.size();++i)r.exploreAndExpand(st,r.order_deferred[i]);
 for(int i=0;i<N;++i)std::printf("L %d %08x %08x %d %d %d\n",i,raw_bits(r.dyn[i].lb),raw_bits(r.dyn[i].upstream),r.dyn[i].prev,r.dyn[i].visited,int(r.dyn[i].target));
 while(!queue.empty()){uint32_t key=raw_bits(queue.h[0].lb);int id=queue.poll();std::printf("Q %d %08x\n",id,key);}
 std::puts("RECURSION_ORDER_CASE_FINISHED");
}
'''
 (src/'case.cpp').write_text(cpp);shutil.copyfile(__file__,src/'runner.py');m={'status':'running','base_manifest_sha256':sha(base/'manifest.json'),'base_audit_sha256':sha(base/'source_bound_audit.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[],'scope':'Explicit synthetic convergent graph on the original Router class/methods. Original immediate recursion vs one-line replacement by deferred list; observer calls only. Counterexample, not FPGA scheduler validation or natural graph trace.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);save()
 try:
  for mode in ['immediate','deferred']:
   args=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),'-DROUTER_SOURCE="'+mode+'.cpp"',str(src/'case.cpp'),'-o',str(out/mode)]
   for stage,argv in [('compile',args),('execute',[str(out/mode)])]:
    with(out/(mode+'_'+stage+'.log')).open('w')as f:r=subprocess.run(argv,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
    m['commands'].append({'mode':mode,'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0,(mode,stage)
   assert 'RECURSION_ORDER_CASE_FINISHED'in(out/(mode+'_execute.log')).read_text()
  assert (out/'immediate_execute.log').read_text()!=(out/'deferred_execute.log').read_text();m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('RECURSION_ORDER_COUNTEREXAMPLE_READY')
if __name__=='__main__':main()
