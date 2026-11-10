from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,struct,random
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def bits(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def vectors(d):
 layout=json.loads((d/'layout.json').read_text());mem=bytearray((d/'initial.bin').read_bytes());n=layout['nodes'];nets=layout['net_count'];po=layout['prices_offset'];no=layout['nets_offset'];lines=[];observed=[];transactions=[];ver=1;editing=False;active=False;aq=0;ap=0;cookie=0
 def query(on,q=0):
  nonlocal active,aq,ap
  assert not on or not editing
  active=on;aq=q;ap=ver%16;lines.append(f'Q {int(on)} {q} {ap}')
 def cmd(host,op,index=0,value=0,version=None,q=None,p=None):
  nonlocal ver,editing,cookie
  version=ver if version is None else version;q=aq if q is None else q;p=ap if p is None else p;status=0;data=0
  if op==7 or (op in [0,1]and index>=n)or(op in [2,3]and index>=256)or(op==6 and index>=nets):status=1
  elif version!=ver or(not host and(not active or q!=aq or p!=ap or p!=ver%16)):status=3
  elif(not host and op not in [0,2,6])or(host and active)or(op in [0,2,6]and editing)or(op in [1,3]and not editing)or(op==4 and editing)or(op==5 and not editing):status=2
  elif op==4:editing=True;data=ver
  elif op==5:ver+=1;editing=False;data=ver
  else:
   offset=index*4 if op in [0,1]else po+index*4 if op in [2,3]else no+index*16;address=0x1fffff000+(offset&~63)
   if op in [0,2,6]:
    size=16 if op==6 else 4;data=int.from_bytes(mem[offset:offset+size],'little');transactions.append(['R',address,mem[offset&~63:(offset&~63)+64].hex()])
   else:
    lane=offset%64;payload=value<<(lane*8);transactions.append(['W',address,15<<lane,payload]);mem[offset:offset+4]=struct.pack('<I',value)
  cookie+=1;lines.append(f'C {int(host)} {op} {index} {value:08x} {version} {q} {p} {status} {data:032x}');observed.append(f'C {cookie} {status} {data:032x} {ver} {int(editing)}')
 # Every price and sampled history/net record before and after editing.
 sample=sorted({0,n-1,*[i*65537%n for i in range(64)]});nsample=sorted({0,nets-1,*[i*97%nets for i in range(64)]})
 query(True,2)
 for i in sample:cmd(False,0,i)
 for i in range(256):cmd(False,2,i)
 for i in nsample:cmd(False,6,i)
 cmd(True,1,0,bits(2));cmd(False,1,0,bits(2));cmd(False,0,n);cmd(False,2,256);cmd(False,6,nets);cmd(False,7);cmd(False,0,version=0);cmd(False,0,p=(ap+1)%16);cmd(True,4)
 query(False);cmd(True,1,0,bits(2));cmd(True,4)
 for i in sample:cmd(True,1,i,bits(1+(i%31)/8))
 for i in range(256):cmd(True,3,i,bits(1+i/4))
 cmd(True,0,0);cmd(True,4);cmd(True,5)
 query(True,1)
 for i in sample:cmd(False,0,i)
 for i in range(256):cmd(False,2,i)
 for i in nsample:cmd(False,6,i)
 query(False);query(True,3)
 for i in sample:cmd(False,0,i)
 query(False)
 # Full generation protects against the low four-bit price tag aliasing.
 for _ in range(16):cmd(True,4);cmd(True,5)
 query(True,2);cmd(False,0,version=2);cmd(False,0);query(False);cmd(True,0,0)
 (d/'commands.txt').write_text('\n'.join(lines)+'\n');(d/'expected.txt').write_text('\n'.join(observed)+'\n');(d/'expected.bin').write_bytes(mem);(d/'transactions.json').write_text(json.dumps(transactions)+'\n')
 return {'commands':cookie,'final_version':ver,'queries':sum(s.startswith('Q ')for s in lines),'read_transactions':sum(r[0]=='R'for r in transactions),'write_transactions':sum(r[0]=='W'for r in transactions),'layout':layout}
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/graph_image_20261024';gate=json.loads((dep/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')
 shutil.copytree(dep/'reference',src/'reference');shutil.copyfile(ROOT/'hardware/variants/cost_state_v1/export_initial_cost_state.cpp',src/'export.cpp');shutil.copyfile(__file__,src/'runner.py')
 m={'status':'running','scope':'Actual eager CPU loader history/net and initial CPU price table; scripted edits and query lifetimes, not full route histories','sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'graph_manifest_sha256':sha(dep/'manifest.json'),'input_rrt_sha256':sha(ROOT/'data/derived/logicnets_jscl.rrt'),'cases':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();real=out/'real';real.mkdir();synthetic=out/'synthetic';synthetic.mkdir();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'export.cpp'),'-o',str(out/'export')]),('export',[str(out/'export'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(real)])]:
   with (out/(stage+'.log')).open('w')as f:code=subprocess.call(args,env=env,cwd=out,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':code});save();assert code==0,stage
  image=bytearray(4096)
  for i in range(32):struct.pack_into('<I',image,i*4,bits(1+i/16))
  for i in range(256):struct.pack_into('<I',image,1024+i*4,bits(1+i/8))
  for i in range(16):struct.pack_into('<4I',image,2048+i*16,bits(i+.5),bits(i+1.5),i+1,2*i+1)
  (synthetic/'initial.bin').write_bytes(image);(synthetic/'layout.json').write_text(json.dumps({'nodes':32,'net_count':16,'prices_offset':1024,'nets_offset':2048,'total_bytes':4096})+'\n')
  for name in ['synthetic','real']:
   d=out/name;m['cases'][name]=vectors(d);m['cases'][name]['artifacts']={p.name:sha(p)for p in d.iterdir()if p.is_file()};save()
  m['status']='passed';save();print(json.dumps({k:{x:v for x,v in c.items()if x!='artifacts'}for k,c in m['cases'].items()},indent=2))
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
