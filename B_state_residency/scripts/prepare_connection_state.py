"""Export real loaded connections plus the original non-timing State initializer."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,time,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/graph_image_20261024'
 dg=json.loads((dep/'source_bound_audit.json').read_text());assert dg['status']=='passed'and dg['manifest_sha256']==sha(dep/'manifest.json')
 shutil.copytree(dep/'reference',src/'reference');reference=(src/'reference/trace.cpp').read_text()
 a=reference.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');b=reference.index('        st.earlyTermination = false;',a)
 initializer=reference[a:b];assert 'fillLmkT(st, c.sinkRnode);'in initializer and 'batchDirect'in initializer
 cpp='''#define main original_router_main
#include "trace.cpp"
#undef main
#include <fstream>
#include <cstring>
#include <stdexcept>
static uint32_t bits(float f){uint32_t u;std::memcpy(&u,&f,4);return u;}
static void word(std::ofstream&f,uint32_t u){for(int j=0;j<4;++j)f.put(char(u>>(j*8)));}
struct Exporter:Router{
 State stateFor(int index){State st{};st.connIdx=index;auto&c=connections[index];
'''+initializer+''' return st;}
};
int main(int argc,char**argv){
 if(argc!=3)throw std::runtime_error("args");Exporter r;r.load(argv[1]);
 r.wlWeight=r.cfg.wirelengthWeight;
 if(r.lazy||Router::tl_wid>=64||r.lmkReady)throw std::runtime_error("not the initial serial CPU profile");
 std::string out=argv[2];std::ofstream f(out+"/connections.bin",std::ios::binary),list(out+"/connections.tsv");
 if(!f||!list)throw std::runtime_error("open");
 for(size_t i=0;i<r.connections.size();++i){auto&c=r.connections[i];auto st=r.stateFor(i);
  uint32_t words[16]={0x43505331u,uint32_t(i),uint32_t(c.netIdx),uint32_t(c.sinkRnode),uint32_t(c.sourceRnode),bits(st.shareWeight),bits(st.rnodeWLWeight),bits(st.estWlWeight),bits(r.lmkInvScale),uint32_t(r.lmkReady),uint32_t(r.superLongLineLength),uint32_t(c.crossSLRnorth?8:0)|uint32_t(c.crossSLRsouth?16:0),bits(r.wlWeight),bits(r.directedness),bits(r.cfg.shareExponent),0};
  for(auto w:words)word(f,w);
  list<<i<<' '<<c.netIdx<<' '<<c.sinkRnode<<' '<<c.sourceRnode;
  for(int j=5;j<16;++j)list<<' '<<words[j];list<<'\\n';
  for(auto value:st.lmkT)if(value!=0)throw std::runtime_error("uninitialized inactive landmarks");
 }
 f.flush();list.flush();if(!f||!list)throw std::runtime_error("write");
 std::ofstream meta(out+"/layout.json");meta<<"{\\\"nodes\\\":"<<r.ns.size()<<",\\\"nets\\\":"<<r.nets.size()<<",\\\"connections\\\":"<<r.connections.size()<<",\\\"bytes\\\":"<<r.connections.size()*64<<",\\\"wl_bits\\\":"<<bits(r.wlWeight)<<",\\\"directed_bits\\\":"<<bits(r.directedness)<<",\\\"share_exponent_bits\\\":"<<bits(r.cfg.shareExponent)<<",\\\"sll_length\\\":"<<r.superLongLineLength<<",\\\"landmark_ready\\\":false}\\n";meta.flush();if(!meta)throw std::runtime_error("metadata write");
 std::printf("CONNECTION_STATE_EXPORT_PASS connections=%zu\\n",r.connections.size());
}
'''
 (src/'export.cpp').write_text(cpp);(src/'initializer.txt').write_text(initializer);shutil.copyfile(__file__,src/'runner.py')
 m={'status':'running','scope':'Real loaded connection identities and original initializer extracted verbatim for initial serial non-timing CPU profile; not a live route State trace; no landmark build.',
 'base_gate_sha256':sha(dep/'source_bound_audit.json'),'base_manifest_sha256':sha(dep/'manifest.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'export.cpp'),'-o',str(out/'export')]),('execute',[str(out/'export'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out)])]:
   start=time.monotonic()
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  layout=json.loads((out/'layout.json').read_text());assert (out/'connections.bin').stat().st_size==layout['connections']*64==layout['bytes']
  assert sum(1 for _ in(out/'connections.tsv').open())==layout['connections']
  assert 'CONNECTION_STATE_EXPORT_PASS'in(out/'execute.log').read_text();m.update(status='passed',layout=layout)
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print(m['layout'])
if __name__=='__main__':main()
