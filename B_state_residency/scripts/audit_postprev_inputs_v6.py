from pathlib import Path
import hashlib,json,struct,sys,mmap
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and m['force_has_laguna_for_SLL_stress']
 dep=ROOT/'results/candidate_occupied_inputs_v2_20261025';dm=json.loads((dep/'manifest.json').read_text());assert m['base_gate_sha256']==sha(dep/'source_bound_audit.json') and m['base_manifest_sha256']==sha(dep/'manifest.json')
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 for n,h in dm['sources'].items():
  if n!='make_inputs.cpp':assert sha(out/'sources'/n)==h
 for n in ['owners.bin','cost.bin']:assert sha(out/n)==dm['artifacts'][n]
 # The entire original golden body stays byte-identical except the explicitly replaced cost hook.
 old=(dep/'sources/make_inputs.cpp').read_text();new=(out/'sources/make_inputs.cpp').read_text()
 a=old.index('    void golden(');b=old.index('\n\n\n};',a)
 aa=new.index('    void golden(');bb=new.index('\n\n\n};',aa)
 assert new[aa:bb].replace('prefixes.push_back(preparePrefix(rnode,childRNode,c.netIdx));','')==old[a:b]
 assert 'check(manual_prefix==r.prefixes)'in(out/'sources/post_decision_fixture_sll_v5.inc').read_text()
 for n in ['initial_design.bin','expected_design.bin']:assert (out/n).stat().st_size==145424192
 assert all(c['exit_code']==0 for c in m['commands']) and 'EXPANSION_INPUTS_PASS'in(out/'execute.log').read_text()
 rows=[tuple(map(int,line.split()))for line in(out/'post_vectors.txt').read_text().splitlines()]
 cost=(out/'cost.bin').read_bytes();no=m['cost_layout']['nets_offset'];labels={};expected=[];parent=net=cookie=0;sll=flips=nonzero=early_count=causal=0
 with (ROOT/'results/graph_image_20261024/nodes.rrt32').open('rb')as f:
  graph=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
  for line in (out/'vectors.txt').read_text().splitlines():
   r=line.split()
   if r[0]=='Q' and int(r[1])==0:labels={}
   elif r[0]=='L':
    node,field,value=map(int,r[1:]);labels.setdefault(node,[0]*5)[field]=value&0xffffffff
   elif r[0]=='E':cookie,parent=map(int,r[1:3])
   elif r[0]=='D':net=int(r[3])
   elif r[0]=='A' and int(r[4])!=0:
    ordinal,child,flags=map(int,r[1:4]);label=labels.setdefault(child,[0]*5);old_prev=label[2];label[2]=parent
    x=struct.unpack_from('<h',graph,child*32+14)[0];end_y=struct.unpack_from('<h',graph,child*32+16)[0];begin_y=struct.unpack_from('<h',graph,child*32+12)[0]
    is_sll=graph[child*32+8]==5;parent_y=struct.unpack_from('<h',graph,parent*32+16)[0];y=begin_y if is_sll and parent_y==end_y else end_y
    upstream=labels.get(parent,[0]*5)[1];cx,cy=struct.unpack_from('<2f',cost,no+net*16)
    distance=bits(f32(abs(f32(f32(x)-cx))+abs(f32(f32(y)-cy))))
    expected.append((cookie,ordinal,parent,child,x&0xffffffff,y&0xffffffff,upstream,distance,old_prev,int(bool(flags&4))))
    sll+=is_sll;flips+=y!=end_y;causal+=is_sll and old_prev==0xffffffff and y!=end_y;nonzero+=upstream!=0;early_count+=bool(flags&4)
  graph.close()
 assert rows==expected and len(rows)==m['coverage']['allowed']
 assert sll>0 and flips>0 and causal>0 and nonzero>0
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'post_prefixes':len(rows),'sll':sll,'postprev_y_differs_from_static':flips,'causal_y_flip_from_minus_one':causal,'nonzero_parent_upstream':nonzero,'early':early_count,'scope':'Fresh original CPU decision/control prefix plus independent raw graph/label journal and binary32-stage center reconstruction; no full cost or recursive expansion'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
