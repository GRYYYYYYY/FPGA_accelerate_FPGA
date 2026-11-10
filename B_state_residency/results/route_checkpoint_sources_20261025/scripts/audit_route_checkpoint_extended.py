"""Independent CRC/slot/path/physical-reference audit of route checkpoint units."""
from pathlib import Path
from collections import Counter
import hashlib,json,struct,mmap,sys,importlib.util,zlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def mod(p,name):
 sp=importlib.util.spec_from_file_location(name,p);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed';capacity=m['max_path'];stride=capacity+7;words=stride*2
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 b=mod(out/'sources/build.py','cp_build');b.BASE=out/'sources/base_controller.sv';assert b.make()==(out/'sources/route_commit_controller.sv').read_text()
 tb=mod(out/'sources/build_tb.py','cp_tb');tb.BASE=out/'sources/base_tb.sv';assert tb.make(capacity)==(out/'sources/tb_route_commit.sv').read_text()
 assert sha(out/'sources/base_controller.sv')==sha(ROOT/'results/recovery_retry_normal_v1/sources/route_commit_controller.sv') and sha(out/'sources/base_tb.sv')==sha(ROOT/'hardware/variants/route_commit_v1/tb_route_commit.sv')
 log=(out/'simulate.log').read_text();assert 'ROUTE_CHECKPOINT_PASS checks=31 cp=27'in log and 'Fatal:'not in log and '$finish called'in log
 expected=[];paths=[]
 for phase,(capture,sink)in enumerate(zip(m['captures'],[150697,128009])):
  p=Path(capture);assert sha(p/'source_bound_audit.json')==m['captures'][capture];chain=[]
  with(p/'search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
   node=sink
   while node!=0xffffffff:
    assert node not in chain;chain.append(node);v=struct.unpack_from('<11I',mm,node*44);vals=[v[0],v[1],v[3],v[4],v[5]];expected.append([str(phase),str(node),f'{sum(x<<(32*j)for j,x in enumerate(vals)):040x}']);node=v[3]
  paths.append(chain[1:-1])
 assert list(map(str.split,(out/'labels.txt').read_text().splitlines()))==expected
 rows=[t.split()for t in(out/'events.txt').read_text().splitlines()]
 R=[[int(v)for v in t[1:]]for t in rows if t[0]=='R']
 old=[[0,0,6,6],[0,1,0,0],[0,0,6,6],[0,1,0,0],[0,1,0,0],[0,0,6,6],[0,0,6,6],[1,2,1,0],[2,2,6,0],[3,4,0,0],[4,4,0,0],[9,3,capacity,0],[5,5,6,1],[10,6,0,0],[10,6,6,1],[8,6,0,0],[10,6,0,0],[10,6,6,1],[11,6,0,0],[12,6,0,0],[13,6,0,0],[14,6,0,0],[15,0,0,0],[15,0,0,0],[16,0,6,6]]
 assert R==old+[[0,0,6,6]]*6
 cr=[t for t in rows if t[0]=='CPR'];assert len(cr)==27 and list(map(lambda t:int(t[1]),cr))==list(range(27))
 statuses=[0]+[1]*11+[0,1,2,0,2,1,1,0,0,0]+[0,0,1,0,0];slots=[3]+[0]*11+[3,3,1,1,1,1,1,1,0,0]+[1,1,1,1,0]
 assert [int(t[2])for t in cr]==statuses and [int(t[4])for t in cr]==slots
 def image(valid):
  a=[]
  for slot in range(2):
   if slot not in valid:a += [0]*stride
   else:a += [1,6,2717,65185,[150697,128009][slot],0x9abcdef0,0x12345678]+paths[slot]+[0]*(capacity-6)
  return a
 def crc(a):return zlib.crc32(struct.pack('<'+'I'*len(a),*a))
 exported={}
 full_image=[1,capacity,2717,100,200,0x9abcdef0,0x12345678]+list(range(1000,1000+capacity))+[0]*stride
 for cid,want in [(23,full_image),(25,full_image),(0,image({0,1})),(15,image({0})),(16,image({0})),(20,image(set()))]:
  stream=[t for t in rows if t[0]=='CPO'and int(t[1])==cid];assert len(stream)==words
  assert [int(t[2])for t in stream]==list(range(words)) and [int(t[3],16)for t in stream]==want and [int(t[4])for t in stream]==[0]*(words-1)+[1]
  assert int(cr[cid][3],16)==crc(want);exported[cid]=crc(want)
 # Each complete input is independently CRC'd and matched to the command.
 batches=[];current=None
 for t in rows:
  if t[0]=='CPC':
   current=dict(id=int(t[1]),restore=int(t[2]),design=int(t[3],16),nodes=int(t[4]),nets=int(t[5]),expected_crc=int(t[6],16),stream=[]);batches.append(current)
  elif t[0]=='CPI':assert current and int(t[1])==current['id'];current['stream'].append((int(t[2]),int(t[3],16),int(t[4])))
 assert len(batches)==28 and [b['id']for b in batches]==list(range(19))+[19,19,20,21,22,23,24,25,26]
 complete={}
 for b in batches:
  i=b['id'];ss=b['stream']
  if not b['restore']:continue
  if i in [2,3]:assert len(ss)==4;assert ss[-1][0]==(4 if i==2 else 3) and ss[-1][2]==int(i==3)
  elif i==14:assert len(ss)==3 and statuses[i]==2
  elif i==19 and len(ss)==5:assert [x[0]for x in ss]==list(range(5))
  else:
   assert len(ss)==words and [x[0]for x in ss]==list(range(words)) and [x[2]for x in ss]==[0]*(words-1)+[1]
   values=[x[1]for x in ss];computed=crc(values);assert int(cr[i][3],16)==computed
   assert (computed!=b['expected_crc'])==(i==1);complete[i]=values
 for cid in list(range(4,12))+[13]:
  want=image({0,1})
  pos,value={4:(0,2),5:(1,capacity+1),6:(2,27960),7:(3,9089009),8:(5,0),9:(8,want[7]),10:(7,want[4]),11:(14,1),13:(1,capacity+1)}[cid]
  want[pos]=value;assert complete[cid]==want
 assert Counter(int(t[1])for t in rows if t[0]=='CPRESET')=={1:3,19:3}
 duplicate=full_image.copy();duplicate[7+capacity-1]=duplicate[7]
 assert complete[22]==full_image and complete[24]==duplicate and complete[26]==image(set())
 assert complete[12]==image({0,1}) and complete[19]==image({0}) and complete[21]==image(set())
 # Reconstruct owner operations across the checkpoint reset and successful
 # restore: INC q1/q2, DEC q1/q2; shared refs move 2->1->0 with no label reads.
 start=next(i for i,t in enumerate(rows)if t[0]=='CPR'and t[1]=='0');end=next(i for i,t in enumerate(rows)if t[0]=='CPR'and t[1]=='14')
 middle=rows[start+1:end]
 counts=Counter(paths[0]+paths[1]);ops=[]
 for path in paths:
  for node in path:counts[node]-=1;ops.append([2,node,counts[node]])
 actual=[[int(v)for v in t[2:]]for t in middle if t[:2]==['O','0']];assert actual[:12]==ops and not any(counts.values())
 cp13=next(i for i,t in enumerate(rows)if t[0]=='CPR'and t[1]=='13');rips=[]
 for t in rows[cp13+1:]:
  if t[0]=='L':break
  if t[0]=='O':rips.append(t)
 assert len(rips)==12
 last19=next(i for i,t in enumerate(rows)if t[0]=='CPR'and t[1]=='19');last20=next(i for i,t in enumerate(rows)if t[0]=='CPR'and t[1]=='20');suffix=rows[last19+1:last20]
 assert not any(t[0]=='L'for t in suffix) and [[int(v)for v in t[2:]]for t in suffix if t[0]=='O']==[[2,n,0]for n in paths[0]]
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),max_path=capacity,route_checks=31,checkpoint_checks=27,old_regression_checks=25,words_per_image=words,crc32={str(k):f'{v:08x}'for k,v in exported.items()},paths=paths,scope='Saved-route component only; real CPU path/labels with registered mock owner/label backends. CRC/order/last/semantic validation, atomic replacement, shared-reference ripup after controller reset, interrupted input/export and partial-reset staging verified. Full-capacity synthetic path import/export and final-node duplicate rejection also checked. External cp_safe, topology and matching owner/checkpoint authority are trusted. No system fence/AXI checkpoint integration or full checkpoint claim.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
