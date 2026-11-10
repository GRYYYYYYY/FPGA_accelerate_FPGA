from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 base=ROOT/'results/cost23_inputs_20261025';bm=json.loads((base/'manifest.json').read_text());assert m['base_manifest_sha256']==sha(base/'manifest.json') and m['base_gate_sha256']==sha(base/'source_bound_audit.json')
 for n in ['initial_design.bin','expected_design.bin','cost.bin','owners.bin','graph_attrs.rrt32']:assert m['artifacts'][n]==bm['artifacts'][n]
 source=(out/'sources/reference/trace.cpp').read_text();a=source.index('    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {');b=source.index('\n    void exploreAndExpand',a);method=source[a:b]
 assert (out/'sources/original_cost_method.inc').read_text()==method
 body=method[method.index('        int countSourceUses'):method.index('        push(st, childRnode, newPartial, newTotal, lookahead);')]
 cpp=(out/'sources/make_inputs.cpp').read_text();a=cpp.index('    void costGolden(');b=cpp.index('std::vector<std::tuple<int,bool,bool>> selected;',a);golden=cpp[a:b];assert body in golden
 ia=source.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');ib=source.index('        st.earlyTermination = false;',ia)
 assert (out/'sources/original_state_initializer.inc').read_text()==source[ia:ib] and source[ia:ib] in golden
 assert 'push(st,' not in golden
 pa=source.index('        TLD(child).lb = newTotal;');pb=source.index('        tl_pushes++;',pa);prefix=source[pa:pb];assert (out/'sources/original_push_label_prefix.inc').read_text()==prefix and prefix.replace('TLD(child)','TLD(childRnode)')in golden
 old=(base/'sources/make_inputs.cpp').read_text();oa=old.index('    void golden(');ob=old.index('\n\n\n};',oa);na=cpp.index('    void golden(');nb=cpp.index('\n\n\n};',na)
 assert cpp[na:nb].replace('costGolden(rnode,childRNode,st.connIdx,st.sequence,*cost_out,false);','')==old[oa:ob]
 fixture=(out/'sources/post_decision_fixture_sll_v5.inc').read_text();assert 'auto initial_labels=*Router::tl_sparse' in fixture and 'auto expected_labels=*Router::tl_sparse;*Router::tl_sparse=initial_labels' in fixture and 'e.visited==a.visited&&e.target==a.target'in fixture
 assert sha(out/'vectors.txt')!=bm['artifacts']['vectors.txt']

 params=ROOT/'results/connection_state_inputs_20261025';pm=json.loads((params/'manifest.json').read_text());table=(params/'connections.bin').read_bytes();assert sha(params/'connections.bin')==pm['artifacts']['connections.bin']
 graph=(out/'graph_attrs.rrt32').read_bytes();cost=(out/'cost.bin').read_bytes();owner=(out/'owners.bin').read_bytes();layout=m['cost_layout'];ol=m['owner_layout']
 def owner_at(node,net):
  key,refs,occ,ptr=struct.unpack_from('<IHHI',owner,node*16);count=refs if key==net+1 else 0;seen=set()
  while ptr:
   assert ptr not in seen and 0<ptr<=ol['pool_capacity'];seen.add(ptr);key,ref,ptr,_=struct.unpack_from('<4I',owner,ol['pool_offset']+(ptr-1)*16)
   if key==net+1:count=ref
  return count,occ
 prefixes={}
 for line in(out/'post_vectors.txt').read_text().splitlines():
  v=list(map(int,line.split()));prefixes[tuple(v[:2])]=v
 oracle={}
 for line in(out/'cost_vectors.txt').read_text().splitlines():
  v=line.split();key=tuple(map(int,v[:2]));assert key not in oracle;oracle[key]=[int(x,16)for x in v[2:]]
 assert len(oracle)==len(prefixes)==m['coverage']['allowed']==702
 labels={};last_commit={};origin={};visited_reuse_skips=parent_chain=sll=flips=causal=nonzero=early=0
 expected={};cookie=ci=net=sink=parent=seq=0
 for line in(out/'vectors.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='Q' and int(t[1])==0:labels={};last_commit={};origin={}
  elif t[0]=='L':
   n,f,v=map(int,t[1:]);labels.setdefault(n,[0]*5)[f]=v&0xffffffff
   if f==1:origin[n]='host'
   if f==3:last_commit.pop(n,None)
  elif t[0]=='E':cookie,parent=map(int,t[1:3])
  elif t[0]=='D':ci,sink,net,seq=map(int,t[1:5]);flags=int(t[5]);assert flags&24==0
  elif t[0]=='A' and int(t[4])==0:
   child=int(t[2])
   if last_commit.get(child)==seq:
    assert labels[child][3]==seq;visited_reuse_skips+=1
  elif t[0]=='A' and int(t[4])!=0:
   ordinal,child=map(int,t[1:3]);key=(cookie,ordinal);cfg=list(map(int,t[6:]));p=prefixes[key];assert p[3]==child
   label=labels.setdefault(child,[0]*5);assert label[3]!=seq and p[2]==parent and p[8]==label[2];label[2]=parent
   upstream=labels.get(parent,[0]*5)[1];assert p[6]==upstream
   x=struct.unpack_from('<h',graph,child*32+14)[0];ey=struct.unpack_from('<h',graph,child*32+16)[0];by=struct.unpack_from('<h',graph,child*32+12)[0];is_sll=graph[child*32+8]==5;y=by if is_sll and struct.unpack_from('<h',graph,parent*32+16)[0]==ey else ey
   assert p[4]==x&0xffffffff and p[5]==y&0xffffffff
   cx,cy=struct.unpack_from('<2f',cost,layout['nets_offset']+net*16)
   f32=lambda v:struct.unpack('<f',struct.pack('<f',v))[0]
   center=struct.unpack('<I',struct.pack('<f',f32(abs(f32(f32(x)-cx))+abs(f32(f32(y)-cy)))))[0];assert p[7]==center
   sll+=is_sll;flips+=y!=ey;causal+=is_sll and p[8]==0xffffffff and y!=ey;nonzero+=upstream!=0;early+=bool(int(t[3])&4);parent_chain+=origin.get(parent)=='commit'

   row=struct.unpack_from('<16I',table,ci*64);assert row[1:4]==(ci,net,sink) and row[9]==0 and row[11]==0
   count,occ=owner_at(child,net);idx=occ-bool(count);assert 0<=idx<256
   hist=struct.unpack_from('<I',cost,child*4)[0];price=struct.unpack_from('<I',cost,layout['prices_offset']+idx*4)[0];nw=struct.unpack_from('<4I',cost,layout['nets_offset']+net*16)
   attrs=graph[child*32:(child+1)*32];basecost=struct.unpack_from('<I',attrs,20)[0];length=struct.unpack_from('<h',attrs,18)[0]&0xffffffff
   signed=lambda w:w if w<0x80000000 else w-0x100000000
   distance=abs(p[4]-signed(cfg[8]))+abs(p[5]-signed(cfg[9]))
   packet=[row[5],count,basecost,hist,price,nw[2],p[7],nw[3],p[6],row[6],length,row[7],distance,row[9],row[8]]+[0]*8
   assert oracle[key][:23]==packet,(key,oracle[key][:23],packet);expected[key]=packet
   label[0]=oracle[key][27];label[1]=oracle[key][25];label[3]=seq;last_commit[child]=seq;origin[child]='commit'
 assert set(expected)==set(oracle) and all(c['exit_code']==0 for c in m['commands']) and visited_reuse_skips>0 and sll>0 and causal>0
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'packets':len(expected),'input_words_independently_rebuilt':23*len(expected),'output_words_from_original_CPU_body':5*len(expected),'visited_reuse_skips_from_prior_commits':visited_reuse_skips,'parent_upstream_from_prior_commits':parent_chain,'sll':sll,'postprev_y_differs_from_static':flips,'causal_y_flip_from_minus_one':causal,'nonzero_parent_upstream':nonzero,'early':early,'explicit_geometry_patches':4,'label_snapshot_comparisons':1216,'scope':'Actual three push-label updates alter later scripted access decisions; original candidate control and manual access machine compare all live label words after each parent. CPU original cost body and input images independently rebuilt. Heap/recursive scheduling and full route absent; crossSLR0/landmark inactive and explicit four-node geometry stress.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
