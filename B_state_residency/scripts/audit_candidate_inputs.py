"""Bind CPU fixture sources and verify every Config14 static field against raw graph."""
from pathlib import Path
import hashlib,json,struct,mmap,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def audit(out):
 m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,digest in m['sources'].items():assert sha(out/'sources'/n)==digest
 for n,digest in m['artifacts'].items():assert sha(out/n)==digest
 dep=ROOT/'results/expansion_inputs_20261024';assert sha(dep/'manifest.json')==m['input_manifest_sha256']
 assert sha(ROOT/'data/derived/logicnets_jscl.rrt')==m['input_rrt_sha256']
 original=(out/'sources/reference/trace.cpp').read_text();a=original.index('    void exploreAndExpand(State& st, int rnode) {');b=original.index('    // ----------------------------------------------------------------- rip up / save',a)
 expected=original[a:b].replace('void exploreAndExpand(','void golden(').replace('evaluateCostAndPush(st, rnode, childRNode, lookahead);','selected.emplace_back(childRNode,lookahead,st.earlyTermination);')
 assert expected in(out/'sources/make_inputs.cpp').read_text()
 graph=ROOT/'results/graph_image_20261024';counts={'expansions':0,'cache_hits':0,'children':0,'decisions':0,'allowed':0,'early':0,'pruned':0,'config_words':0};e=None;kids=[];decisions=[];d=None
 with (graph/'nodes.rrt32').open('rb')as f:
  attrs=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
  def node(n):return struct.unpack_from('<i4xBBhhhh',attrs,n*32)
  def u(v):return v&0xffffffff
  for line in (out/'vectors.txt').read_text().splitlines():
   row=line.split();kind=row[0];v=list(map(int,row[1:]))
   if kind=='E':
    assert e is None;e=v;kids=[];decisions=[];d=None;counts['expansions']+=1;counts['cache_hits']+=v[4]
   elif kind=='C':assert e is not None;kids.append(v);counts['children']+=1
   elif kind=='D':assert d is None;d=v;assert len(kids)==e[7]
   elif kind=='A':
    assert e is not None and d is not None;ordinal,child,bits,action,services,*cfg=v;assert len(cfg)==14
    assert ordinal==len(decisions)and kids[ordinal][1]==child and not any(x[2]&4 for x in decisions)
    assert action in [0,1,2]and services>=1 and bits<16
    _,parent,prune,haslag,hit,raw,mask,nkids=e;ci,sink,net,seq,flags,xmin,xmax,ymin,ymax=d
    ct,ctype,cflags,cbx,cby,cex,cey=node(child);pt,ptype,pflags,*_=node(parent);st,stype,sflags,sbx,sby,sex,sey=node(sink)
    staticflags=flags|(32 if pflags&2 else 0)|(64 if cflags&2 else 0)|(128 if cflags&128 else 0)
    assert cfg[1]&~2==staticflags
    expected=[seq,cfg[1],ctype,ptype,stype,u(cex),u(ct),u(st),u(sbx),u(sby),u(xmin),u(xmax),u(ymin),u(ymax)]
    assert cfg==expected,(e[0],ordinal,cfg,expected)
    decisions.append(v);counts['decisions']+=1;counts['allowed']+=action!=0;counts['early']+=bool(bits&4);counts['pruned']+=bool(bits&8);counts['config_words']+=14
   elif kind=='Z':
    assert v==[sum(x[3]!=0 for x in decisions),int(any(x[2]&4 for x in decisions)),sum(bool(x[2]&8)for x in decisions)]
    assert len(decisions)==len(kids)or(decisions and decisions[-1][2]&4)
    assert len({x[0]for x in kids})==len(kids)and sum(1<<x[0]for x in kids)==e[6]
    e=None
   else:assert kind in ['Q','L']
  attrs.close()
 assert e is None
 for key in ['decisions','allowed','early','pruned']:assert counts[key]==m['coverage'][key]
 result={'status':'passed','scope':'Source/artifact binding, original CPU decision-body substitution, raw graph static Config14 and stream/count checks; dynamic dead correctness relies on CPU fixture oracle; no RTL result','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':audit(Path(sys.argv[1]).resolve())
