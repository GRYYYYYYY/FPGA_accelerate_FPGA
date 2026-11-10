"""Replay native controllers and a separate cycle-level receipt-state oracle."""
from pathlib import Path
import sys,json,struct,zlib,collections
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
base=p.parent/'checkpoint_commit_v6';bm=json.loads((base/'manifest.json').read_text())
for n in ['label_restore_controller.sv','route_commit_controller.sv']:assert sha(p/'sources'/n)==bm['sources'][n]['sha256']
rebase=p.parent/'query_warm_rebase_v3';assert json.loads((rebase/'source_bound_audit.json').read_text())['status']=='passed';assert sha(p/'sources/query_lifecycle.sv')==sha(rebase/'sources/query_lifecycle.sv')
bundle=Path(m['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==m['bundle_manifest_sha256'];paths=list(struct.unpack('<78I',(bundle/'paths.bin').read_bytes()));query=list(struct.unpack('<10I',(bundle/'query.bin').read_bytes()));labels={n:list(w)for n,*w in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())}
assert [int(x,16)for x in(p/'paths.hex').read_text().splitlines()]==paths and [int(x,16)for x in(p/'query.hex').read_text().splitlines()]==query
packed=[int(x,16)for x in(p/'labels.hex').read_text().splitlines()];assert [(x>>160,[(x>>(32*i))&0xffffffff for i in range(5)])for x in packed]==list(labels.items())
rows=[x.split()for x in(p/'native.txt').read_text().splitlines()];groups=collections.defaultdict(list);cases=collections.defaultdict(list)
for r in rows:
 if r[0]=='DONE':checks=int(r[1]);continue
 groups[int(r[2])].append(r);cases[int(r[1])].append(r)
assert set(cases)==set(range(9)) and checks==389
# Independent mutable storage model: actual field writes must equal bundle,
# and final readback requests must cover all rows in original order.
for case,rs in cases.items():
 def by(tag):return[r for r in rs if r[0]==tag]
 if case==5:assert not by('L')and not by('B');continue
 assert [int(r[3])for r in by('C')]==[0,1]
 memory={n:[0]*5 for n in labels};writes=[];reads=[]
 for r in by('B'):
  write,node,field=int(r[3]),int(r[4]),int(r[5]);value=int(r[6],16)
  if write:
   assert node in labels and 0<=field<5 and value==labels[node][field];memory[node][field]=value;writes.append((node,field))
  else:reads.append(node)
 assert writes==[(n,f)for n in labels for f in range(5)] and reads==[0,*labels] and memory==labels
 assert len(by('LR'))==1 and by('LR')[0][3:]==['0',str(778 if case==1 else 777),'328','328']
 for tag,reply,original in [('PW','PR',paths),('QW','QR',query)]:
  packets=by(tag)
  if not packets:assert not by(reply);continue
  words=[]
  for r in packets:assert int(r[3])==len(words)and int(r[5])==int(len(words)==len(original)-1);words.append(int(r[4],16))
  want=original.copy()
  if case==7 and tag=='PW':want[7]=42
  if case==8 and tag=='QW':want[8]=2
  assert words==want[:len(words)]
  assert len(by(reply))==1;r=by(reply)[0];computed=zlib.crc32(struct.pack('<'+str(len(words))+'I',*words))if len(words)==len(original)else 0
  assert int(r[4],16)==computed
  if tag=='PW':assert len(words)==78 and int(r[3])==int(case==2)
  else:assert len(words)==(9 if case==3 else 10)and int(r[3])==(2 if case==3 else 0)
# Cycle model observes live inputs and accepted/consumed native handshakes.
state=0;started=[False]*3;good=[False]*3;pending=[False]*3;cp=0;live=None;last_g=None;joined_cycles=0;fault_cases=set();g_count=0
for cyc in range(1,max(groups)+1):
 rs=groups[cyc];tags=[r[0]for r in rs]
 ins=[r for r in rs if r[0]=='I']
 if ins:assert len(ins)==1;live=list(map(int,ins[0][3:]))
 assert live is not None
 rst,abort,owned,drained,repaired,version,armcp=live
 if rst:state=0;started=[False]*3;good=[False]*3;pending=[False]*3;cp=0;last_g=None;assert 'G'not in tags;continue
 retired=int(not any(pending));context=version==5;bad=state!=0 and(abort or not owned or cp!=18 or((repaired or state==2)and not context));fault=int(state==3 or bad);held=int(state!=0);bits=sum(int(x)<<i for i,x in enumerate(good))if held else 0
 safe=int(state==1 and not fault and drained and repaired and context and good[0]);joined=int(state==2 and not fault and drained and retired)
 expected=[state,bits,joined,fault,held,safe,retired,drained,repaired];gs=[r for r in rs if r[0]=='G']
 if expected!=last_g:assert len(gs)==1 and list(map(int,gs[0][3:]))==expected,(cyc,expected,gs);last_g=expected;g_count+=1
 else:assert not gs,(cyc,gs)
 if joined:joined_cycles+=1
 for r in rs:
  if r[0]=='F':assert list(map(int,r[3:]))==[joined,fault]
 # Native busy intervals are independent of join state and must drain after abort.
 for tag,index in [('L',0),('P',1),('Q',2)]:
  if tag in tags:assert not pending[index];pending[index]=True
 for tag,index in [('LR',0),('PR',1),('QR',2)]:
  if tag in tags:assert pending[index];pending[index]=False
 if bad:state=3
 elif state==0 and 'A'in tags:
  assert owned and drained and retired;cp=armcp;state=1 if armcp==18 else 3;started=[False]*3;good=[False]*3
 elif state==1:
  old_good=good.copy()
  for tag,index in [('L',0),('P',1),('Q',2)]:
   if tag in tags:
    allow=(drained and repaired and context and not started[0])if index==0 else(safe and not started[index])
    assert allow;started[index]=True
  for r in rs:
   if r[0]=='LR':ok=started[0]and not good[0]and r[3:]==['0','777','328','328'];index=0
   elif r[0]in ['PR','QR']:
    index=1 if r[0]=='PR'else 2;expected_crc=mf['path_crc32']if index==1 else mf['query_crc32'];ok=started[index]and not good[index]and int(r[3])==0 and int(r[4],16)==expected_crc
   else:continue
   if ok:good[index]=True
   else:state=3
  if 'F'in tags:state=3
  if all(old_good)and retired and drained and not any(t in tags for t in ['L','LR','P','PR','Q','QR','F']):state=2
 elif state==2:
  if any(t in tags for t in ['L','LR','P','PR','Q','QR']):state=3
  elif 'F'in tags and joined:state=0
 for r in gs:
  if int(r[6]):fault_cases.add(int(r[1]))
assert fault_cases=={1,2,3,4,5,6,7,8} and joined_cycles>8 and state==0
log=(p/'simulate.log').read_text();assert 'WARM_RECEIPT_JOIN_PASS checks=389'in log and 'Fatal:'not in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),checks=checks,scenarios=len(cases),native_label_runs=8,labels_verified=8*328,native_label_field_writes=8*328*5,gate_observations=g_count,fault_cases=sorted(fault_cases),limits=['Native three-controller restore slice, behavioral mutable label RAM. Recovery ownership/owner-repaired and active identity/context supplied by TB; not full-root fence/coordinator integration.','No working-owner AXI repair or q2 search/retry executed; no cross-price distance-validity, durable authorization, synthesis/timing or board proof.'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(status='passed',checks=checks,gate_observations=g_count)))
