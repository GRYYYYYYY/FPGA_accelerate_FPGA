"""Source-bound native cancellation/reject/retry, DDR replay and CPU oracle audit."""
from pathlib import Path
import sys,json,runpy,tempfile,struct,mmap
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;single='--single'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
fixed=p.parent/'warm_cancel_fixed_v2';fm=json.loads((fixed/'manifest.json').read_text());assert json.loads((fixed/'source_bound_audit.json').read_text())['status']=='passed'
changed={'query_residency_system.sv','warm_restore_receipt_join.sv','tb_query_fault.sv','cancel_build.py','cancel_build_tb.py','regression_runner.py'}
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in changed:assert h['sha256']==fm['sources'][n]['sha256'],n
b=runpy.run_path(str(p/'sources/cancel_build.py'))
with tempfile.TemporaryDirectory()as t:
 b['make'].__globals__['HERE']=Path(t);b['make']()
 for n in ['query_residency_system.sv','warm_restore_receipt_join.sv']:assert (Path(t)/n).read_bytes()==(p/'sources'/n).read_bytes(),n
t=runpy.run_path(str(p/'sources/cancel_build_tb.py'));assert t['make']()==(p/'sources/tb_query_fault.sv').read_text()
assert m['rtl']==bm['rtl']+['warm_restore_receipt_join.sv'];inp=Path(bm['input']);original=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes();report={}
fault_node=m['fault_node'];assert fault_node==263946;ordinal=6
if not partial and not single:assert set(m['cases'])=={'full_5','pressure_5'}
if single:assert len(m['cases'])==1
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 assert all(x['exit_code']==0 for x in c['commands']);d=p/name;bundle=Path(c['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==c['bundle_manifest_sha256'];warm=(bundle/'owner_primary.bin').read_bytes()+(bundle/'owner_allocator.bin').read_bytes();assert (d/'pool.bin').read_bytes()==warm
 log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'WARM_RESTORE_OBSERVED'in log and 'JOINT_SYSTEM_COMMIT_PASS'in log
 rows=[x.split()for x in(d/'natural_trace.txt').read_text().splitlines()];oldrows=[x.split()for x in(fixed/name/'natural_trace.txt').read_text().splitlines()]
 def by(tag,source=rows):return[r for r in source if r[0]==tag]
 for tag in ['WARM_FAULT_START','CANCEL_COMPLETE','RETRY_REJECT','RETRY_START','WARM_COMPLETE','WARM_RETRY','JOINT_SYSTEM_Q2_PASS']:assert len(by(tag))==1,tag
 for tag in ['WARM_OWNER_REPAIRED','WL','WP','WPR','WQ','WQR']:assert len(by(tag))==2,tag
 assert len(by('WA'))==3 and all(r[2:]==['1','0']for r in by('WA'))
 assert len(by('CANCEL_HELD'))==8 and all(r[2]=='2'and r[3]=='0'and r[5:]==['1','1']for r in by('CANCEL_HELD'))
 assert by('CANCEL_COMPLETE')[0][2:]==['6','6','18']
 assert by('RETRY_REJECT')[0][2:]==['1','6','c0020000']
 assert by('RETRY_START')[0][2:]==['6','6','c0020001']
 assert by('WARM_COMPLETE')[0][2:]==['0','0','1','1']and by('WARM_RETRY')[0][2:]==['0','6']
 assert by('JOINT_SYSTEM_Q2_PASS')[0][2:]==['43','42','176']
 assert [r[2:]for r in by('WARM_OWNER_REPAIRED')]==[['6','6'],['0','6']]
 assert all(r[2:]==['0','328','328']for r in by('WL'))
 assert [r[2:]for r in by('WQR')]==[['2','00000000'],['0',f'{mf["query_crc32"]:08x}']]
 assert all(r[2:]==['0',f'{mf["path_crc32"]:08x}']for r in by('WPR'))
 ci=rows.index(by('CANCEL_COMPLETE')[0]);oi=oldrows.index(next(r for r in oldrows if r[0]=='CANCEL_COMPLETE'));assert rows[:ci+1]==oldrows[:oi+1]
 nodes=[1231788,726313,1279818,1431195,554512,263946];wants=[0,0,0,0,1,1];occs=wants
 shared_rows=by('SHARED_B');assert [list(map(int,r[2:]))for r in shared_rows]==[[n,2 if i==5 else 0,i+1]for i,n in enumerate(nodes)]
 start=rows.index(by('WARM_FAULT_START')[0]);ri=rows.index(by('RETRY_START')[0]);end=rows.index(by('WARM_RETRY')[0]);parts=[rows[start:ri],rows[ri:end]]
 reject=rows[ci+1:ri];assert not any(r[0]in ['RESET','AS_REARM','KA','KO','LL','WL','WP','WQ']for r in reject)
 assert by('RESET',parts[1])[0][2:]==['6']and by('AS_REARM',parts[1])
 assert all(r[2:] == ['0000000100000002']for r in by('AS_REARM',parts[1]))
 ts=[int(by(tag,parts[1])[0][1])for tag in ['WA','WARM_OWNER_REPAIRED','WL','WP','WPR','WQ','WQR','WARM_COMPLETE']];assert ts==sorted(ts)and len(set(ts))==len(ts)
 # Both native repairs visit all six retained keys in both authority passes.
 for attempt,part in enumerate(parts):
  ka=by('KA',part);ar=by('AS_REPLY',part);ko=by('KO',part);kr=by('KR',part)
  assert len(ka)==len(ar)==12 and [int(r[3])for r in ka]==nodes*2
  assert all(r[2]=='18'and r[4]=='2717'for r in ka)
  assert [r[2:]for r in ar]==[['0',str(w),str(o),'0000000100000002']for w,o in zip(wants,occs)]*2
  expected_ko=([(op,n)for n in nodes for op in [0,2]]+[(0,n)for n in nodes])if attempt==0 else [(0,n)for n in nodes]*2
  assert [(int(r[2]),int(r[3]))for r in ko]==expected_ko
  expected_kr=([x for w,o in zip(wants,occs)for x in [['0',str(w+1),'1'],['0',str(w),str(o)]]]+[['0',str(w),str(o)]for w,o in zip(wants,occs)])if attempt==0 else [['0',str(w),str(o)]for w,o in zip(wants,occs)]*2
  assert [r[2:]for r in kr]==expected_kr
  qrows=part[part.index(by('WQ',part)[0]):part.index(by('WQR',part)[0])];qs=by('QCS',qrows);nwords=9 if attempt==0 else 10
  assert len(qs)==nwords and [int(r[2])for r in qs]==list(range(nwords))and [int(r[3],16)for r in qs]==list(struct.unpack('<10I',(bundle/'query.bin').read_bytes()))[:nwords]
  assert [r[4]for r in qs]==(['0']*9 if attempt==0 else ['0']*9+['1'])
 # Labels/path must be restored anew; old successful receipt flags are cleared.
 records={n:list(w)for n,*w in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())}
 for part in parts:
  lr=part[part.index(by('WARM_OWNER_REPAIRED',part)[0]):part.index(by('WL',part)[0])+1]
  writes=[r for r in by('LL',lr)if r[2]=='1'];assert [(int(r[3]),int(r[4]),int(r[5],16))for r in writes]==[(n,f,w)for n,words in records.items()for f,w in enumerate(words)]
  assert [(int(r[2]),int(r[3],16))for r in by('CHECK',lr)]==[(n,sum(w<<(32*i)for i,w in enumerate(words)))for n,words in records.items()]
 restore=parts[1]
 # Full original label stream is written and then read/verified by the native DDR path.
 records={n:list(w)for n,*w in struct.iter_unpack('<6I',(bundle/'labels.records').read_bytes())};labelrows=restore[restore.index(by('WARM_OWNER_REPAIRED',restore)[0]):restore.index(by('WL',restore)[0])+1]
 writes=[r for r in by('LL',labelrows)if r[2]=='1'];assert [(int(r[3]),int(r[4]),int(r[5],16))for r in writes]==[(n,f,w)for n,words in records.items()for f,w in enumerate(words)]
 checked=by('CHECK',labelrows);assert [(int(r[2]),int(r[3],16))for r in checked]==[(n,sum(w<<(32*i)for i,w in enumerate(words)))for n,words in records.items()]
 # Query packet reaches the native rebase port unchanged, under generation2.
 wq=restore.index(by('WQ',restore)[0]);wqr=restore.index(by('WQR',restore)[0]);qs=by('QCS',restore[wq:wqr]);assert len(qs)==10 and [int(r[2])for r in qs]==list(range(10))and [int(r[3],16)for r in qs]==list(struct.unpack('<10I',(bundle/'query.bin').read_bytes()))
 immutable=mf['immutable_resources'];regions=[('graph',[(0x1fffff000,Path(immutable['graph0']['path'])),(0x10fffff000,Path(immutable['graph1']['path'])),(0x20fffff000,Path(immutable['graph2']['path']))],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],d/'cost.bin'),('owner',[(0x61fffff000,original)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(immutable['qstate0']['path']))],None),('table',[(0x41fffff000,Path(immutable['tables0']['path'])),(0x51fffff000,Path(immutable['tables1']['path']))],None),('snapshot',[(0x91fffff000,inp/'owners.bin'),(0x9208aaef40,inp/'owner_allocator.bin'),(0xa000000000,warm)],None)]
 memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
 for tag,v in memory.items():assert v['error_read_beats']==0 and v['error_write_replies']==(2 if tag=='owner'else 0),(name,tag)
 snapshot=[r.split()for r in(d/'snapshot_axi.txt').read_text().splitlines()];assert [int(r[1],16)for r in snapshot if r[0]=='A'][-8*ordinal:]==[address for n in nodes for address in [0xa008aaff40,0xa000000000+(n*16//64)*64]]*4
 assert sha(d/'cost.bin')==sha(inp/'cost.bin')==sha(bundle/'cost.bin')
 # Price contents never changed; attempt tags changed to6. Compare numerical CPU oracle independently.
 retry=rows[next(i for i,r in enumerate(rows)if r[0]=='WARM_RETRY')+1:]
 cpu=[l.split()for l in(ROOT/'results/followup_q2_v1/events.txt').read_text().splitlines()]
 assert [[int(r[2]),int(r[3],16),int(r[4])]for r in by('P',retry)]==[[int(x)for x in r[1:4]]for r in cpu if r[0]=='P']
 assert [[int(r[3]),int(r[4]),int(r[6]),int(r[5]=='1')]for r in by('O',retry)]==[[int(r[1]),int(r[2]),int(r[3]),int(i+1<len(cpu)and cpu[i+1][0]=='W')]for i,r in enumerate(cpu)if r[0]=='C']
 args=c['commands'][-1]['argv'];pa=dict(args[i+1].split('=',1)for i,x in enumerate(args)if x=='--testplusarg');costs=[]
 for line in Path(pa['cost2']).read_text().splitlines():
  t=line.split();costs.append((int(t[1]),sum(int(w,16)<<(32*i)for i,w in enumerate(t[2:25])),sum(int(w,16)<<(32*i)for i,w in enumerate(t[25:]))))
 assert [(int(r[2]),int(r[3],16),int(r[4],16))for r in by('C',retry)]==costs
 first=list(struct.unpack('<78I',(bundle/'paths.bin').read_bytes())[7:13]);second=[int(r[4])for r in by('RO',retry)if r[2]=='1'and r[3]=='1'];assert len(first)==len(second)==6
 assert [int(r[4])for r in by('RO',retry)if r[2]=='0'and r[3]=='2']==first
 with(ROOT/'results/followup_q2_v1/search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
  chain=[128009]
  while chain[-1]!=65185:
   n=struct.unpack_from('<I',mm,chain[-1]*44+12)[0];assert n!=0xffffffff and len(chain)<32;chain.append(n)
 assert second==chain[1:-1]and len(set(first)&set(second))==2
 for stage in [1,2,3]:
  probes=[r for r in by('SO',retry)if int(r[2])==stage];assert len(probes)==12
  for r in probes:
   n=int(r[4]);count=int(n in first)+int(n in second)if stage==1 else int(n in second)if stage==2 else 0;assert [int(r[5]),int(r[6])]==[count,int(count!=0)]
 expected=bytearray(warm)
 for n in set(first+second):struct.pack_into('<4I',expected,n*16,0,0,0,0)
 assert (d/'owners.bin').read_bytes()==expected
 report[name]=dict(cancel_status=2,rejected_attempt=5,retry_attempt=6,retry_cookie='c0020001',retry_corrected=0,retained_journal=6,fault_node=fault_node,journal_entries=ordinal,repaired_nodes=nodes,wanted_refs=wants,old_g1_shared_refs=[0]*(ordinal-4),warm_checkpoint=18,labels_verified=328,path_words=78,query_words=10,q2_polls=43,q2_expands=42,q2_candidates=176,q2_costs=len(costs),shared_nodes=sorted(set(first)&set(second)),post_retry_owner_probes=36,memory=memory);print(name,'warm full-system audited',flush=True)
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),replay_sha256=sha(ROOT/'scripts/audit_route_fault_axi.py'),oracle_hashes={str(x):sha(x)for x in [ROOT/'results/followup_q2_v1/events.txt',ROOT/'results/followup_q2_v1/search_final_nodes.u32',ROOT/'results/followup_q2_cost_v1/cost_vectors.txt']},cases=report,limits=['Both q2 shared nodes,5/6-entry journals, one-net capacity-zero fixture. Other faults/overflow/arbitrary workloads pending.','Price/history DDR contents identical before/after; only attempt tags changed. Not arbitrary changed-price distance-label reuse.','AXI-inflight/label-inflight cancellation, late success abort, durable floors, runtime snapshot writer, synthesis/timing and board remain pending.'])
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n')
