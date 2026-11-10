from pathlib import Path
from collections import Counter
import hashlib,json,re,sys,runpy
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from build_search_access_router import generate

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/search_access_unit_v3_20261024';m=read(out/'manifest.json');assert m['status']=='passed'
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 assert sha(Path(m['source_path']))==m['source_sha256']
 assert sha(ROOT/'scripts/verify_search_access_unit_v3.py')==m['runner_sha256']==sha(out/'runner.py')
 assert sha(ROOT/'adapters/build_search_access_router.py')==m['generator_sha256']==sha(out/'generator.py')
 assert all(c['exit_code']==0 for c in m['commands'])
 for name in ['access_machine.hpp','kernel.cpp','test_access_machine.cpp']:assert sha(ROOT/'hardware/hls/search_access/v2'/name)==sha(out/'sources'/name)
 ns=runpy.run_path(str(ROOT/'scripts/verify_search_access_unit_v3.py'));s=Path(m['source_path']).read_text();candidate,_=generate(s,'#include <fstream>')
 assert (out/'sources/original_access.inc').read_text()==ns['extract'](s)
 expected=ns['extract'](candidate).replace('search_access::State as=search_access::start();','search_access::State as=record_start(ac);').replace('search_access::accept(ac,as,value)','record_accept(ac,as,value)')
 assert (out/'sources/candidate_access.inc').read_text()==expected and candidate.count('\n')==s.count('\n')
 coords=(out/'sources/coordinates.inc').read_text();assert 'events.push_back({6,id,0});' in coords and 'events.push_back({7,id,0});' in coords
 phase_request={1:1,2:2,3:3,4:4,5:5,6:6,7:4,8:8,9:7,10:4,11:7,12:8,13:9,14:9,15:10,16:7,17:8,18:11,0:0}
 last=None;cfg=None;case=-1;counts=Counter();reqs=Counter();steps=0
 with (out/'vectors.txt').open() as f:
  for line in f:
   v=line.split();assert len(v)==28
   idx,cid=map(int,v[:2]);inp=list(map(lambda x:int(x,16),v[2:22]));ret=list(map(lambda x:int(x,16),v[22:]));assert idx==steps and ret[0]==0
   if inp[0]==0:
    assert cid==case+1 and (last is None or last[1]==0) and ret==[0,1,0,0,1,0]
    case=cid;cfg=inp[6:];counts['hot']+=bool(cfg[1]&256)
   else:
    assert cid==case and inp[6:]==cfg and last is not None
    assert inp[1:5]==[last[1],last[2],last[3],last[5]] and phase_request[inp[1]]==last[4]
    reqs[last[4]]+=1
    if inp[1]==1:counts['visited']+=inp[5]==cfg[0]
   assert ret[4]==phase_request[ret[1]]
   if ret[1]==0:
    counts['allowed']+=ret[5]!=0;counts['skipped']+=ret[5]==0;counts['lookahead']+=ret[5]==2
    counts['early']+=bool(ret[2]&4);counts['pruned']+=bool(ret[2]&8)
   last=ret;steps+=1
 assert steps==195175 and case+1==46656 and last[1]==0
 log=(out/'verify.log').read_text();match=re.search(r'ACCESS_UNIT_PASS cases=(\d+) steps=(\d+) allowed=(\d+) skipped=(\d+) lookahead=(\d+) early=(\d+) pruned=(\d+) hot=(\d+) visited=(\d+)',log);assert match
 assert list(map(int,match.groups()))==[46656,steps]+[counts[k]for k in ['allowed','skipped','lookahead','early','pruned','hot','visited']]
 assert reqs==Counter({int(a):int(b)for a,b in re.findall(r'REQUEST (\d+) (\d+)',log)}) and len(reqs)==11
 old=ROOT/'results/search_access_unit_20261024';assert read(old/'manifest.json')['status']=='failed' and "‘TLD’ was not declared" in (old/'build.log').read_text()
 for name in ['access_machine.hpp','kernel.cpp']:assert sha(old/'sources'/name)==sha(out/'sources'/name)
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':46656,'steps':steps,'counts':dict(counts),'requests':dict(reqs),'scope':'Verbatim original per-child expansion decision and dynamic label/SLR/endY callback order, all 18x18x18 type combinations with 8 contexts. Recursive execution, device services and RTL are separate.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
