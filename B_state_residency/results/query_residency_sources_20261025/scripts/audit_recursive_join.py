"""Source-bound original-CPU / causal recursion / complete byte transcript audit."""
from pathlib import Path
import hashlib,json,re,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def words(n,count):return [(n>>(32*i))&0xffffffff for i in range(count)]
def packed(v):return sum(x<<(32*i)for i,x in enumerate(v))
def replay(path,regions,final=None):
 buffers=[bytearray(p.read_bytes())if isinstance(p,Path)else bytearray(p)for _,p in regions];pending=[];reads=writes=bs=requests=0
 for line in path.read_text().splitlines():
  t=line.split()
  if t[0]=='A':
   assert not pending;requests+=1;address=int(t[1],16);length=int(t[2]);assert 1<=length<=3;pending=[address+64*i for i in range(length)]
  elif t[0]=='B':assert t==['B','0'];bs+=1
  else:
   address=int(t[1],16);choices=[(i,address-base)for i,(base,_)in enumerate(regions)if base<=address<base+len(buffers[i])];assert len(choices)==1
   idx,offset=choices[0];assert offset%64==0 and offset+64<=len(buffers[idx]);buf=buffers[idx]
   if t[0]=='R':
    assert pending and pending.pop(0)==address and t[3]=='0';assert int(t[2],16).to_bytes(64,'little')==buf[offset:offset+64];reads+=1
   else:
    assert t[0]=='W' and final is not None
    mask=int(t[2],16);assert mask==2**64-1 if path.name=='label_axi.txt' else mask in [0xffff<<(16*i)for i in range(4)]
    data=int(t[3],16).to_bytes(64,'little');assert mask
    for j in range(64):
     if mask>>j&1:buf[offset+j]=data[j]
    writes+=1
 assert not pending
 if final is None:assert not writes and not bs
 else:assert len(buffers)==1 and bytes(buffers[0])==final.read_bytes()
 if path.name=='label_axi.txt':assert writes==3*bs and reads==3*requests
 return {'read_transactions':requests,'read_beats':reads,'write_beats':writes,'write_replies':bs,'bytes_checked':sum(map(len,buffers))}
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,v in m['sources'].items():assert sha(out/'sources'/n)==v['sha256']==sha(Path(v['path'])),n
 inp=Path(m['input']);im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());assert ig['status']==im['status']=='passed'and ig['manifest_sha256']==sha(inp/'manifest.json')==m['input_manifest_sha256']
 base=ROOT/'results/candidate_recursive_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());assert sha(base/'manifest.json')==m['base_manifest_sha256']and sha(base/'source_bound_audit.json')==m['base_audit_sha256']
 same=0
 for n,v in m['sources'].items():
  if n in ['runner.py','tb_recursive_join.sv']:continue
  assert n in bm['sources']and v['sha256']==bm['sources'][n]['sha256'];same+=1
 assert same>90
 cpu=[]
 for l in(inp/'cost_vectors.txt').read_text().splitlines():
  t=l.split();cpu.append((int(t[0])*8,int(t[1])*8,[int(x,16)for x in t[2:25]],[int(x,16)for x in t[25:]]))
 final={int(t[0]):[int(x,16)for x in t[1:]]for t in(l.split()for l in(inp/'final_labels.txt').read_text().splitlines())}
 counts={}
 for case,cm in m['cases'].items():
  assert case in ['full','pressure'] and cm['status']=='passed'and len(cm['commands'])==3 and all(c['exit_code']==0 for c in cm['commands'])
  assert ('PRESSURE'in cm['commands'][0]['argv'])==(case=='pressure')
  d=out/case
  for n,h in cm['artifacts'].items():assert sha(d/n)==h,n
  log=(d/'simulate.log').read_text();assert cm['result']in log and 'Fatal:'not in log and '$finish called'in log
  c={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert (c['outputs'],c['commits'],c['offers'],c['expands'],c['visited_reads'])==(3,2,1,2,3)and c['host_blocks']>0
  rows=[l.split()for l in(d/'joined_trace.txt').read_text().splitlines()];assert all(int(a[1])<=int(b[1])for a,b in zip(rows,rows[1:]))
  by=lambda tag:[t for t in rows if t[0]==tag]
  E,S,M,V,O,C,W,A,F,R,FQ,FR=[by(tag)for tag in ['E','S','M','V','O','C','W','A','F','R','FQ','FR']]
  assert [[int(x)for x in t[2:]]for t in E]==[[100,0],[101,8]]
  assert [[int(x)for x in t[2:]]for t in S]==[[100,2],[101,1]]
  assert [[int(x)for x in t[2:]]for t in M]==[[100,0,8],[101,8,16],[100,0,16]]
  assert [[int(x)for x in t[2:]]for t in O]==[[100,0,8,2,0],[101,8,16,1,0],[100,0,16,0,1]]
  assert int(E[0][1])<int(S[0][1])<int(M[0][1])<int(O[0][1])<int(E[1][1])<int(S[1][1])<int(M[1][1])<int(O[1][1])<int(M[2][1])<int(O[2][1])
  assert len(V)==3 and [int(t[2])for t in V]==[8,16,16]and all(t[3]=='0'for t in V)
  assert words(int(V[0][4],16),5)==[0,0,0xffffffff,0,0]and words(int(V[1][4],16),5)==[0,0,0xffffffff,0,0]
  assert words(int(V[2][4],16),5)==final[16]and int(M[2][1])<int(V[2][1])<int(O[2][1])
  assert len(C)==2
  for t,(p,n,packet,result)in zip(C,cpu):assert int(t[2])==n and words(int(t[3],16),23)==packet and words(int(t[4],16),5)==result
  expected_w=[];expected_a=[]
  for p,n,packet,result in cpu:
   label=[0,0,p,0,0]
   for field,value in [(0,result[4]),(1,result[2]),(3,77)]:
    expected_w.append([n,field,value]);label[field]=value;expected_a.append(packed(label))
  assert [[int(t[2]),int(t[3]),int(t[4],16)]for t in W]==expected_w
  assert len(A)==6 and all(t[2:4]==['0','1']for t in A)and[int(t[4],16)for t in A]==expected_a
  for i in range(6):
   assert int(W[i][1])<int(A[i][1])
   if i<5:assert int(A[i][1])<int(W[i+1][1])
  assert int(A[2][1])<int(O[0][1]) and int(A[5][1])<int(F[0][1])<int(O[1][1])<int(V[2][1])
  assert len(F)==1 and F[0][2:]==['16','4089999a','0']
  assert {int(t[2]):words(int(t[3],16),5)for t in R}==final and len(R)==5
  assert min(int(t[1])for t in R)>int(O[-1][1])
  assert [int(t[2])for t in FQ]==[0,1,2,2,4]and len(FR)==5
  assert [[int(t[2]),int(t[3],16),int(t[4]),int(t[5])]for t in FR]==[[0,0,0,0],[0,0,0,1],[0,cpu[1][3][4],16,0],[1,0,0,0],[0,0,0,0]]
  assert int(FQ[1][3],16)==cpu[1][3][4]and int(FQ[1][4])==16
  assert int(FQ[-1][1])>max(int(t[1])for t in R)
  memory={}
  for tag,regions,expected in [
   ('graph',[(0x1fffff000,inp/'offsets.u32le'),(0x10fffff000,inp/'edges.u32le'),(0x20fffff000,inp/'nodes.rrt32')],None),
   ('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),
   ('label',[(0,bytes(3145728))],d/'labels.bin'),
   ('owner',[(0x61fffff000,inp/'owners.bin')],None),
   ('cost',[(0x71fffff000,inp/'cost.bin')],None),
   ('qstate',[(0x81fffff000,inp/'connections.bin')],None),
   ('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]:memory[tag]=replay(d/(tag+'_axi.txt'),regions,expected)
  assert sha(d/'design.bin')==sha(inp/'expected_design.bin')and sha(d/'owners.bin')==sha(inp/'owners.bin')and sha(d/'cost.bin')==sha(inp/'cost.bin')
  assert memory['label']['read_transactions']==c['label_reads']and memory['label']['write_replies']==c['label_writes']
  assert memory['qstate']['read_beats']==1 and memory['table']['read_beats']==0
  counts[case]={**c,'actual_CPU_cost_words_checked':56,'ordered_native_cost_ACKs':6,'final_native_records':5,'memory':memory}
 assert counts['pressure']['label_reads']>counts['full']['label_reads']and counts['pressure']['label_writes']>counts['full']['label_writes']
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'input_audit_sha256':sha(inp/'source_bound_audit.json'),'unchanged_baseline_RTL_dat':same,'counts':counts,'scope':m['scope'],'limitations':['No natural-route trace, board timing/performance, landmark, nonzero owner or joined failure/recovery proof.','One convergent synthetic recursive path, no target EARLY in this joined test.','Query-end polls are verification fixtures, not a complete routing search.']}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
