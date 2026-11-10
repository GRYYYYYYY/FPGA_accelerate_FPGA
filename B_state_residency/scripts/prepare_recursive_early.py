"""Original Router immediate recursion + explicitly synthetic five-node AXI images."""
from pathlib import Path
import hashlib,json,shutil,subprocess,os,sys,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';base=ROOT/'results/recursion_order_20261025';g=json.loads((base/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(base/'manifest.json');shutil.copytree(base/'sources',src)
 s=(src/'immediate.cpp').read_text();needle='        push(st, childRnode, newPartial, newTotal, lookahead);';assert s.count(needle)==1
 observe='''        uint32_t join_words[23]={raw_bits(st.shareWeight),uint32_t(countSourceUses),raw_bits(ns[childRnode].baseCost),raw_bits(dyn[childRnode].hist),raw_bits(presentCongestionCosts[getOccupancy(childRnode)-(countSourceUses!=0)]),uint32_t(nets[c.netIdx].connectionsSize),raw_bits(std::abs(childX-nets[c.netIdx].xCenter)+std::abs(childY-nets[c.netIdx].yCenter)),uint32_t(nets[c.netIdx].doubleHpwl),raw_bits(TLD(rnode).upstream),raw_bits(st.rnodeWLWeight),uint32_t(ns[childRnode].length),raw_bits(st.estWlWeight),uint32_t(distanceToSink),uint32_t(lmkReady),raw_bits(lmkInvScale)};
        uint32_t join_result[5]={raw_bits(sharingFactor),raw_bits(getNodeCostSearch(childRnode,c,countSourceUses,sharingFactor)),raw_bits(newPartial),raw_bits(hBase),raw_bits(newTotal)};
        std::printf("C %d %d",rnode,childRnode);for(auto w:join_words)std::printf(" %08x",w);for(auto w:join_result)std::printf(" %08x",w);std::puts("");
'''
 clear_observer='                    std::printf("CLEAR %zu\\n",st.queue->h.size());\n'
 s=s.replace('                    st.queue->clear();',clear_observer+'                    st.queue->clear();',1);(src/'early_observer.txt').write_text(clear_observer)
 s=s.replace(needle,observe+needle,1);(src/'joined.cpp').write_text(s);(src/'cost_observer.txt').write_text(observe)
 # Exact prior constructor and State initializer, original recursive Router methods.
 case=(src/'case.cpp').read_text().replace('#include <stdexcept>','#include <stdexcept>\n#include <fstream>\n#include <string>\nstatic void emit_words(const std::string&p,const std::vector<uint32_t>&v){std::ofstream f(p,std::ios::binary);for(auto w:v)for(int j=0;j<4;++j)f.put(char(w>>(j*8)));if(!f)throw std::runtime_error("image write");}\n')
 case=case.replace('int main(){','int main(int argc,char**argv){if(argc!=2)throw std::runtime_error("args");std::string out=argv[1];',1)
 export='''
 uint32_t qw[16]={0x43505331,0,0,32,0,raw_bits(st.shareWeight),raw_bits(st.rnodeWLWeight),raw_bits(st.estWlWeight),0,0,uint32_t(r.superLongLineLength),0,raw_bits(r.wlWeight),raw_bits(r.directedness),raw_bits(r.cfg.shareExponent),0};
 emit_words(out+"/connections.bin",std::vector<uint32_t>(qw,qw+16));
'''
 case=case.replace(' r.exploreAndExpand(st,0);',export+' r.dyn[2].target=true;queue.offer(1.0f,3);\n r.exploreAndExpand(st,0);',1);(src/'case.cpp').write_text(case);shutil.copyfile(__file__,src/'join_runner.py')
 m={'status':'running','base_audit_sha256':sha(base/'source_bound_audit.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[],'scope':'EARLY target on logical node2 with preseeded nonempty original CPU queue. Explicit synthetic logical graph 0->{1,2},1->{2}; original Router methods and actual cost arithmetic. Physical IDs map logical i to i*8 for page pressure. Not natural device routing.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);save()
 try:
  args=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),'-DROUTER_SOURCE="joined.cpp"',str(src/'case.cpp'),'-o',str(out/'golden')]
  for stage,argv in [('compile',args),('execute',[str(out/'golden'),str(out)])]:
   with(out/(stage+'.log')).open('w')as f:r=subprocess.run(argv,env=env,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0
  log=(out/'execute.log').read_text().splitlines();cost=[l.split()for l in log if l.startswith('C ')];assert len(cost)==2 and all(len(t)==31 for t in cost)
  (out/'cost_vectors.txt').write_text('\n'.join(' '.join(t[1:3]+t[3:])for t in cost)+'\n')
  lab=[l.split()for l in log if l.startswith('L ')];assert len(lab)==5
  (out/'final_labels.txt').write_text('\n'.join(str(int(t[1])*8)+' '+' '.join([t[2],t[3],f'{(int(t[4])*8 if int(t[4])>=0 else 0xffffffff):08x}',f'{int(t[5]):08x}',f'{int(t[6]):08x}'])for t in lab)+'\n')
  def write(name,data,size):assert len(data)<=size;(out/name).write_bytes(data+bytes(size-len(data)))
  phys=[0,8,16,24,32];nodes=33;adj={0:[8,16],8:[16]};offsets=[0];edges=[];attrs=[];design=[]
  for node in range(nodes):
   logical=phys.index(node)if node in phys else 0;active=node in phys;flags=(1|(2 if logical==0 else 0))if active else 0
   attrs.append(struct.pack('<iiBBhhhhhIii',logical,logical,12,flags,logical,0,logical,0,1,0x3f800000,logical,-1))
   edges+=adj.get(node,[]);offsets.append(len(edges));design.append(struct.pack('<4I',int(active),0,0,0))
  write('offsets.u32le',struct.pack('<34I',*offsets),192);write('edges.u32le',struct.pack('<3I',*edges),64);write('nodes.rrt32',b''.join(attrs),1088);write('design.bin',b''.join(design),576)
  expected=bytearray((out/'design.bin').read_bytes());struct.pack_into('<4I',expected,0,5,2,3,0);struct.pack_into('<4I',expected,8*16,5,1,1,0);(out/'expected_design.bin').write_bytes(expected)
  write('owners.bin',bytes(640),640)
  cost_image=bytearray(1280)
  for i in range(nodes):struct.pack_into('<I',cost_image,i*4,0x3f800000)
  for i in range(256):struct.pack_into('<I',cost_image,192+i*4,0x3f800000)
  struct.pack_into('<4I',cost_image,1216,0,0,1,10);(out/'cost.bin').write_bytes(cost_image)
  write('rows.bin',bytes(8),64);write('columns.bin',b'',64)
  layout={'nodes':33,'edges':3,'logical_to_physical':phys,'cost_prices_offset':192,'cost_nets_offset':1216,'owners_pool_offset':576,'owners_allocator_offset':576,'owners_capacity':0,'connections':1,'nets':1,'labels_bytes':3145728,'early_target':16,'seed_node':24,'seed_key':0x3f800000};(out/'layout.json').write_text(json.dumps(layout,indent=2)+'\n');m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('RECURSIVE_EARLY_INPUTS_READY')
if __name__=='__main__':main()
