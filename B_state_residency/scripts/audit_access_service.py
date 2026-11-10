from pathlib import Path
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,s in m['sources'].items():assert sha(out/'sources'/n)==s['sha256']==sha(Path(s['path']))
 for n,h in m['gates'].items():assert sha(Path(n))==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 unit=ROOT/'results/search_access_unit_v3_20261024';assert sha(out/'vectors.txt')==m['vectors_sha256']==sha(unit/'vectors.txt')
 assert all(c['exit_code']==0 for c in m['commands']);log=(out/'simulate.log').read_text();assert m['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
 cnt={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',m['result'])};k=svc=case_steps=0;case_id=-1;requests={};actions={0:0,1:0,2:0};early=pruned=0;pending=None;lasttoken=0
 with (out/'observed.txt').open()as obs,(out/'vectors.txt').open()as vectors:
  def expect(parts):assert obs.readline().split()==list(map(str,parts)),parts
  for line in vectors:
   r=line.split();idx,cid=map(int,r[:2]);x=list(map(lambda s:int(s,16),r[2:22]));y=list(map(lambda s:int(s,16),r[22:]))
   if x[0]==0:
    assert pending is None and cid==case_id+1;case_id=cid;case_steps=0
   else:
    assert pending and cid==case_id
    kind,phase,node=pending;rr=obs.readline().split();assert rr[:6]==list(map(str,['S',cid,kind,phase,node,0])) and int(rr[6])>lasttoken and int(rr[7],16)==x[5]
    lasttoken=int(rr[6]);svc+=1;requests[kind]=requests.get(kind,0)+1;pending=None
   expect(['K',idx,cid,f'{sum(v<<(32*i)for i,v in enumerate(y)):048x}']);k+=1;case_steps+=1
   if y[4]:pending=(y[4],y[1],2 if y[4]==8 else 0 if y[4]==9 else y[3]if y[4]==10 else 1)
   else:
    expect(['D',cid,y[2],y[5],case_steps,case_steps-1]);actions[y[5]]+=1;early+=bool(y[2]&4);pruned+=bool(y[2]&8)
  assert not obs.read()and pending is None
 assert cnt['cases']==case_id+1==46656 and cnt['steps']==k==195175 and cnt['services']==svc==148519
 assert set(requests)==set(range(1,12))
 assert [cnt['allowed'],cnt['skipped'],cnt['lookahead'],cnt['early'],cnt['pruned']]==[actions[1]+actions[2],actions[0],actions[2],early,pruned]
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':cnt,'requests':requests,'actions':actions,'scope':m['scope']};(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
