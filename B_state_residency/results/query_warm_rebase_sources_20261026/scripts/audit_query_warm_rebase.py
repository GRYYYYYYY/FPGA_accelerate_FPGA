"""Original-byte CRC/identity and anti-replay ledger state-machine oracle."""
from pathlib import Path
import sys,json,runpy,tempfile,struct,zlib
from run_checkpoint_authority import sha
from verify_rtl_bundle import verify
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
b=runpy.run_path(str(p/'sources/build.py'))
with tempfile.TemporaryDirectory()as d:
 b['make'].__globals__['HERE']=Path(d);b['make']();assert (Path(d)/'query_lifecycle.sv').read_bytes()==(p/'sources/query_lifecycle.sv').read_bytes()
bundle=Path(m['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==m['bundle_manifest_sha256'];original=list(struct.unpack('<10I',(bundle/'query.bin').read_bytes()));assert [int(x,16)for x in(p/'query.hex').read_text().splitlines()]==original
rows=[x.split()for x in(p/'native.txt').read_text().splitlines()];seq=0;ctx=[0,0,0];tx=None;permission=1;abort=0;results=[];outputs=[];queries=0;resets=0
for t in rows:
 tag=t[0]
 if tag=='Z':seq=0;ctx=[0,0,0];assert tx is None;resets+=1
 elif tag=='P':
  permission,abort=map(int,t[2:]);
  if tx is not None and(not permission or abort):tx['cancel']=True
 elif tag=='S':
  assert tx is None
  rb,pe,sv,av,wanted,load,sq,sp=map(int,t[2:]);assert pe==permission
  tx=dict(rb=rb,pe=pe,sv=sv,av=av,wanted=wanted,load=load,sq=sq,sp=sp,words=[],out=[],cancel=False)
 elif tag in ['W','M']:
  assert tx is not None;pos=int(t[2]);word=int(t[3],16);last=int(t[4]);buf=tx['words']if tag=='W'else tx['out'];assert pos==len(buf)and last==int(pos==9);buf.append(word)
 elif tag=='R':
  assert tx is not None;status=int(t[2]);crc=int(t[3],16);observed=list(map(int,t[4:]));x=tx;words=x['words']if x['load']else x['out'];computed=zlib.crc32(struct.pack('<'+str(len(words))+'I',*words))if len(words)==10 else 0
  early=x['rb']and(not x['load']or not x['pe']or x['sv']==0 or x['sv']>=x['av']or x['sp']!=(x['sv']&15))
  if early:expected=1;assert not words
  elif x['cancel']:expected=2
  elif not x['load']:
   expected=0;assert len(words)==10;want=original.copy();want[6]=x['av'];want[7]=(want[7]&~63)|(5<<2)|3;want[8]=seq;assert words==want;outputs.append(words)
  else:
   assert len(words)==10;imageversion=x['sv']if x['rb']else x['av'];imagequery=x['sq']if x['rb']else 3;imageprice=x['sp']if x['rb']else 5
   bad=words[0]!=0x51435031 or words[1]!=1 or words[2:6]!=original[2:6] or words[6]!=imageversion or words[7]>>8!=0 or words[7]&3!=imagequery or(words[7]>>2)&15!=imageprice or words[9]!=0 or (words[8]==0 if words[7]&64 else words[8]!=0)
   lower=seq!=0 and(not(words[7]&64)or words[8]<seq)
   expected=int(bad or lower or computed!=x['wanted'])
   if not expected:seq=words[8];ctx=[x['av'],3,5]if words[7]&64 else [0,0,0]
  assert status==expected and crc==computed and observed==[seq,*ctx],(t,expected,computed,seq,ctx,x)
  results.append(status);tx=None
 elif tag=='Q':assert int(t[2])==1 and seq==1;queries+=1
 elif tag=='DONE':checks=int(t[1])
 else:raise AssertionError(t)
assert tx is None and results==[1,1,1,1,1,2,2,0,0,1,1,2]and len(outputs)==1 and queries==1 and resets==2 and checks==119
log=(p/'simulate.log').read_text();assert 'QUERY_REBASE_PASS checks=119'in log and 'Fatal:'not in log
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=checks,results=results,rebased_export=outputs[0],resets=resets,limits=['Native query controller only; source context/recovery permission from TB. Not yet wired to full-system recovery fence or path/label receipt join.','Only ledger context is rebased; no proof of distance-label validity across changed prices, durable authorization or board behavior.'])
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=checks,transactions=len(results))))
