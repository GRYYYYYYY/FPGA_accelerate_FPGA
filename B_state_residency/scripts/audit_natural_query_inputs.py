"""Independent full-image codec and natural geometry/binary32 cost audit."""
from pathlib import Path
import hashlib,json,mmap,struct,sys,contextlib,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def fl(x):return struct.unpack('<f',struct.pack('<I',x))[0]
def f(x):return fl(bits(x))
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());ba=json.loads((base/'source_bound_audit.json').read_text());assert m['status']==ba['status']=='passed'
 assert sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 for name,v in m['sources'].items():assert sha(p/'sources'/name)==v,name
 for name,v in m['artifacts'].items():assert sha(p/name)==v,name
 assert all(c['exit_code']==0 for c in m['commands'])
 for name,v in m['compared'].items():assert sha(p/name)==sha(base/name)==v
 src=p/'sources';obs=(src/'cost_observer.txt').read_text();assert (src/'router.cpp').read_text().replace(obs,'',1)==(base/'sources/router.cpp').read_text()
 dp=src/'make_replay.py';sp=importlib.util.spec_from_file_location('maker',dp);maker=importlib.util.module_from_spec(sp);sp.loader.exec_module(maker)
 cp=src/'derive_cost_inputs.py';sp=importlib.util.spec_from_file_location('costderive',cp);cd=importlib.util.module_from_spec(sp);sp.loader.exec_module(cd)
 router,driver,observer=cd.derive((base/'sources/router.cpp').read_text(),maker.make((base/'sources/router.cpp').read_text()))
 assert router==(src/'router.cpp').read_text() and driver==(src/'replay.cpp').read_text() and obs==observer
 graph=ROOT/'results/graph_image_20261024';ga=json.loads((graph/'source_bound_audit.json').read_text());gm=json.loads((graph/'manifest.json').read_text());assert ga['status']==gm['status']=='passed' and ga['manifest_sha256']==sha(graph/'manifest.json')
 assert gm['input_sha256']==bm['input_sha256']==sha(Path(bm['input']))
 for name in ['offsets.u32le','edges.u32le','nodes.rrt32','config_prefix.rrtbin','design_suffix.rrtbin']:assert sha(graph/name)==gm['artifacts'][name]
 layout=json.loads((p/'input_layout.json').read_text());state=ba['state'];n=layout['nodes'];assert n==ba['nodes']==ga['nodes']
 assert layout['price_offset']==(n*4+63)//64*64 and layout['net_offset']==layout['price_offset']+1024
 assert (base/'initial_overflow.u32').stat().st_size==(base/'initial_caches.u32').stat().st_size==0
 assert (p/'owner_allocator.bin').read_bytes()==bytes(64) and layout['owner_pool_capacity']==0
 prefix=(graph/'config_prefix.rrtbin').read_bytes();wl=struct.unpack_from('<I',prefix,32)[0];exp=struct.unpack_from('<I',prefix,36)[0];sll=struct.unpack_from('<I',prefix,60)[0]
 rows=struct.unpack_from('<I',prefix,68)[0];assert rows==layout['rows'];rowbytes=prefix[72:72+4*rows];haslag=struct.unpack_from('<I',prefix,72+4*rows)[0];assert haslag==layout['has_laguna']==0
 assert (p/'rows.bin').read_bytes()==rowbytes+bytes((-len(rowbytes))%64) and (p/'columns.bin').read_bytes()==bytes(64)
 data=(graph/'design_suffix.rrtbin').read_bytes();nets=struct.unpack_from('<I',data)[0];assert nets==layout['nets'];pos=4;ci=0;sinks=set();netrows=[];C=(p/'connections.bin').read_bytes();assert len(C)==layout['connections']*64
 for ni in range(nets):
  xc,yc,hp,fan,source,num=struct.unpack_from('<IIhiii',data,pos);pos+=22;netrows.append((xc,yc,fan,hp))
  for j in range(num):
   connid,source,sink,na=struct.unpack_from('<4i',data,pos);pos+=16;alts=struct.unpack_from('<'+'i'*na,data,pos)if na else ();pos+=4*na;sinks.add(sink);sinks.update(alts)
   bbox=struct.unpack_from('<4h',data,pos);north,south=data[pos+10],data[pos+11];nr=struct.unpack_from('<I',data,pos+13)[0];pos+=17+nr*4
   expected=(0x43505331,ci,ni,sink,source,*[state[k][0] for k in ['share','wire','estimate']],0,0,sll,(8 if north else 0)|(16 if south else 0),wl,bits(1),exp,0)
   assert struct.unpack_from('<16I',C,ci*64)==expected,ci
   if ci==state['conn_index'][0]:assert [connid]==state['conn_id'] and ni==state['net'][0] and source==state['source'][0] and sink==state['sink'][0]
   ci+=1
 assert pos==len(data) and ci==layout['connections'];assert state['wire']==[bits(f(1-fl(wl)))] and state['estimate']==[wl]
 with contextlib.ExitStack()as stack:
  def mm(path):
   h=stack.enter_context(path.open('rb'));return stack.enter_context(mmap.mmap(h.fileno(),0,access=mmap.ACCESS_READ))
  snap=mm(base/'initial_nodes.u32');attrs=mm(graph/'nodes.rrt32');design=mm(p/'design.bin');owner=mm(p/'owners.bin');cost=mm(p/'cost.bin');labels=mm(p/'initial_labels.native160')
  assert len(design)==len(owner)==(n*16+63)//64*64 and len(labels)==n*20 and len(cost)==(layout['net_offset']+nets*16+63)//64*64
  assert cost[layout['price_offset']:layout['net_offset']]==(base/'prices.u32').read_bytes()
  for ni,row in enumerate(netrows):assert struct.unpack_from('<4I',cost,layout['net_offset']+ni*16)==row
  activeowners=0;refs=0;delta=0
  for i,u in enumerate(struct.iter_unpack('<11I',snap)):
   rawcreated=bool(attrs[i*32+9]&1);assert u[9]>=rawcreated and u[10]==attrs[i*32+8]
   expectedflags=(1 if u[9] and not rawcreated else 0)|(8 if i in sinks else 0)
   assert struct.unpack_from('<4I',design,i*16)==(expectedflags,0,0,0),(i,'design')
   key=0 if u[6]==0xffffffff else u[6]+1
   assert bool(key)==bool(u[7]) and u[8]==int(bool(key)) and u[7]<=65535
   assert struct.unpack_from('<4I',owner,i*16)==(key,u[7]|(u[8]<<16),0,0),(i,'owner')
   assert struct.unpack_from('<I',cost,i*4)[0]==u[2] and struct.unpack_from('<5I',labels,i*20)==(u[0],u[1],u[3],u[4],u[5]),(i,'labels/history')
   activeowners+=bool(key);refs+=u[7];delta+=bool(expectedflags&1)
  assert not any(design[n*16:]) and not any(owner[n*16:]) and not any(cost[n*4:layout['price_offset']]) and not any(cost[layout['net_offset']+nets*16:])
  vectors=[l.split()for l in(p/'cost_vectors.txt').read_text().splitlines()];writes=[list(map(int,l.split()[1:]))for l in(base/'events.txt').read_text().splitlines()if l.startswith('W ')];assert len(vectors)==len(writes)==171
  current={};types={};maxrefs=0;targetcosts=0
  def node(i):return struct.unpack_from('<11I',snap,i*44)
  def attr(i):return struct.unpack_from('<iiBBhhhhhIii',attrs,i*32)
  xc,yc,fan,hp=netrows[state['net'][0]];xc=fl(xc);yc=fl(yc);snk=attr(state['sink'][0]);sinksxy=(snk[4],snk[5])
  for row,w in zip(vectors,writes):
   assert len(row)==30;parent,child=map(int,row[:2]);words=list(map(lambda s:int(s,16),row[2:25]));result=list(map(lambda s:int(s,16),row[25:]));assert [child,parent]==w[:2]
   u=node(child);a=attr(child);pa=attr(parent);childX=a[6];childY=a[5] if u[10]==5 and pa[7]==a[7] else a[7]
   count=u[7] if u[6]==state['net'][0] else 0;occ=min(255,u[8]);pi=max(occ-1,0)if count else occ;price=struct.unpack_from('<I',cost,layout['price_offset']+pi*4)[0]
   dist=f(f(abs(f(childX-xc)))+f(abs(f(childY-yc))));distance=abs(childX-sinksxy[0])+abs(childY-sinksxy[1]);up=current.get(parent,node(parent)[1])
   packet=[state['share'][0],count,a[9],u[2],price,fan,bits(dist),hp,up,state['wire'][0],a[8],state['estimate'][0],distance,0,0]+[0]*8
   assert words==packet,(parent,child,'packet',words,packet)
   sf=f(1+f(fl(words[0])*count));bias=f(f(f(fl(a[9])/fan)*dist)/hp);nc=f(f(f(fl(a[9])*fl(u[2]))*fl(price))/sf);nc=f(nc+min(bias,f(nc/2)))
   partial=f(f(fl(up)+nc)+f(f(fl(words[9])*a[8])/sf));heur=f(fl(words[11])*distance);total=f(partial+f(heur/sf));expected=list(map(bits,[sf,nc,partial,heur,total]))
   assert result==expected,(parent,child,'cost',result,expected)
   assert result[4]==w[2] and result[2]==w[3] and w[4]==1 and w[5]==u[5] and w[6]==0
   current[child]=result[2];types[u[10]]=types.get(u[10],0)+1;maxrefs=max(maxrefs,count);targetcosts+=bool(u[5])
 result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),base_audit_sha256=sha(base/'source_bound_audit.json'),graph_audit_sha256=sha(graph/'source_bound_audit.json'),graph_root=str(graph),nodes=n,connections=ci,live_owner_nodes=activeowners,total_references=refs,created_delta=delta,design_sink_nodes=len(sinks),cost_packets=171,cost_input_words=171*23,cost_result_words=171*5,cost_child_types=types,max_query_refs=maxrefs,target_costs=targetcosts,scope='Full node design/owner/history/native label codecs; full initial connection table and graph binding; natural binary32 geometry/cost independently recomputed for every actual push. No RTL execution, whole-search independent filter proof, or performance measurement.')
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
