from pathlib import Path
import hashlib,json,struct,shutil,subprocess,time,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();unit=ROOT/'results/search_access_unit_v3_20261024';graph=ROOT/'results/graph_image_20261024';coord=ROOT/'results/coordinate_inputs_20261024'
 gate=json.loads((unit/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(unit/'manifest.json')
 for p in (unit/'sources').iterdir():
  if p.is_file():shutil.copyfile(p,src/p.name)
 s=(src/'test_access_machine.cpp').read_text().replace('slrTable[256]','slrTable[65536]')
 a=s.index('static void record(');b=s.index('static search_access::State record_start',a)
 s=s[:a]+'''static uint32_t ids[4];static bool auxnode=false;
static uint32_t mapped(uint32_t v){if(v==0xffffffffu)return v;if(v>=4)throw std::runtime_error("prev fixture");return ids[v];}
static void record(uint32_t op,const search_access::Config&c,const search_access::State&before,uint32_t value,const search_access::State&after){
 if(op==0)auxnode=false;uint32_t oldaux=auxnode?mapped(uint32_t(before.aux)):uint32_t(before.aux);
 if(op==1&&(before.phase==13||before.phase==14))value=mapped(value);
 if(op==1&&before.phase==14)auxnode=true;
 uint32_t newaux=auxnode?mapped(uint32_t(after.aux)):uint32_t(after.aux);
 uint32_t in[20]={op,before.phase,before.bits,oldaux,before.action,value,c.sequence,c.flags,c.child_type,c.parent_type,c.sink_type,uint32_t(c.child_x),uint32_t(c.child_tile),uint32_t(c.sink_tile),uint32_t(c.sink_x),uint32_t(c.sink_y),uint32_t(c.xmin),uint32_t(c.xmax),uint32_t(c.ymin),uint32_t(c.ymax)};
 uint32_t out[6]={0,after.phase,after.bits,newaux,search_access::request(after),after.action};
 std::fprintf(vec,"%u %u",steps++,case_id);for(auto v:in)std::fprintf(vec," %08x",v);for(auto v:out)std::fprintf(vec," %08x",v);std::fprintf(vec,"\\n");
}
'''+s[b:]
 s=s[:s.index('int main(){')]+(ROOT/'adapters/access_fabric_fixture_main.inc').read_text()
 (src/'fixture.cpp').write_text(s)
 syn=out/'synthetic';syn.mkdir();attrs=[]
 for n in range(64):
  typ=n%18;by=29+n%3;ey=30+n%3;tile=n%5
  if n==0:ey=32
  if n==54:typ=5;by=20;ey=32;tile=2
  flags=1+(2 if n%2==0 else 0)+(128 if n%3==0 else 0)
  attrs.append(struct.pack('<iiBBhhhhhIii',tile,n,typ,flags,n%3,by,n%3,ey,1,0x3f800000,n,-1))
 (syn/'nodes.rrt32').write_bytes(b''.join(attrs));(syn/'offsets.u32le').write_bytes(bytes(260));(syn/'edges.u32le').write_bytes(b'')
 (syn/'rows.bin').write_bytes(b''.join(struct.pack('<ii',y//32,int(y%32<16))for y in range(128)));(syn/'columns.bin').write_bytes(b''.join(struct.pack('<ii',16 if x<=16 else 48 if x<=48 else 2147483647,-2147483648 if x<16 else 16 if x<48 else 48)for x in range(64)))
 m={'status':'running','gates':{str(unit/'manifest.json'):sha(unit/'manifest.json'),str(unit/'source_bound_audit.json'):sha(unit/'source_bound_audit.json'),str(graph/'manifest.json'):sha(graph/'manifest.json'),str(coord/'manifest.json'):sha(coord/'manifest.json')},'sources':{p.name:sha(p)for p in src.iterdir()if p.is_file()},'commands':[],'cases':{}}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def run(stage,argv,d):
  c={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(c);save();t=time.monotonic()
  with (d/(stage+'.log')).open('w')as log:c['exit_code']=subprocess.call(c['argv'],cwd=d,stdout=log,stderr=subprocess.STDOUT)
  c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,stage
 try:
  run('compile',['g++','-std=c++17','-O2','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(src),src/'fixture.cpp','-o',out/'fixture'],out)
  for case,g,t,N,E,rows,cols in [('synthetic',syn,syn,64,0,128,64),('real',graph,coord/'real',9089009,40469536,311,0)]:
   d=out/case;d.mkdir(exist_ok=True);run('oracle',[out/'fixture',g/'nodes.rrt32',t/'rows.bin',N,rows,0 if case=='synthetic'else 1],d)
   log=(d/'oracle.log').read_text();assert 'FABRIC_ORACLE_PASS'in log and 'runtime error'not in log
   m['cases'][case]={'nodes':N,'edges':E,'rows':rows,'columns':cols,'graph':str(g),'tables':str(t),'result':log.strip()}
  shutil.copyfile(Path(__file__),out/'runner.py');m['status']='passed';m['artifacts']={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='manifest.json'};save();print(json.dumps(m['cases'],indent=2))
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
