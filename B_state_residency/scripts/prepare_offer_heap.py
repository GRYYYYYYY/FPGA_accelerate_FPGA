from pathlib import Path
import hashlib,json,subprocess,sys,shutil,os,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def plan(inp,limit):
 cost={}
 for line in(inp/'cost_vectors.txt').read_text().splitlines():
  v=line.split();cost[tuple(map(int,v[:2]))]=int(v[29],16)
 lines=(inp/'vectors.txt').read_text().splitlines();rows=[];q=p=0;seeds=0;expansions=0
 def command(op,key=0,node=0,cookie=0):rows.append((op,key,node,cookie,q,p))
 def control(op):
  if op==0:command(0,cookie=0xf1000000)
  elif op==1:command(3,cookie=0xffffffff);command(3,cookie=0xffffffff)
  elif op==2:command(99);command(4,cookie=0xf1000004)
 i=0
 while i<len(lines):
  v=lines[i].split();i+=1
  if v[0]=='Q':op,q,p=map(int,v[1:]);control(op)
  elif v[0]=='E':
   cookie=int(v[1]);block=[]
   while i<len(lines):
    t=lines[i].split();i+=1;block.append(t)
    if t[0]=='Z':break
   if int(block[-1][2]):
    for si in range(3):command(1,0x3f800000+si*0x00800000,0x10000000+seeds,seeds);seeds+=1
   for t in block:
    if t[0]!='A':continue
    ordinal,node,bits,action=map(int,t[1:5])
    if bits&4:command(5,cookie=ordinal)
    if action==1:command(1,cost[(cookie,ordinal)],node,ordinal)
   expansions+=1
   if limit and expansions==limit:break
 # Testbench closes its current query, opens/ closes one empty post-edit query.
 control(2);q=1;p+=1;control(0);control(2)
 return rows

def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();inp=ROOT/'results/commit_inputs_20261025';im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());assert ig['status']=='passed' and ig['manifest_sha256']==sha(inp/'manifest.json')
 original=(inp/'sources/reference/trace.cpp').read_text();a=original.index('    struct DaryPQ {');b=original.index('    std::vector<DaryPQ::E> pqStorage;',a);heap=original[a:b];assert heap.rstrip().endswith('};');(src/'original_heap.inc').write_text(heap)
 cpp=r'''#include <vector>
#include <cstdint>
#include <cstring>
#include <fstream>
#include <iostream>
#include <stdexcept>
#include "original_heap.inc"
static float fl(uint32_t b){float x;std::memcpy(&x,&b,4);return x;}
static uint32_t raw(float x){uint32_t b;std::memcpy(&b,&x,4);return b;}
int main(int argc,char**argv){
 if(argc!=3)throw std::runtime_error("args");std::ifstream in(argv[1]);std::ofstream out(argv[2]);if(!in||!out)throw std::runtime_error("open");
 std::vector<DaryPQ::E> storage;DaryPQ h(storage,8);uint32_t obs=0,op,key,id,cookie,q,p,aq=0,ap=0;bool active=false;size_t calls=0,peak=0;
 auto apply=[&](uint32_t op,uint32_t key,uint32_t id,uint32_t cookie,uint32_t q,uint32_t p){
  if(op==0){if(active)throw std::runtime_error("open active");active=true;aq=q;ap=p;}
  else if(!active||q!=aq||p!=ap)throw std::runtime_error("owner");
  uint32_t status=0,rkey=0,rid=0;
  if(op==0||op==4||op==5)h.clear();
  else if(op==1){if(h.sz==65536)status=2;else h.offer(fl(key),int(id));}
  else if(op==2){if(h.empty())status=1;else{rkey=raw(h.h[0].lb);rid=uint32_t(h.poll());}}
  else if(op!=3)throw std::runtime_error("op");
  if(op==4)active=false;
  peak=std::max(peak,size_t(h.sz));++calls;
  out<<op<<' '<<key<<' '<<id<<' '<<cookie<<' '<<q<<' '<<p<<' '<<status<<' '<<rkey<<' '<<rid<<' '<<h.sz<<'\n';
 };
 while(in>>op>>key>>id>>cookie>>q>>p){
  if(op==99){while(!h.empty())apply(2,0,0,0xc0000000u|obs++,q,p);apply(2,0,0,0xc0000000u|obs++,q,p);}
  else{if(op==3&&cookie==0xffffffffu)cookie=0xc0000000u|obs++;apply(op,key,id,cookie,q,p);}
 }
 if(!in.eof())throw std::runtime_error("plan parse");out.flush();if(!out||active)throw std::runtime_error("final state/write");std::cout<<"OFFER_HEAP_REFERENCE_PASS calls="<<calls<<" peak="<<peak<<"\n";
}
'''
 (src/'heap_reference.cpp').write_text(cpp);shutil.copyfile(__file__,src/'runner.py');m={'status':'running','input_manifest_sha256':sha(inp/'manifest.json'),'input_audit_sha256':sha(inp/'source_bound_audit.json'),'sources':{p.name:sha(p)for p in src.iterdir()},'cases':{},'commands':[],'scope':'Verbatim original DaryPQ with explicit8-ary profile. Scripted actual cost OFFERs, EARLY CLEAR, separate fixture seeds, CP SIZE and destructive query-end POLL verification. No recursive lookahead or full search.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None);save()
 try:
  args=['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-I'+str(src),str(src/'heap_reference.cpp'),'-o',str(out/'heap_reference')]
  with(out/'compile.log').open('w')as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append({'stage':'compile','argv':args,'exit_code':r.returncode});assert r.returncode==0
  for name,limit in [('pilot',160),('full',0)]:
   rows=plan(inp,limit);(out/(name+'_plan.txt')).write_text(''.join(' '.join(map(str,r))+'\n'for r in rows));args=[str(out/'heap_reference'),str(out/(name+'_plan.txt')),str(out/(name+'_expected.txt'))]
   with(out/(name+'.log')).open('w')as f:r=subprocess.run(args,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=60)
   m['commands'].append({'stage':name,'argv':args,'exit_code':r.returncode});assert r.returncode==0 and 'OFFER_HEAP_REFERENCE_PASS'in(out/(name+'.log')).read_text();m['cases'][name]={'limit':limit,'plan_rows':len(rows),'expected_rows':len((out/(name+'_expected.txt')).read_text().splitlines())}
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print('OFFER_HEAP_INPUTS_PASS',m['cases'])
if __name__=='__main__':main()
