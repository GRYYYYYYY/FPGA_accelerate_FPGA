from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 base=ROOT/'results/postprev_inputs_v7_20261025';bm=json.loads((base/'manifest.json').read_text());assert m['base_manifest_sha256']==sha(base/'manifest.json') and m['base_gate_sha256']==sha(base/'source_bound_audit.json')
 for n in ['vectors.txt','post_vectors.txt','initial_design.bin','expected_design.bin','cost.bin','owners.bin','graph_attrs.rrt32']:assert m['artifacts'][n]==bm['artifacts'][n]
 source=(out/'sources/reference/trace.cpp').read_text();a=source.index('    void evaluateCostAndPush(State& st, int rnode, int childRnode, bool lookahead) {');b=source.index('\n    void exploreAndExpand',a);method=source[a:b]
 assert (out/'sources/original_cost_method.inc').read_text()==method
 body=method[method.index('        int countSourceUses'):method.index('        push(st, childRnode, newPartial, newTotal, lookahead);')]
 cpp=(out/'sources/make_inputs.cpp').read_text();a=cpp.index('    void costGolden(');b=cpp.index('std::vector<std::tuple<int,bool,bool>> selected;',a);golden=cpp[a:b];assert body in golden
 ia=source.index('        st.shareWeight = std::pow(1.0f, cfg.shareExponent);');ib=source.index('        st.earlyTermination = false;',ia)
 assert (out/'sources/original_state_initializer.inc').read_text()==source[ia:ib] and source[ia:ib] in golden
 assert 'push(st,' not in golden and '.lb ='not in golden and '.visited ='not in golden
 params=ROOT/'results/connection_state_inputs_20261025';pm=json.loads((params/'manifest.json').read_text());table=(params/'connections.bin').read_bytes();assert sha(params/'connections.bin')==pm['artifacts']['connections.bin']
 graph=(out/'graph_attrs.rrt32').read_bytes();cost=(out/'cost.bin').read_bytes();owner=(out/'owners.bin').read_bytes();layout=bm['cost_layout'];ol=bm['owner_layout']
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
 assert len(oracle)==len(prefixes)==713
 expected={};cookie=ci=net=sink=0
 for line in(out/'vectors.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='E':cookie=int(t[1])
  elif t[0]=='D':ci,sink,net=map(int,t[1:4]);flags=int(t[5]);assert flags&24==0
  elif t[0]=='A' and int(t[4])!=0:
   ordinal,child=map(int,t[1:3]);key=(cookie,ordinal);cfg=list(map(int,t[6:]));p=prefixes[key];assert p[3]==child
   row=struct.unpack_from('<16I',table,ci*64);assert row[1:4]==(ci,net,sink) and row[9]==0 and row[11]==0
   count,occ=owner_at(child,net);idx=occ-bool(count);assert 0<=idx<256
   hist=struct.unpack_from('<I',cost,child*4)[0];price=struct.unpack_from('<I',cost,layout['prices_offset']+idx*4)[0];nw=struct.unpack_from('<4I',cost,layout['nets_offset']+net*16)
   attrs=graph[child*32:(child+1)*32];basecost=struct.unpack_from('<I',attrs,20)[0];length=struct.unpack_from('<h',attrs,18)[0]&0xffffffff
   signed=lambda w:w if w<0x80000000 else w-0x100000000
   distance=abs(p[4]-signed(cfg[8]))+abs(p[5]-signed(cfg[9]))
   packet=[row[5],count,basecost,hist,price,nw[2],p[7],nw[3],p[6],row[6],length,row[7],distance,row[9],row[8]]+[0]*8
   assert oracle[key][:23]==packet,(key,oracle[key][:23],packet);expected[key]=packet
 assert set(expected)==set(oracle) and all(c['exit_code']==0 for c in m['commands'])
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'packets':len(expected),'input_words_independently_rebuilt':23*len(expected),'output_words_from_original_CPU_body':5*len(expected),'scope':'Original cost calculation before push; actual nonzero initial State weights, immutable image reads and post-prev coordinates; landmark inactive/crossSLR0 profile. No cost label commits/recursive search or live full-route costs.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
