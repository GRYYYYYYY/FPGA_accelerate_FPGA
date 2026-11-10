"""Full snapshot lifecycle audit; observed CPU state, no hardware speed claim."""
from pathlib import Path
import json,struct,mmap,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def meta(p):return {x.split()[0]:list(map(int,x.split()[1:])) for x in (p/'state.txt').read_text().splitlines()}
def rows(p):
 f=p.open('rb');m=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ);return f,m

def analyze(p):
 a=json.loads((p/'source_bound_audit.json').read_text());assert a['status']=='passed'
 s=meta(p);n=s['nodes'][0];f,m=rows(p/'initial_nodes.u32')
 overflow={};last=None
 for node,net,refs in struct.iter_unpack('<III',(p/'initial_overflow.u32').read_bytes()):
  assert node<n and refs>0 and net!=0xffffffff
  key=(node,net);assert last is None or last<key;last=key
  assert struct.unpack_from('<I',m,node*44+24)[0]!=net
  overflow[node]=overflow.get(node,0)+1
 stats=dict(old_visited=0,nondefault_prev=0,historical_above_one=0,occupied_nodes=0,primary_references=0,multinet_nodes=0,created_nodes=0)
 for node,v in enumerate(struct.iter_unpack('<11I',m)):
  stats['old_visited']+=v[4]!=0 and v[4]!=s['sequence'][0]
  stats['nondefault_prev']+=v[3]!=0xffffffff
  stats['historical_above_one']+=v[2]>1065353216
  assert v[2]>=1065353216
  extra=overflow.get(node,0);assert v[8]==(v[6]!=0xffffffff)+extra,(node,'distinct net occupancy')
  assert (v[6]==0xffffffff)==(v[7]==0)
  stats['occupied_nodes']+=v[8]>0;stats['primary_references']+=v[7];stats['multinet_nodes']+=v[8]>1;stats['created_nodes']+=v[9]!=0
 cache=(p/'initial_caches.u32').read_bytes();pos=0;parents=set();edges=0
 while pos<len(cache):
  parent,count=struct.unpack_from('<II',cache,pos);pos+=8
  assert parent<n and parent not in parents;parents.add(parent)
  assert pos+count*4<=len(cache)
  for child, in struct.iter_unpack('<I',cache[pos:pos+count*4]):assert child<n
  pos+=count*4;edges+=count
 assert pos==len(cache)
 stats.update(cache_parents=len(parents),cache_children=edges,overflow_records=(p/'initial_overflow.u32').stat().st_size//12,overflow_nodes=len(overflow))
 m.close();f.close();return dict(audit_sha256=sha(p/'source_bound_audit.json'),state=s,statistics=stats)

def transition(q1,q2):
 s1=meta(q1);s2=meta(q2);assert s1['net']==s2['net'] and s1['sequence']==[1] and s2['sequence']==[2]
 f,a=rows(q1/'search_final_nodes.u32');g,b=rows(q2/'initial_nodes.u32');assert len(a)==len(b)
 def row(m,i):return list(struct.unpack_from('<11I',m,i*44))
 chain=[];node=s1['sink'][0]
 while node!=0xffffffff:
  assert node not in chain;chain.append(node);node=row(a,node)[3]
 assert chain[-1]==s1['source'][0]
 expected={}
 for node in chain[1:-1]:
  v=expected.setdefault(node,row(a,node));assert v[6] in (0xffffffff,s1['net'][0])
  if v[6]==0xffffffff:v[6]=s1['net'][0];v[8]+=1
  v[7]+=1
 for node in s1['targets']:expected.setdefault(node,row(a,node))[5]=0
 for node in s2['targets']:expected.setdefault(node,row(a,node))[5]=1
 v=expected.setdefault(s2['source'][0],row(a,s2['source'][0]));v[0]=0;v[1]=0;v[4]=2
 differing=[]
 stride=44*16384
 for start in range(0,len(a),stride):
  aa=a[start:start+stride];bb=b[start:start+stride]
  if aa==bb:continue
  for off in range(0,len(aa),44):
   if aa[off:off+44]==bb[off:off+44]:continue
   node=(start+off)//44;assert row(b,node)==expected.get(node,row(a,node)),node;differing.append(node)
 for node,v in expected.items():assert row(b,node)==v,node
 assert (q1/'prices.u32').read_bytes()==(q2/'prices.u32').read_bytes()
 a.close();b.close();f.close();g.close()
 return dict(status='passed',path_sink_to_source=chain,interior_committed_nodes=chain[1:-1],changed_rows=differing,full_snapshot_rows_verified=s1['nodes'][0],scope='Exact entire-node transition: query1 backtrace owner commit/target cleanup, query2 target setup/source push; no intervening global label reset.')
if __name__=='__main__':
 p2=BASE/'followup_q2_v1';pi=BASE/'followup_iter2_v1';q1=ROOT/'results/natural_query_v2'
 out=dict(status='passed',auditor_sha256=sha(Path(__file__)),queries={'q2':analyze(p2),'iteration2':analyze(pi)},same_net_transition=transition(q1,p2),scope='CPU natural lifecycle evidence. Existing-query snapshots and full source-bound route identity. No unknown-page hardware initialization or board performance proof.')
 target=ROOT/'results/followup_lifecycle_20261025.json';target.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
