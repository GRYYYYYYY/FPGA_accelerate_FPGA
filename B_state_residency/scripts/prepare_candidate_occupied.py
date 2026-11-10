"""Scripted occupied-state experiment on real graph, with fresh original CPU oracle."""
from pathlib import Path
import hashlib,json,os,shutil,struct,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';dep=ROOT/'results/candidate_decisions_20261024'
 dm=json.loads((dep/'manifest.json').read_text());dg=json.loads((dep/'source_bound_audit.json').read_text());assert dg['status']=='passed' and dg['manifest_sha256']==sha(dep/'manifest.json')
 shutil.copytree(dep/'sources',src)
 for name,digest in dm['sources'].items():assert sha(src/name)==digest
 origowner=ROOT/'results/candidate_initial_owner_20261024';om=json.loads((origowner/'manifest.json').read_text());ol=om['layout'];owners=bytearray((origowner/'owners.bin').read_bytes())
 ci=ROOT/'results/cost_state_inputs_20261025';cm=json.loads((ci/'manifest.json').read_text());cl=cm['cases']['real']['layout'];cost=bytearray((ci/'real/initial.bin').read_bytes())
 selected=[];seen=set()
 for line in (ROOT/'results/candidate_prefetch_pressure_20261025/pressure/prep_inputs.txt').read_text().splitlines():
  r=line.split();node,net=int(r[3]),int(r[4])
  if node not in seen:
   assert not any(owners[node*16:node*16+16]);selected.append((node,net));seen.add(node)
  if len(selected)==8:break
 assert len(selected)==8
 events=[];snapshots=[];allocated=0
 for i,(node,net) in enumerate(selected):
  # primary/overflow placement is intentional; all source refs are exact CPU increments.
  if i==0:entries=[(net,3)]
  elif i==1:entries=[((net+101)%ol['nets'],2)]
  elif i==2:entries=[(net,7),((net+101)%ol['nets'],2)]
  elif i==3:entries=[((net+101)%ol['nets'],1),((net+102)%ol['nets'],4)]
  elif i==4:entries=[((net+101)%ol['nets'],2),(net,5),((net+102)%ol['nets'],1)]
  else:
   others={5:4,6:15,7:31}[i];entries=[((net+101+j)%ol['nets'],1+j%3) for j in range(others)]+[(net,2 if i==5 else 1 if i==6 else 7)]
  assert len({n for n,_ in entries})==len(entries);occ=len(entries);head=allocated+1 if occ>1 else 0
  struct.pack_into('<4I',owners,node*16,entries[0][0]+1,entries[0][1]|(occ<<16),head,0)
  for j,(nw,refs) in enumerate(entries[1:]):
   allocated+=1;ptr=allocated+1 if j<occ-2 else 0
   struct.pack_into('<4I',owners,ol['pool_offset']+(allocated-1)*16,nw+1,refs,ptr,0)
  hist=raw(1.25+i/8);struct.pack_into('<I',cost,node*4,hist)
  for nw,refs in entries:events.append((node,nw,refs))
  snapshots.append({'node':node,'query_net':net,'entries':entries,'history_bits':hist})
 assert allocated==54 and allocated<=ol['pool_capacity'];struct.pack_into('<4I',owners,ol['allocator_offset'],allocated,0,allocated,0)
 factor=1.25
 for i in range(256):struct.pack_into('<I',cost,cl['prices_offset']+i*4,raw(1 if i==0 else 1+i*factor))
 # Sparse files retain exact bytes while avoiding another full allocation.
 def sparse_write(p,data):
  with p.open('wb')as f:
   for i in range(0,len(data),4096):
    b=data[i:i+4096]
    if any(b):f.write(b)
    else:f.seek(len(b),1)
   f.truncate(len(data))
 sparse_write(out/'owners.bin',owners);sparse_write(out/'cost.bin',cost)
 (out/'edits.txt').write_text(''.join(f'{n} {net} {refs}\n' for n,net,refs in events))
 cpp=(src/'make_inputs.cpp').read_text().replace('check(argc==3);','check(argc==4);',1)
 inject='''
 std::ifstream edit(argv[3]);int en,ew,er;check(bool(edit));
 while(edit>>en>>ew>>er){for(int k=0;k<er;++k)r.incrementUser(en,ew);}check(edit.eof());
 r.updatePresentCongestionCosts(1.25f);
 std::ofstream occupied(out+"/cpu_owner_samples.txt");
'''
 for x in snapshots:
  inject+=f' {{uint32_t u={x["history_bits"]}U;std::memcpy(&r.dyn[{x["node"]}].hist,&u,4);}}\n'
  for nw,_ in x['entries']:
   inject+=f' occupied<<{x["node"]}<<" "<<{nw}<<" "<<r.countConnectionsOfUser({x["node"]},{nw})<<" "<<r.getOccupancy({x["node"]})<<"\\n";\n'
 inject+='''
 {std::ofstream cf(out+"/cpu_prices.bin",std::ios::binary);cf.write((char*)r.presentCongestionCosts,sizeof(r.presentCongestionCosts));}
'''
 anchor=' Router::SparseLabels labels;';assert cpp.count(anchor)==1;cpp=cpp.replace(anchor,inject+anchor,1);(src/'make_inputs.cpp').write_text(cpp)
 shutil.copyfile(__file__,src/'occupied_runner.py')
 m={'status':'running','scope':'Scripted occupancy/ref/history/factor changes on real graph; original CPU incrementUser and original candidate golden regenerated. Not naturally observed route updates.',
 'base_manifest_sha256':sha(dep/'manifest.json'),'base_owner_manifest_sha256':sha(origowner/'manifest.json'),'base_cost_manifest_sha256':sha(ci/'manifest.json'),
 'snapshots':snapshots,'events':events,'owner_layout':ol,'cost_layout':cl,'factor_bits':raw(factor),'allocated_overflow':allocated,'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save();env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-ffp-contract=off','-pthread','-I'+str(src),'-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out),str(out/'edits.txt')])]:
   start=time.monotonic()
   with (out/(stage+'.log')).open('w')as f:r=subprocess.run(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':r.returncode,'elapsed_s':time.monotonic()-start});save();assert r.returncode==0,stage
  expected=[(n,nw,refs,len(next(x['entries']for x in snapshots if x['node']==n)))for n,nw,refs in events]
  actual=[tuple(map(int,s.split()))for s in (out/'cpu_owner_samples.txt').read_text().splitlines()];assert actual==expected
  assert (out/'cpu_prices.bin').read_bytes()==cost[cl['prices_offset']:cl['prices_offset']+1024]
  assert 'EXPANSION_INPUTS_PASS'in(out/'execute.log').read_text();m['coverage']=json.loads((out/'decision_coverage.json').read_text());m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};save()
 print(m['coverage'])
if __name__=='__main__':main()
