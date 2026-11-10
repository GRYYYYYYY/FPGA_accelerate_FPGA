"""Independently replay cold restore DDR and compare native q2 to CPU oracle."""
from pathlib import Path
import sys,json,struct,mmap,zlib
from collections import Counter
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay

def audit(out,partial=False):
 out=Path(out);m=json.loads((out/'manifest.json').read_text());assert m['status']=='observed' or partial
 base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text())
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h['sha256'],n
 ns={'__file__':str(ROOT/'hardware/variants/cold_stream_late_v1/build.py'),'__name__':'frozen_build'};exec(compile((out/'sources/build.py').read_text(),'build.py','exec'),ns);ns['BASE']=base/'sources';ns['HERE']=out/'sources'
 for n,s in ns['make']().items():assert s==(out/'sources'/n).read_text()
 tb={'__file__':str(ROOT/'hardware/variants/cold_stream_late_v1/build_tb.py'),'__name__':'frozen_tb'};exec(compile((out/'sources/build_tb.py').read_text(),'build_tb.py','exec'),tb);tb['BASE']=base/'sources';assert tb['make']()==(out/'sources/tb_cold_boot.sv').read_text()
 for n,h in m['sources'].items():
  if n not in {'query_residency_system.sv','boot_restore_gate.sv','tb_cold_boot.sv','build.py','build_tb.py','runner.py'}:assert h['sha256']==bm['sources'][n]['sha256']
 proven=Path('/tmp/B_state_residency_offer_20261025/cold_abort_fixed_v1/sources')
 for n in ['query_residency_system.sv','boot_restore_gate.sv']:assert sha(out/'sources'/n)==sha(proven/n)
 report={} 
 for mode,c in m['cases'].items():
  if c['status']!='observed':assert partial;continue
  d=out/mode;p=Path(c['bundle']);mft=verify(p);assert sha(p/'manifest.json')==c['bundle_manifest_sha256']
  log=(d/'simulate.log').read_text();assert 'COLD_BOOT_PASS'in log and 'Fatal:'not in log
  ts=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()]
  def by(tag):return[t for t in ts if t[0]==tag]
  assert len(by('COLD_BOOT_PASS'))==len(by('COLD_Q2_PASS'))==1
  assert [int(x)for x in by('COLD_Q2_PASS')[0][2:]]==[43,42,176]
  stages=by('BOOT_STAGE');assert [t[1]for t in stages]==['labels_written','labels_verified']*2+['imports'];assert stages[1][3]==stages[3][3]=='07'and stages[4][3]=='1f';assert not by('BOOT_ABORT_CANCELED')
  cut=by('STREAM_CUT');aborted=by('STREAM_ABORT');assert len(cut)==len(aborted)==1
  kind='path'if mode.endswith('_path')else'query';assert cut[0][2]==aborted[0][2]==kind and int(cut[0][3])==(39 if kind=='path'else 9)
  assert aborted[0][3:]==['2','0','01']
  if kind=='query':assert cut[0][4:]==['0','0']
  else:assert cut[0][4:]==['0']
  bind=by('AS_BIND');assert len(bind)==2 and all([int(t[2],16),int(t[3]),int(t[4],16)]==[mft['design'],mft['checkpoint'],mft['generation']]for t in bind)
  assert len(by('QCP'))==1 and all(int(t[2])==0 and int(t[3],16)==mft['query_crc32']for t in by('QCP'))
  assert len(by('I'))==656
  records={n:list(r)for n,*r in struct.iter_unpack('<6I',(p/'labels.records').read_bytes())}
  assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)]for t in by('I')}==records
  args=c['commands'][-1]['argv'];pa=dict(args[i+1].split('=',1)for i,x in enumerate(args)if x=='--testplusarg')
  immutable=mft['immutable_resources'];warm=(p/'owner_primary.bin').read_bytes()+(p/'owner_allocator.bin').read_bytes()
  regions=[('graph',[(0x1fffff000,Path(immutable['graph0']['path'])),(0x10fffff000,Path(immutable['graph1']['path'])),(0x20fffff000,Path(immutable['graph2']['path']))],None),('design',[(0x31fffff000,p/'design.bin')],d/'design.bin'),('cost',[(0x71fffff000,p/'cost.bin')],d/'cost.bin'),('owner',[(0x61fffff000,warm)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(immutable['qstate0']['path']))],None),('table',[(0x41fffff000,Path(immutable['tables0']['path'])),(0x51fffff000,Path(immutable['tables1']['path']))],None),('snapshot',[(0x91fffff000,p/'owner_primary.bin'),(0x9208aaef40,p/'owner_allocator.bin')],None)]
  memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
  assert all(v['error_read_beats']==v['error_write_replies']==0 for v in memory.values())
  assert sha(d/'cost.bin')==sha(p/'cost.bin')
  cpu=[l.split()for l in(ROOT/'results/followup_q2_v1/events.txt').read_text().splitlines()]
  expected_p=[[int(x)for x in t[1:4]]for t in cpu if t[0]=='P']
  actual_p=[[int(t[2]),int(t[3],16),int(t[4])]for t in by('P')];assert actual_p==expected_p
  expected_o=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpu)and cpu[i+1][0]=='W')]for i,t in enumerate(cpu)if t[0]=='C']
  actual_o=[[int(t[3]),int(t[4]),int(t[6]),int(int(t[5])==1)]for t in by('O')];assert actual_o==expected_o
  costs=[]
  for line in Path(pa['cost2']).read_text().splitlines():
   t=line.split();costs.append((int(t[1]),sum(int(w,16)<<(32*i)for i,w in enumerate(t[2:25])),sum(int(w,16)<<(32*i)for i,w in enumerate(t[25:]))))
  assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C')]==costs
  qw=struct.unpack('<10I',(p/'query.bin').read_bytes())
  count=9 if kind=='query'else 0
  expected_stream=[(i,qw[i],0)for i in range(count)]+[(i,qw[i],int(i==9))for i in range(10)]
  assert [(int(t[2]),int(t[3],16),int(t[4]))for t in by('QCS')]==expected_stream
  paths=struct.unpack('<78I',(p/'paths.bin').read_bytes());first=list(paths[7:13]);second=[int(t[4])for t in by('RO')if t[2]=='1'and t[3]=='1'];assert len(first)==len(second)==6
  with(ROOT/'results/followup_q2_v1/search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
   chain=[128009]
   while chain[-1]!=65185:
    node=struct.unpack_from('<I',mm,chain[-1]*44+12)[0];assert node!=0xffffffff and len(chain)<32;chain.append(node)
  assert second==chain[1:-1]
  shared=set(first)&set(second);assert len(shared)==2
  for stage in range(4):
   observed=[t for t in by('SO')if int(t[2])==stage];assert len(observed)==(6 if stage==0 else 12)
   for t in observed:
    node=int(t[4]);want=int(node in first)if stage==0 else int(node in first)+int(node in second)if stage==1 else int(node in second)if stage==2 else 0
    assert [int(t[5]),int(t[6])]==[want,int(want!=0)]
  expected=bytearray(warm)
  for n in set(first+second):struct.pack_into('<4I',expected,n*16,0,0,0,0)
  assert expected==(d/'owners.bin').read_bytes()
  assert [(int(t[2]),int(t[3]))for t in by('RO')]==[(1,1)]*6+[(0,2)]*6+[(1,2)]*6
  report[mode]={'interrupted_stream':kind,'words_accepted_before_abort':int(cut[0][3]),'aborted_boots':1,'successful_restarts':1,'cycles':int(by('COLD_Q2_PASS')[0][1]),'labels_restored':len(records),'q2_polls':len(actual_p),'q2_candidates':len(actual_o),'q2_costs':len(costs),'shared_nodes':sorted(shared),'owner_probes':len(by('SO')),'memory':memory}
  print(mode,'audited',flush=True)
 result={'status':'partial'if partial else 'passed','manifest_sha256':sha(out/'manifest.json'),'audit_script_sha256':sha(Path(__file__)),'replay_sha256':sha(ROOT/'scripts/audit_route_fault_axi.py'),'bundle_verifier_sha256':sha(ROOT/'scripts/verify_rtl_bundle.py'),'oracle_hashes':{str(p):sha(p)for p in [ROOT/'results/followup_q2_v1/events.txt',ROOT/'results/followup_q2_v1/search_final_nodes.u32',ROOT/'results/followup_q2_cost_v1/cost_vectors.txt']},'cases':report,'limits':['Partial path/query import abort, fail-closed and cold-reset retry in the same RTL instance for this capacity-zero, one-net/two-path fixture; no runtime rotation, arbitrary snapshots or durable anti-replay proof.','No synthesis/timing/board acceleration measurement for the new boot gate.']}
 (out/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':audit(Path(sys.argv[1]).resolve(),'--partial'in sys.argv)
