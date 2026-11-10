"""Audit optimized G4 label failure, retained journal and attempt8 noncold retry."""
from pathlib import Path
from collections import Counter
import json,runpy,struct,sys,zlib
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
from audit_restore_seed_retry_records import audit_native_records

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and len(m['cases'])==1
case=next(iter(m['cases']));d=p/case;c=m['cases'][case]
assert c['status']=='observed'and len(c['commands'])==3 and all(v['exit_code']==0 for v in c['commands'])
ref=p.parent/('fourth_system_'+case+'_v2');rd=ref/case
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
report=json.loads((ROOT/'results/fourth_system_20261027.json').read_text())
assert report['cases'][ref.name]==ra and report['restores'][ref.name]['audit_sha256']==sha(ref/'source_bound_audit.json')
assert ra['manifest_sha256']==sha(ref/'manifest.json')
assert sha(Path(m['parent_run'])/'source_bound_audit.json')==m['parent_audit_sha256']
candidate=runpy.run_path(str(p/'sources/restore_seed_build.py'))['make']()
changed=set(candidate)|{'runner.py','tb_query_fault.sv','restore_seed_build.py','restore_seed_tb_build.py','build.py','base_tb.py','failure_task.sv'}
parent=Path(m['parent_run']);parent_m=json.loads((parent/'manifest.json').read_text())
for n,e in m['sources'].items():
    assert sha(p/'sources'/n)==e['sha256'],n
    if n not in changed:assert e['sha256']==parent_m['sources'][n]['sha256'],n
for n,s in candidate.items():assert (p/'sources'/n).read_text()==s,n
assert m['rtl']==parent_m['rtl']
tb_builder=p/'sources/restore_seed_tb_build.py'
tb_code=tb_builder.read_text();assert tb_code.count("HERE/'build.py'")==1
tb_ns={'__file__':str(tb_builder),'__name__':'restore_seed_audit_builder'}
exec(compile(tb_code.replace("HERE/'build.py'","HERE/'restore_seed_build.py'"),str(tb_builder),'exec'),tb_ns)
assert tb_ns['make']()==(p/'sources/tb_query_fault.sv').read_text()
enabled=m['restore_seed_bypass'];assert enabled==1
mode=m['restore_seed_failure'];assert mode in ['cancel','crc']
is_crc=mode=='crc'
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    for n,h in m[key].items():assert sha(p/n)==h==rm[key][n]
for root,h in m['fourth_inputs'].items():assert sha(Path(root)/'source_bound_audit.json')==h
assert sha(Path(m['binding']))==m['binding_sha256']==rm['binding_sha256']
rows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
old=[t.split()for t in(rd/'natural_trace.txt').read_text().splitlines()]
def by(tag,part=None):return[t for t in (rows if part is None else part)if t[0]==tag]
def at(tag):return next(i for i,t in enumerate(rows)if t[0]==tag)
crc=lambda words:zlib.crc32(struct.pack('<'+'I'*len(words),*words))
oldcut=next(i for i,t in enumerate(old)if t[0]=='FOURTH_PREPARED')+1
cut=at('FOURTH_FAULT_BEGIN')
assert rows[:cut]==old[:oldcut],'Native G4/first natural ripup prefix or cycles changed'
start=at('FOURTH_WARM_START');release=at('FOURTH_WARM_RELEASE');retry=at('FOURTH_RETRY_BEGIN')
assert cut<start<release<retry
fault=rows[cut:start];warm=rows[start:release+1];q4=rows[at('FOURTH_BEGIN'):];again=rows[retry:]
first=rows[at('SEED_FAILURE_BEGIN'):at('SEED_RETRY_START')]
restored=rows[at('SEED_RETRY_OWNER'):release+1]
assert len(by('FOURTH_BEGIN'))==len(by('FOURTH_PREPARED'))==2
assert all(t[2:]==['7','0','180329']for t in by('FOURTH_BEGIN'))
assert all(t[2:]==['7','3','180329']for t in by('FOURTH_PREPARED'))
assert len(by('FI',fault))==1 and by('FI',fault)[0][2:]==['3','4','4']
failed=by('FAILED_QUERY',fault);assert len(failed)==1
assert failed[0][2:]==['3','7','8','0','0','3']
assert by('SEARCH',fault)[0][2:]==['3','8','1','1','0']
assert by('FOURTH_FAULT_DONE')[0][2:]==['1','0','0','0','7','8','180330']
assert by('FOURTH_FAULT_DONE')[0][-1]=='180330','Failed attempt must retain its accepted sequence'
assert not by('RO',fault)and not by('C',fault)and not by('O',fault),'Fault must precede owner commit'
assert len(by('RESET',q4))==2 and all(t[2:]==['3']for t in by('RESET',q4))
rearm=by('AS_REARM',q4);assert len(rearm)==1 and rearm[0][2:]==['0000000100000004']
assert int(by('SEED_RETRY_START')[0][1])<int(rearm[0][1])<int(by('RESET',q4)[1][1])
assert not by('JP',q4),'No extra generation publication during restore/retry'
nodes=[990178,558358,265324]
routes=[[3,op,n]for op in [2,2,1]for n in nodes]
assert [list(map(int,t[2:]))for t in by('RO',q4)]==routes
assert [list(map(int,t[2:5]))for t in by('J',q4)]==[[n,26422,op]for _,op,n in routes]
assert [(int(t[2]),int(t[3]))for t in by('BF',q4)]==[(op,n)for _,op,n in routes]
assert all(int(j[1])<int(b[1])for j,b in zip(by('J',q4),by('BF',q4)))

authority=by('KA',warm)
assert [list(map(int,t[2:5]))for t in authority]==[[20,n,26422]for n in nodes]*4
expected_cookies=[cookie^i^(0x80000000 if verify else 0)for cookie in [0xc0040001,0xc0040002]for verify in [False,True]for i in range(3)]
assert [int(t[5])for t in authority]==expected_cookies
assert len({int(t[5])for t in authority[:6]})==len({int(t[5])for t in authority[6:]})==6
auth_pending=None
for t in warm:
    if t[0]=='KA':assert auth_pending is None;auth_pending=t
    elif t[0]=='AS_REPLY':assert auth_pending is not None;auth_pending=None
    elif t[0]=='AS_REARM':assert auth_pending is None
assert auth_pending is None
assert [t[2:]for t in by('AS_REPLY',warm)]==[[str(0),str(r),str(o),'0000000100000004']for r,o in [(1,1),(4,2),(5,1)]*4]
assert [(int(t[2]),int(t[3]))for t in by('KO',warm)]==[(op,n)for n in nodes for op in [0,1]]+[(0,n)for n in nodes]+[(0,n)for n in nodes]*2
assert [list(map(int,t[2:]))for t in by('KR',warm)]==[[0,r,o]for r,o in [(0,0),(1,1),(3,2),(4,2),(4,1),(5,1),(1,1),(4,2),(5,1)]+[(1,1),(4,2),(5,1)]*2]
assert by('FOURTH_WARM_OWNER')[0][2:]==['3','3']
path=[int(t[3],16)for t in by('G4_PATH_WORD')]
query=[int(t[3],16)for t in by('G4_QUERY_WORD')]
assert len(path)==156 and path[0]==path[39]==path[78]==1 and path[117:]==[0]*39
assert query==[0x51435031,1,0x9abcdef0,0x12345678,4,1,6,0x58,180329,0]
assert [(int(t[2]),int(t[3],16))for t in by('FOURTH_WARM_PATH')]==list(enumerate(path))
assert [(int(t[2]),int(t[3],16))for t in by('FOURTH_WARM_QUERY')]==list(enumerate(query))
labels=[(int(t[2]),int(t[3],16))for t in by('G4_LABEL_RECORD')]
assert len(labels)==len(dict(labels))==781
labelcrc=zlib.crc32(b''.join(struct.pack('<I',n)+v.to_bytes(20,'little')for n,v in labels))
assert [(int(t[2]),int(t[3],16))for t in by('RELOAD',restored)]==labels
assert [(int(t[2]),int(t[3],16))for t in by('CHECK',restored)]==labels
assert [list(map(int,t[2:5]))+[int(t[5],16)]for t in by('LL',restored)if t[2]=='1']==[[1,n,f,(v>>(32*f))&0xffffffff]for n,v in labels for f in range(5)]
assert by('FOURTH_WARM_START')[0][2:]==['3','20',f'{labelcrc:08x}',f'{crc(path):08x}',f'{crc(query):08x}']
assert by('FOURTH_WARM_LABELS')[0][2:]==['781','781',f'{labelcrc:08x}']
assert [t[2:]for t in by('WL',restored)]==[['0','781','781']]
assert [t[2:]for t in by('WPR',warm)]==[['0',f'{crc(path):08x}']]
assert [t[2:]for t in by('WQR',warm)]==[['0',f'{crc(query):08x}']]
held=by('FOURTH_WARM_HELD');assert len(held)==8 and all(t[2:]==['0','0','0','7','1','0']for t in held)
assert int(by('WL',restored)[0][1])<int(by('WPR',warm)[0][1])<int(by('WQR',warm)[0][1])<int(held[0][1])<int(by('FOURTH_WARM_RELEASE')[0][1])
assert by('FOURTH_WARM_RELEASE')[0][2:]==['8','2','8','7','180329']
assert by('FOURTH_FLOOR_BEGIN')[0][2:]==['7','0','180329']
assert by('FOURTH_FLOOR_REJECT')[0][2:]==['1','0','7','180329']
probe=rows[at('FOURTH_FLOOR_BEGIN'):at('FOURTH_FLOOR_REJECT')+1]
assert all(not by(tag,probe)for tag in ['LI','P','E','RO','J','BF'])

cpu=p.parent/'followup_iter2_fourth_plain_v1';cost=p.parent/'followup_iter2_fourth_cost_v1'
cpur=[t.split()for t in(cpu/'events.txt').read_text().splitlines()]
polls=[list(map(int,t[1:4]))for t in cpur if t[0]=='P']
candidates=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpur)and cpur[i+1][0]=='W')]for i,t in enumerate(cpur)if t[0]=='C']
costs=[(int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(cost/'cost_vectors.txt').read_text().splitlines())]
assert(len(polls),len(candidates),len(costs))==(83,402,231)
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P',again)]==polls
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O',again)]==candidates
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C',again)]==costs
assert [int(t[2])for t in by('Q',again)]==list(range(100,182))
assert by('LIFECYCLE',again)[0][2:]==['3','0','1','4','1','3','3']
finalpath=path[:117]+[1,3,26422,66893,6954,0x9abcdef0,0x12345678,*nodes]+[0]*29
assert [int(t[4],16)for t in by('FOURTH_PATH_WORD',again)if t[2]=='1']==finalpath
finalquery=query[:6]+[8,0x62,180330,0]
assert [int(t[3],16)for t in by('FOURTH_QUERY_WORD')]==finalquery
assert [int(t[3],16)for t in by('QCM',again)]==finalquery
assert by('FOURTH_PASS')[0][2:]==['83','82','402','231','15','180330',f'{crc(finalquery):08x}']

# No new snapshot copy/export is made during recovery. All three corresponding
# original AXI files and raw source image files must equal the restored reference.
memory={}
for tag in ['copy','g3copy','labelsnap']:
    assert(d/(tag+'_axi.txt')).read_bytes()==(rd/(tag+'_axi.txt')).read_bytes(),tag
    memory[tag]=dict(verified_reference_audit=sha(ref/'source_bound_audit.json'),axi_sha256=sha(d/(tag+'_axi.txt')),physical_bytes_identical=True)
for n in ['snapshot.bin','pool.bin','g3.bin','cost.bin','design.bin','runtime_g4_labels.txt']:
    assert sha(d/n)==sha(rd/n),n
reg=json.loads(Path(m['binding']).read_text())['regions']
initial=b''.join(Path(reg[k]['path']).read_bytes()for k in ['owners','owner_pool','owner_allocator'])
graph=ROOT/'results/graph_image_20261024'
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),
         ('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),
         ('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),
         ('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),
         ('baseline',[(0xb000000000,Path(m['baseline_image'])/'baseline.bin')],None)]
memory.update({tag:replay(d/(tag+'_axi.txt'),rr,final)for tag,rr,final in regions})
assert all(memory[tag]['error_read_beats']==(1 if tag=='graph'else 0)and memory[tag]['error_write_replies']==(2 if tag=='owner'else 0)for tag,_,_ in regions)
assert memory['owner']['write_beats']==37 and sha(d/'owners.bin')==ra['owner_sha256']
oldowner=(p.parent/('third_warm_'+case+'_v2')/case/'owner_axi.txt').read_bytes()
raw=(d/'owner_axi.txt').read_bytes();assert raw.startswith(oldowner)
writes=[]
for t in map(str.split,raw[len(oldowner):].decode().splitlines()):
    if t[0]!='W':continue
    mask=int(t[2],16);lane=(mask&-mask).bit_length()-1
    assert lane in [0,16,32,48]and mask==0xffff<<lane
    n=(int(t[1],16)-0x61fffff000+lane)//16;value=((int(t[3],16)>>(8*lane))&((1<<128)-1)).to_bytes(16,'little');writes.append((n,value))
assert [n for n,v in writes]==nodes*4
for (n,value),count in zip(writes,[0,3,4,1,4,5]*2):
    with(d/'owners.bin').open('rb')as f:f.seek(n*16);expected=list(struct.unpack('<4I',f.read(16)))
    if n==990178 and count==0:expected=[0]*4
    else:expected[1]=(expected[1]&0xffff0000)|count
    assert struct.unpack('<4I',value)==tuple(expected),(n,value.hex(),expected)

g2=(p.parent/('third_warm_'+case+'_v2')/case/'pool.bin').read_bytes();g4=(d/'pool.bin').read_bytes()
cutbeats=int(by('G4_ROTATION_BEGIN')[0][2]);assert cutbeats==72 and by('G4_ROTATION_COPIED')[0][2:]==['72','16','8']
pending=[];readbeats=requests=0
old_snapshot=(rd/'snapshot_axi.txt').read_bytes();new_snapshot=(d/'snapshot_axi.txt').read_bytes();assert new_snapshot.startswith(old_snapshot)
for t in map(str.split,new_snapshot.decode().splitlines()):
    if t[0]=='A':
        assert not pending;address=int(t[1],16);length=int(t[2]);assert 1<=length<=3 and address%4096+length*64<=4096
        pending=[address+64*i for i in range(length)];requests+=1
    else:
        assert t[0]=='R'and pending and pending.pop(0)==int(t[1],16)and t[3]=='0'
        address=int(t[1],16);regions_now=[(0x91fffff000,initial),(0xa000000000,g2 if readbeats<cutbeats else g4),(0xc000000000,g4)]
        choices=[data[address-base:address-base+64]for base,data in regions_now if base<=address<base+len(data)]
        assert len(choices)==1 and int(t[2],16).to_bytes(64,'little')==choices[0];readbeats+=1
        if readbeats==cutbeats:assert not pending
assert not pending and readbeats==109
memory['snapshot']=dict(read_beats=readbeats,read_transactions=requests,versioned_a_bank=True,rotation_cut_beats=cutbeats,g4_recovery_read_beats=readbeats-85)

misses={int(t[2])for t in by('BM')};pages={}
with(cpu/'search_final_nodes.u32').open('rb')as f:
    for n in misses:
        f.seek(n*44);u=struct.unpack('<11I',f.read(44));v=[u[k]for k in [0,1,3,4,5]]
        if n==6954:v[4]=0
        pg,sl=divmod(n,8);buf=pages.setdefault(pg,bytearray(192));buf[0]|=1<<sl;struct.pack_into('<5I',buf,1+sl*20,*v)
expected=Counter(bytes(v)for v in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
native=audit_native_records(rows,d)
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),native_auditor_sha256=sha(ROOT/'scripts/audit_restore_seed_retry_records.py'),case=case,
 production_parent=parent.name,modified_production_sources=sorted(candidate),restore_seed_bypass=enabled,query_sequence=180330,connection=170791,checkpoint=20,source_context=[6,0,6],target_context=[8,2,8],
 prefix_native_cycles_byte_identical=True,prefix_rows=cut,graph_error_beats=1,failed_attempt_consumed_sequence=180330,restored_source_floor=180329,empty_slot_floor_probe_status=1,
 authority_rounds=4,journal_keys=nodes,correction_increments=3,recreated_primary_owner=990178,restored_labels=781,path_words=156,
 source_label_crc=f'{labelcrc:08x}',source_path_crc=f'{crc(path):08x}',source_query_crc=f'{crc(query):08x}',final_path_crc=f'{crc(finalpath):08x}',final_query_crc=f'{crc(finalquery):08x}',
 retry_polls=83,retry_expansions=82,retry_candidates=402,retry_costs=231,final_sequence=180330,final_slot_mask=15,final_journal=3,
 final_labels=len(misses),final_pages=len(pages),physical_memory=memory,native_labels=native,owner_sha256=sha(d/'owners.bin'),final_cycle=int(by('FOURTH_PASS')[0][1]),
 failed_query_response=[int(v)for v in failed[0][2:]],failed_search_counts=[int(v)for v in by('FOURTH_FAULT_DONE')[0][2:6]],
 scope='Actual graph R error followed by optimized restore failure/retry, four G4 authority rounds and three native INC repairs including empty primary recreation; original781/156/10-word receipts rebased to fresh attempt8 and source ledger180329, empty fourth-slot floor rejection then CPU q180330 retry. Sequence180330 was consumed in the failed attempt6; this is new-attempt recovery, not global never-reuse proof. Fixed price/history, externally trusted initial clones/full baseline. No arbitrary fault/cancel, overflow allocation/free, persistent floor/authentication or timing/board proof.')
events={tag:int(by(tag,q4)[0][1])for tag in ['FI','FOURTH_WARM_START','RESET','FOURTH_WARM_OWNER','FOURTH_WARM_LABELS','WPR','WQR','FOURTH_WARM_RELEASE','FOURTH_RETRY_BEGIN','FOURTH_PASS']}
result['behavioral_cycles']=dict(events=events,fault_to_release=events['FOURTH_WARM_RELEASE']-events['FI'],owner_phase=events['FOURTH_WARM_OWNER']-events['FOURTH_WARM_START'],label_phase=events['FOURTH_WARM_LABELS']-events['FOURTH_WARM_OWNER'],retry_including_exports=events['FOURTH_PASS']-events['FOURTH_RETRY_BEGIN'])

# Original source stream is preserved; only the last payload bit is corrupted
# in the explicit CRC-negative attempt. The next attempt rereads original data.
bad_labels=list(labels) if is_crc else labels[:1]
if is_crc:bad_labels[-1]=(bad_labels[-1][0],bad_labels[-1][1]^1)
assert [(int(t[2]),int(t[3],16))for t in by('RELOAD',first)]==bad_labels
expected_written=780 if is_crc else 0
expected_fields=3900 if is_crc else 3
expected_status=8 if is_crc else 7
assert [t[2:]for t in by('SEED_FAILURE_RECEIPT')]==[[str(expected_status),str(expected_written),'0',str(expected_fields)]]
assert [t[2:]for t in by('WL',first)]==[[str(expected_status),str(expected_written),'0']]
first_writes=[t for t in by('LL',first)if t[2]=='1']
expected_all=[(n,f,(v>>(f*32))&0xffffffff)for n,v in labels for f in range(5)]
assert [(int(t[3]),int(t[4]),int(t[5],16))for t in first_writes]==expected_all[:expected_fields]
assert not by('CHECK',first) and not by('BM',first)
assert len(by('SEED_ABORT'))==(0 if is_crc else 1)
if not is_crc:
    aborted=by('SEED_ABORT')[0];assert aborted[2:]==['3','0','0']
    native_writes=[t for t in by('NB',first)if t[2]=='3']
    assert len(native_writes)==3 and native_writes[-1][7]=='2'
    assert int(native_writes[-1][1])<int(aborted[1])
    replies=[t for t in by('NR',first)if int(t[1])>int(native_writes[-1][1])]
    assert replies and int(aborted[1])<int(replies[0][1])<int(by('SEED_FAILURE_RECEIPT')[0][1])
held_failure=by('SEED_FAILURE_HELD')
assert len(held_failure)==8 and all(t[2:]==['6','3',str(expected_written),'0','1','1']for t in held_failure)
assert int(by('SEED_FAILURE_RECEIPT')[0][1])<int(held_failure[0][1])
assert by('SEED_RETRY_REJECT')[0][2:]==['1','3','c00400ff']
assert by('SEED_RETRY_START')[0][2:]==['8','2','3']
assert by('SEED_RETRY_OWNER')[0][2:]==['0','3']
retired_gap=rows[at('SEED_FAILURE_HELD'):at('SEED_RETRY_START')]
assert all(not by(tag,retired_gap)for tag in ['RESET','KA','KO','RELOAD','LL','P','E','RO','J','BF'])
assert not by('BM',restored)
assert sum(t[2]=='3'for t in by('NB',restored))==3905

seedrows=[t.split()for t in(d/'restore_seed_trace.txt').read_text().splitlines()]
starts=[i for i,t in enumerate(seedrows)if t[0]=='START']
assert len(starts)==2 and starts[0]==0
for number,segment in enumerate([seedrows[:starts[1]],seedrows[starts[1]:]]):
    writes=[t for t in segment if t[0]=='WRITE'];limit=expected_fields if number==0 else 3905
    assert [(int(t[2]),int(t[3]),int(t[4],16))for t in writes]==expected_all[:limit]
    assert all(t[5]=='7'for t in writes)
    assert len(segment)==limit+2
    if number==0:assert segment[-1][0]=='FAIL'and segment[-1][2:]==[str(expected_fields),str(expected_written),'0',str(expected_status)]
    else:assert segment[-1][0]=='PASS'and segment[-1][2:]==['3905','781','781']

reference=p.parent/('restore_seed_on_'+case+'_v1');reference_d=reference/case
reference_a=json.loads((reference/'source_bound_audit.json').read_text())
assert reference_a['status']=='passed'and reference_a['manifest_sha256']==sha(reference/'manifest.json')
reference_rows=[t.split()for t in(reference_d/'natural_trace.txt').read_text().splitlines()]
ref_cut=next(i for i,t in enumerate(reference_rows)if t[0]=='FOURTH_WARM_OWNER')+1
assert rows[:at('FOURTH_WARM_OWNER')+1]==reference_rows[:ref_cut]
for n in candidate:assert sha(p/'sources'/n)==sha(reference/'sources'/n),n
for n in ['owners.bin','labels.bin','pool.bin','snapshot.bin','g3.bin','design.bin','cost.bin']:
    assert sha(d/n)==sha(reference_d/n),n
result['retry_label_phase_cycles']=int(by('FOURTH_WARM_LABELS')[0][1])-int(by('SEED_RETRY_OWNER')[0][1])
result['restore_failure']=dict(mode=mode,failed_context=[7,1,7],retry_context=[8,2,8],
    failed_native_status=expected_status,failed_complete_records=expected_written,
    failed_field_writes=expected_fields,verified_before_failure=0,coordinator_status=6,
    held_failure_cycles=8,same_attempt_status=1,retained_journal=3,retry_corrections=0,
    final_ddr_identical_to_success=True,successful_optimized_reference_audit=sha(reference/'source_bound_audit.json'),
    original_prefix_cycles_identical=True,external_cold_reset=False,working_ddr_reloaded=False)
result['scope']+=' Two deterministic optimized label failure points only: partial native write cancellation or last-record CRC corruption, according to mode. Both retain three-key journal and require retirement before attempt8 rearm; native same-attempt rejection and six owner GETs on retry, then all781 records verified and CPU q4 retry. Not arbitrary cancellation, AXI-timeout, price-change validity, persistent floor/authentication or board performance proof.'
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('RESTORE_SEED_RETRY_AUDITED',case,mode,result['final_cycle'])
