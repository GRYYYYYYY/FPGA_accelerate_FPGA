from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def fl(w):return struct.unpack('<f',struct.pack('<I',w))[0]
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and all(c['exit_code']==0 for c in m['commands'])
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 inp=ROOT/'results/commit_inputs_20261025';assert m['input_manifest_sha256']==sha(inp/'manifest.json') and m['input_audit_sha256']==sha(inp/'source_bound_audit.json')
 text=(inp/'sources/reference/trace.cpp').read_text();a=text.index('    struct DaryPQ {');b=text.index('    std::vector<DaryPQ::E> pqStorage;',a);assert (out/'sources/original_heap.inc').read_text()==text[a:b]
 counts={}
 for name,cm in m['cases'].items():
  heap=[];expected=[];obs=0;active=False;owner=None;peak=0
  def apply(op,key,node,cookie,q,p):
   nonlocal active,owner,peak
   if op==0:assert not active;active=True;owner=(q,p)
   else:assert active and owner==(q,p)
   status=rkey=rid=0
   if op in [0,4,5]:heap.clear()
   elif op==1:
    if len(heap)==65536:status=2
    else:
     k=len(heap);heap.append((key,node))
     while k:
      parent=(k-1)//8
      if fl(heap[parent][0])<=fl(key):break
      heap[k]=heap[parent];k=parent
     heap[k]=(key,node)
   elif op==2:
    if not heap:status=1
    else:
     rkey,rid=heap[0];last=heap.pop();k=0
     if heap:
      while k*8+1<len(heap):
       first=k*8+1;best=first
       for c in range(first+1,min(first+8,len(heap))):
        if fl(heap[c][0])<fl(heap[best][0]):best=c
       if fl(last[0])<=fl(heap[best][0]):break
       heap[k]=heap[best];k=best
      heap[k]=last
   else:assert op==3
   if op==4:active=False;owner=None
   peak=max(peak,len(heap));expected.append((op,key,node,cookie,q,p,status,rkey,rid,len(heap)))
  for line in(out/(name+'_plan.txt')).read_text().splitlines():
   op,key,node,cookie,q,p=map(int,line.split())
   if op==99:
    while heap:apply(2,0,0,0xc0000000|obs,q,p);obs+=1
    apply(2,0,0,0xc0000000|obs,q,p);obs+=1
   else:
    if op==3 and cookie==0xffffffff:cookie=0xc0000000|obs;obs+=1
    apply(op,key,node,cookie,q,p)
  actual=[tuple(map(int,s.split()))for s in(out/(name+'_expected.txt')).read_text().splitlines()];assert actual==expected and len(actual)==cm['expected_rows'] and not heap and not active
  counts[name]={'commands':len(actual),'peak':peak,'poll_success':sum(r[0]==2 and r[6]==0 for r in actual),'poll_empty':sum(r[0]==2 and r[6]==1 for r in actual),'cost_and_seed_offers':sum(r[0]==1 for r in actual)}
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'scope':'Verbatim original CPU8-ary heap plus independent Python replay. Query-end destructive verification only, not router polling/recursive lookahead.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
