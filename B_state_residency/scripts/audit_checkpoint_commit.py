"""Source-bound three-way publication and independent q2/AXI oracle."""
from pathlib import Path
import json,sys,runpy,struct,mmap,zlib,tempfile
from run_checkpoint_authority import ROOT,sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());partial='--partial'in sys.argv;assert m['status']=='observed'or partial
base=Path(m['base']);integration=p.parent/'checkpoint_system_v4';im=json.loads((integration/'manifest.json').read_text());ia=json.loads((integration/'source_bound_audit.json').read_text());assert ia['status']=='passed'and ia['manifest_sha256']==sha(integration/'manifest.json')
for n,h in m['sources'].items():
 assert sha(p/'sources'/n)==h['sha256'],n
 if n not in ['tb_query_fault.sv','query_residency_system.sv','build.py','build_tb.py','runner.py']:assert h['sha256']==im['sources'][n]['sha256'],n
assert m['rtl']==im['rtl']
g=runpy.run_path(str(p/'sources/build.py'))
with tempfile.TemporaryDirectory()as tmp:
 g['make'].__globals__['HERE']=Path(tmp);g['make']();assert (Path(tmp)/'query_residency_system.sv').read_bytes()==(p/'sources/query_residency_system.sv').read_bytes()

b=runpy.run_path(str(p/'sources/build_tb.py'));tb=b['make']((base/'sources/tb_query_fault.sv').read_text())
ties=".boot_required(1'b0),.boot_cfg_valid(1'b0),.boot_verify_valid(1'b0),.boot_rsp_ready(1'b0),.boot_design(64'd0),.boot_generation(64'd0),.boot_checkpoint(32'd0),.boot_version(32'd0),.boot_nodes(32'd0),.boot_label_count(32'd0),.boot_label_crc(32'd0),.boot_path_crc(32'd0),.boot_query_crc(32'd0),.boot_query(2'd0),.boot_slots(2'd0),.boot_price(4'd0),.boot_payload(2304'd0),"
tb=tb.replace(')system(.jp_start',')system('+ties+'.jp_start').replace('endmodule','always @(posedge clk)if(!k_cold_rst&&!rst)begin if(system.boot_pending||system.boot_rsp_valid)$fatal(1,"normal start entered bootstrap");end\nendmodule');assert tb==(p/'sources/tb_query_fault.sv').read_text()
report={};inp=Path(m['input']);original=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
if not partial:assert set(m['cases'])=={'full_5','pressure_5'}
for name,c in m['cases'].items():
 if c['status']!='observed':assert partial;continue
 assert all(x['exit_code']==0 for x in c['commands'])
 d=p/name;bundle=Path(c['bundle']);mf=verify(bundle);assert sha(bundle/'manifest.json')==c['bundle_manifest_sha256']
 warm=(bundle/'owner_primary.bin').read_bytes()+(bundle/'owner_allocator.bin').read_bytes();assert (d/'pool.bin').read_bytes()==warm and sha(d/'pool.bin')==c['warm_sha256']==sha(base/name/'owners.bin')
 log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and 'JOINT_SYSTEM_COMMIT_PASS'in log
 rows=[x.split()for x in(d/'natural_trace.txt').read_text().splitlines()]
 def by(tag):return[r for r in rows if r[0]==tag]
 assert len(by('JP'))==len(by('JOINT_SYSTEM_COMMIT'))==len(by('JOINT_SYSTEM_Q2_PASS'))==1
 assert by('JP')[0][2:]==['7','17','17','6','0000000100000001']
 assert [r[2:]for r in by('JE')]==[['2','17','6','17','1'],['0','18','0','18','1']]
 assert [r[2:]for r in by('JS')]==[['17','6','4','4','1']]*2
 assert by('JAS')[-1][2:]==['1','0000000100000002','18'] and by('JAR')[-1][2:]==['0','0000000100000001']
 assert by('JOINT_SYSTEM_COMMIT')[0][2:]==['18','0','0000000100000002'] and by('JOINT_SYSTEM_Q2_PASS')[0][2:]==['43','42','176']
 # New namespace only changes generation/checksum; context and monotonic floor persist.
 oldq=[r for r in rows if r[0]=='QCM'and r[1]=='3'];newq=[r for r in rows if r[0]=='QCM'and r[1]=='6'];assert len(oldq)==len(newq)==10
 ow=[int(r[3],16)for r in oldq];nw=[int(r[3],16)for r in newq];assert ow[4]==1 and nw[4]==2 and all(ow[i]==nw[i]for i in range(10)if i!=4) and nw[8]==1
 assert [r[2]for r in by('QCP')][-3:]==['1','0','0']
 assert struct.pack('<10I',*nw)==(bundle/'query.bin').read_bytes()
 assert int(by('QCP')[-2][3],16)==zlib.crc32(struct.pack('<10I',*nw))
 for index,words in [('5',ow),('7',nw)]:assert [int(r[3],16)for r in by('QCS')if r[1]==index]==words

 # All working transaction streams before publication match the independently audited capture.
 for tag in ['graph','cost','design','owner','label','qstate','table']:
  before=(base/name/(tag+'_axi.txt')).read_bytes();assert (d/(tag+'_axi.txt')).read_bytes().startswith(before),(name,tag)
 immutable=mf['immutable_resources']
 regions=[('graph',[(0x1fffff000,Path(immutable['graph0']['path'])),(0x10fffff000,Path(immutable['graph1']['path'])),(0x20fffff000,Path(immutable['graph2']['path']))],None),('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],d/'cost.bin'),('owner',[(0x61fffff000,original)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),('qstate',[(0x81fffff000,Path(immutable['qstate0']['path']))],None),('table',[(0x41fffff000,Path(immutable['tables0']['path'])),(0x51fffff000,Path(immutable['tables1']['path']))],None),('snapshot',[(0x91fffff000,inp/'owners.bin'),(0x9208aaef40,inp/'owner_allocator.bin'),(0xa000000000,warm)],None)]
 memory={tag:replay(d/(tag+'_axi.txt'),rr,ff)for tag,rr,ff in regions}
 for tag,v in memory.items():assert v['error_read_beats']==0 and v['error_write_replies']==int(tag=='owner'),(name,tag)
 snapshot_rows=(d/'snapshot_axi.txt').read_text().splitlines();old_snapshot=(base/name/'snapshot_axi.txt').read_text().splitlines()
 assert snapshot_rows[:len(old_snapshot)]==old_snapshot
 added=[x.split()for x in snapshot_rows[len(old_snapshot):]]
 aq=by('APQ');ar=by('APR');assert len(aq)==len(ar)==8
 assert aq[0][2:]==['0','4754','0000000100000001','1'] and ar[0][2:]==['1','0','0','0000000100000002','1']
 expected_addresses=[]
 for rq,rp in zip(aq[1:],ar[1:]):
  node,net=int(rq[2]),int(rq[3]);assert rq[4]=='0000000100000002' and rp[2:]==['0','1','1','0000000100000002',rq[5]]
  record=struct.unpack_from('<4I',warm,node*16);assert record[:2]==(net+1,65537)
  expected_addresses.extend([0xa008aaff40,0xa000000000+(node*16//64)*64])
 assert len(added)==2*len(expected_addresses) and [int(t[1],16)for t in added if t[0]=='A']==expected_addresses
 assert len([t for t in added if t[0]=='R'])==len(expected_addresses)

 assert sha(d/'cost.bin')==sha(inp/'cost.bin')
 split=next(i for i,r in enumerate(rows)if r[0]=='JOINT_SYSTEM_COMMIT');q=rows[split+1:]
 def qb(tag):return[r for r in q if r[0]==tag]
 cpu=[l.split()for l in(ROOT/'results/followup_q2_v1/events.txt').read_text().splitlines()]
 assert [[int(r[2]),int(r[3],16),int(r[4])]for r in qb('P')]==[[int(x)for x in r[1:4]]for r in cpu if r[0]=='P']
 assert [[int(r[3]),int(r[4]),int(r[6]),int(r[5]=='1')]for r in qb('O')]==[[int(r[1]),int(r[2]),int(r[3]),int(i+1<len(cpu)and cpu[i+1][0]=='W')]for i,r in enumerate(cpu)if r[0]=='C']
 args=c['commands'][-1]['argv'];pa=dict(args[i+1].split('=',1)for i,x in enumerate(args)if x=='--testplusarg');costs=[]
 for line in Path(pa['cost2']).read_text().splitlines():
  t=line.split();costs.append((int(t[1]),sum(int(w,16)<<(32*i)for i,w in enumerate(t[2:25])),sum(int(w,16)<<(32*i)for i,w in enumerate(t[25:]))))
 assert [(int(r[2]),int(r[3],16),int(r[4],16))for r in qb('C')]==costs
 first=list(struct.unpack('<78I',(bundle/'paths.bin').read_bytes())[7:13]);second=[int(r[4])for r in qb('RO')if r[2]=='1'and r[3]=='1'];assert len(first)==len(second)==6
 with(ROOT/'results/followup_q2_v1/search_final_nodes.u32').open('rb')as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as mm:
  chain=[128009]
  while chain[-1]!=65185:
   node=struct.unpack_from('<I',mm,chain[-1]*44+12)[0];assert node!=0xffffffff and len(chain)<32;chain.append(node)
 assert [(int(r[2]),int(r[3]))for r in aq[1:]]==[(n,2717)for n in first]+[(0,4754)]
 for rq,rp in zip(aq,ar):assert int(rq[1])>int(by('JP')[0][1]) and int(rp[1])-int(rq[1])>=8
 assert second==chain[1:-1] and len(set(first)&set(second))==2
 for stage in range(4):
  observed=[r for r in qb('SO')if int(r[2])==stage];assert len(observed)==(6 if stage==0 else 12)
  for r in observed:
   node=int(r[4]);want=int(node in first)if stage==0 else int(node in first)+int(node in second)if stage==1 else int(node in second)if stage==2 else 0
   assert [int(r[5]),int(r[6])]==[want,int(want!=0)]
 expected=bytearray(warm)
 for n in set(first+second):struct.pack_into('<4I',expected,n*16,0,0,0,0)
 assert expected==(d/'owners.bin').read_bytes()
 report[name]=dict(joint_publications=1,q2_polls=len(qb('P')),q2_costs=len(costs),authority_gets=len(aq),authority_new_read_beats=len(expected_addresses),owner_probes=len(qb('SO')),shared_nodes=sorted(set(first)&set(second)),memory=memory)
 print(name,'audited',flush=True)
r=dict(status='partial'if partial else 'passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),replay_sha256=sha(ROOT/'scripts/audit_route_fault_axi.py'),integration_audit_sha256=sha(integration/'source_bound_audit.json'),oracle_hashes={str(x):sha(x)for x in [ROOT/'results/followup_q2_v1/events.txt',ROOT/'results/followup_q2_v1/search_final_nodes.u32',ROOT/'results/followup_q2_cost_v1/cost_vectors.txt']},cases=report,limits=['Actual fixture full-system publication and normal q2 continuation; no post-rotation fault recovery/target-reset path-query-label restore yet.','Warm image from existing committed capture; no runtime working DDR snapshot writer, general multi-net/overflow, durable authentication, timing or board result.'])
(p/('partial_audit.json'if partial else 'source_bound_audit.json')).write_text(json.dumps(r,indent=2)+'\n');print(r['status'])
