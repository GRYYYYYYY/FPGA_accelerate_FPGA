"""Re-read raw bytes independently and check the complete logged AXI/response sequence."""
from pathlib import Path
import hashlib,json,mmap,struct,re,random
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/graph_reader_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 graph=Path(m['graph']);gm=read(graph/'manifest.json');gate=read(graph/'source_bound_audit.json')
 assert gate['status']=='passed'and gate['manifest_sha256']==m['graph_manifest_sha256']==sha(graph/'manifest.json')
 assert sha(graph/'source_bound_audit.json')==m['graph_gate_sha256']
 for name,digest in m['graph_artifacts'].items():assert sha(graph/name)==digest==gm['artifacts'][name]
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for name,digest in m['oracle'].items():assert sha(out/name)==digest
 assert all(x['exit_code']==0 for x in m['commands'])
 fs=[(graph/n).open('rb')for n in ['offsets.u32le','edges.u32le','nodes.rrt32']]
 off,edge,attr=[mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)for f in fs];n=len(attr)//32;e=len(edge)//4
 def word(buf,i):return int.from_bytes(buf[4*i:4*i+4],'little')
 bases=[0x1fffff000,0x10fffff000,0x20fffff000];expected=[];parents=set();children=0;pagebound=set();degrees=set();mod16=set();half=set();duplicate=False
 rows=(out/'vectors.txt').read_text().splitlines()
 cursor=0
 while cursor<len(rows):
  fields=rows[cursor].split();parent=int(fields[1]);assert parent not in parents;parents.add(parent)
  lo=word(off,parent);hi=word(off,parent+1);d=hi-lo;degrees.add(d);mod16.add(parent%16)
  if parent%1024==1023:pagebound.add(parent)
  actual_children=[word(edge,j)for j in range(lo,hi)]
  duplicate|=len(set(actual_children))<len(actual_children)
  for seq in range(d+2):
   f=rows[cursor].split();op,p,index,status,target,first,count=map(int,f[:7]);raw=int(f[7],16);beats=int(f[8]);addresses=[int(v,16)for v in f[9:]]
   wantop=0 if seq==0 else 1;wantindex=max(0,seq-1);bad=seq==d+1
   assert (op,p,index)==(wantop,parent,wantindex)
   wanttarget=0 if bad else parent if seq==0 else actual_children[index]
   wantattrs=0 if bad else int.from_bytes(attr[wanttarget*32:(wanttarget+1)*32],'little')
   assert (status,target,first,count,raw)==(2 if bad else 0,wanttarget,0 if bad else lo,0 if bad else d,wantattrs)
   wantaddr=[bases[0]+(parent//16)*64]
   if parent//16!=(parent+1)//16:wantaddr.append(bases[0]+((parent+1)//16)*64)
   if not bad:
    half.add(wanttarget%2)
    if op:wantaddr.append(bases[1]+((lo+index)//16)*64);children+=1
    wantaddr.append(bases[2]+(wanttarget//2)*64)
   assert beats==len(wantaddr)and addresses==wantaddr+[0]*(4-beats)
   expected.append((wantaddr,status,target,first,count,raw));cursor+=1
 assert pagebound==set(range(1023,n-1,1024))and mod16==set(range(16))and half=={0,1}and duplicate
 assert set(range(128))|set(range(n-128,n))<=parents
 assert set(random.Random(20261024).sample(range(n),1024))<=parents
 coverage=read(out/'coverage.json')
 assert coverage['queries']==len(expected)and coverage['sampled_nodes']==len(parents)and coverage['child']==children
 assert set(map(int,coverage['degree_representatives']))==degrees
 assert coverage['axi_beats']==sum(len(x[0])for x in expected)
 results={}
 for case,cm in m['cases'].items():
  assert cm['status']=='passed'and all(x['exit_code']==0 for x in cm['commands'])
  d=out/case
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
  assert log.count(cm['result'])==1
  numbers={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])}
  cases=expected[:200]if case=='pilot'else expected
  assert numbers['queries']==len(cases)and numbers['checks']==len(cases)+22 and numbers['faults']==19 and numbers['configurations']==28 and numbers['AR']==numbers['R']and numbers['blocked']>0
  with (d/'axi_trace.txt').open()as trace:
   beats=0
   for q,(addresses,status,target,first,count,raw)in enumerate(cases,5):
    for address in addresses:
     assert trace.readline().strip()==f'A {q} {address:016x}';beats+=1
    assert trace.readline().strip()==f'R {q} {status} {target} {first} {count} {raw:064x}'
   assert trace.read()==''
  assert numbers['AR']==beats+38
  results[case]={**numbers,'audited_real_axi_beats':beats,'trace_sha256':sha(d/'axi_trace.txt')}
 for mm in (off,edge,attr):mm.close()
 for f in fs:f.close()
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'coverage':coverage,'cases':results,'scope':m['scope'],'limitations':['Sampled RTL queries, not exhaustive hardware traversal of all graph nodes/edges.','Zero padding of partial final beats is the memory model contract.','No graph/build/pager system integration or platform/board validation.']}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
