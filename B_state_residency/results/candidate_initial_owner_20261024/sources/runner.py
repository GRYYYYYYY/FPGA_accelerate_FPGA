"""Produce actual load-time owner memory and cross-check an independent event ledger."""
from pathlib import Path
import hashlib,json,shutil,subprocess,sys,os,struct,mmap,time
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 dep=ROOT/'results/graph_image_20261024';profile=ROOT/'results/owner_profile_real_v4_20261024'
 m={'status':'running','scope':'Actual CPU loader initial owner state exported to AXI record format; no hardware load or routing claimed','sources':{},'gates':{},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for base in [dep,profile]:
  gate=json.loads((base/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(base/'manifest.json')
  m['gates'][str(base/'manifest.json')]=sha(base/'manifest.json');m['gates'][str(base/'source_bound_audit.json')]=sha(base/'source_bound_audit.json')
 shutil.copytree(dep/'reference',src/'reference');shutil.copyfile(ROOT/'hardware/variants/candidate_pipeline_v1/export_initial_owner.cpp',src/'export.cpp');shutil.copyfile(__file__,src/'runner.py')
 m['sources']={str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()};m['input_rrt_sha256']=sha(ROOT/'data/derived/logicnets_jscl.rrt');save()
 env=dict(os.environ);env.pop('LD_LIBRARY_PATH',None);env.pop('LD_PRELOAD',None)
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'export.cpp'),'-o',str(out/'export')]),('execute',[str(out/'export'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out)])]:
   start=time.monotonic()
   with (out/(stage+'.log')).open('w')as f:code=subprocess.call(args,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT)
   m['commands'].append({'stage':stage,'argv':args,'exit_code':code,'elapsed_s':time.monotonic()-start});save();assert code==0,stage
  layout=json.loads((out/'layout.json').read_text());ledger={};events=0
  with (profile/'owner.events').open('rb')as f:
   while True:
    b=f.read(32);assert len(b)==32
    op,node,net,count,occ,owner,owner_refs,overflow=struct.unpack('<8I',b)
    if op==0:
     assert node==layout['nodes']and not any([net,count,occ,owner,owner_refs,overflow]);break
    assert op==1 and node not in ledger and count==occ==owner_refs==1 and owner==net and overflow==0
    ledger[node]=(net,1,1);events+=1
  observed={}
  for line in (out/'owners.tsv').read_text().splitlines():
   node,net,refs,occ=map(int,line.split());assert node not in observed;observed[node]=(net,refs,occ)
  assert observed==ledger and events==layout['occupied']==layout['references']==180326
  # Inspect every node record, including all empty nodes and all reserved words.
  with (out/'owners.bin').open('rb')as f:
   data=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
   assert len(data)==layout['total_bytes']
   for node in range(layout['nodes']):
    net,packed,head,reserved=struct.unpack_from('<4I',data,node*16)
    expected=ledger.get(node)
    assert (net,packed,head,reserved)==((expected[0]+1,0x10001,0,0)if expected else (0,0,0,0)),node
   assert not any(data[layout['nodes']*16:]);data.close()
  m.update(status='passed',layout=layout,independent_load_events=events,all_node_records_checked=layout['nodes'],artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'});save();print(json.dumps({'status':'passed','layout':layout,'all_node_records_checked':layout['nodes']}),flush=True)
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
