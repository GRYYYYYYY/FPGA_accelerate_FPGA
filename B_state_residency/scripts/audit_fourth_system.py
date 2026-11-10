"""Source-bound four-slot/G4/q4 audit of original native logs and all twelve AXI ports.

No compatibility trace is manufactured. The frozen G3-warm prefix is compared
on original event payloads and physical files; all extended memory is replayed.
The overwritten A snapshot bank is explicitly versioned at the observed G4
retirement boundary, never interpreted using only its final file contents.
"""
from pathlib import Path
from collections import Counter
import json
import runpy
import struct
import sys
import zlib
from run_checkpoint_authority import ROOT, sha
from audit_route_fault_axi import replay
from audit_third_warm_records import audit_native_records

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed' and len(m['cases'])==1
case=next(iter(m['cases']));d=p/case;c=m['cases'][case]
assert c['status']=='observed' and len(c['commands'])==3 and all(v['exit_code']==0 for v in c['commands'])
ref=p.parent/('third_warm_'+case+'_v2');rd=ref/case
rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
report=json.loads((ROOT/'results/third_warm_20261027.json').read_text())
assert ra==report['cases'][ref.name]
assert ra['manifest_sha256']==sha(ref/'manifest.json')
assert report['restores'][ref.name]['audit_sha256']==sha(ref/'source_bound_audit.json')
parent=Path(m['parent_run']);assert sha(parent/'source_bound_audit.json')==m['parent_audit_sha256']
for n,e in m['sources'].items():
    assert sha(p/'sources'/n)==e['sha256'],n
    if n not in ['runner.py','tb_query_fault.sv','fourth_build.py','fourth_tasks.sv']:
        assert e['sha256']==rm['sources'][n]['sha256'],n
assert m['rtl']==rm['rtl']
assert runpy.run_path(str(p/'sources/fourth_build.py'))['make']()==(p/'sources/tb_query_fault.sv').read_text()
assert sha(Path(m['binding']))==m['binding_sha256']==rm['binding_sha256']
for key in ['scoreboards','next_scoreboards','third_scoreboards','fourth_scoreboards']:
    for n,h in m[key].items():assert sha(p/n)==h
for root,h in m['fourth_inputs'].items():assert sha(Path(root)/'source_bound_audit.json')==h
cost=p.parent/'followup_iter2_fourth_cost_v1';cpu=p.parent/'followup_iter2_fourth_plain_v1'
for n in ['cost.bin','connections.bin']:assert sha(cost/n)==sha(p.parent/'followup_iter2_third_cost_v1'/n)

rows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
oldrows=[t.split()for t in(rd/'natural_trace.txt').read_text().splitlines()]
def by(tag, part=None):return[t for t in (rows if part is None else part)if t[0]==tag]
def at(tag):return next(i for i,t in enumerate(rows)if t[0]==tag)
crc=lambda words:zlib.crc32(struct.pack('<'+'I'*len(words),*words))
rotation=at('G4_ROTATION_BEGIN');published=at('G4_PUBLISHED');begin=at('FOURTH_BEGIN');prepared=at('FOURTH_PREPARED')
assert rotation<published<begin<prepared
prefix=rows[:rotation];fourth=rows[begin:];search=rows[prepared:]
# Cycle shifts follow the extra 39 path words. CPU packet values, route slot
# numbers, journal ordering and recovery responses must remain the real prefix.
transferred={}
for tag in ['P','O','C','Q','SEARCH','LIFECYCLE','RO','RB','RC','RL','RA','J','BF','KA','AS_REPLY','KO','KR','WL']:
    a=[t[2:]for t in by(tag,prefix)];b=[t[2:]for t in by(tag,oldrows)]
    assert a==b,('prefix native',tag);transferred[tag]=len(a)
assert by('THIRD_PASS')[0][2:]==['114','113','565','302','7','180329']
assert by('THIRD_WARM_RELEASE')[0][2:]==['6','0','6','3','180328']
assert len(by('THIRD_WARM_HELD'))==8 and all(t[2:]==['0','1','0','7','1','0']for t in by('THIRD_WARM_HELD'))

def slot(sink,first):return[1,3,26422,66893,sink,0x9abcdef0,0x12345678,first,558358,265324]+[0]*29
g3path=slot(204279,339193)+slot(67922,990179)+[0]*78
g4path=slot(204279,339193)+slot(67922,990179)+slot(151354,990179)+[0]*39
finalpath=g4path[:117]+slot(6954,990178)
assert [int(t[3],16)for t in by('G3_PATH_WORD')]==g3path
assert [(int(t[2]),int(t[3],16))for t in by('THIRD_WARM_PATH')]==list(enumerate(g3path))
warm=rows[at('THIRD_WARM_START'):at('THIRD_WARM_RELEASE')+1]
assert by('WPR',warm)[0][2:]==['0',f'{crc(g3path):08x}']
assert [int(t[4],16)for t in by('THIRD_PATH_WORD')if t[2]=='1']==g4path
assert [int(t[3],16)for t in by('G4_PATH_WORD')]==g4path
assert by('G4_PATH_RESULT')[0][2:]==[f'{crc(g4path):08x}']
assert [(int(t[1]),int(t[2],16))for t in by('FOURTH_PATH_IMPORT')]==list(enumerate(finalpath))
for capture,want in [(0,g4path),(1,finalpath)]:
    assert [(int(t[3]),int(t[4],16))for t in by('FOURTH_PATH_WORD')if int(t[2])==capture]==list(enumerate(want))
    done=[t for t in by('FOURTH_PATH_DONE')if int(t[2])==capture]
    assert len(done)==1 and done[0][3:]==[f'{crc(want):08x}',str(7 if capture==0 else 15)]
# Every actually accepted export, not just a task's copied word array, is 156 words.
groups=[]
for t in by('BPATH'):
    if t[1]=='0':groups.append([])
    groups[-1].append((int(t[1]),int(t[2],16),int(t[3])))
assert groups and all(len(g)==156 and [x[0]for x in g]==list(range(156)) and [x[2]for x in g]==[0]*155+[1]for g in groups)
assert [x[1]for x in groups[-1]]==finalpath

g4query=[0x51435031,1,0x9abcdef0,0x12345678,4,1,6,0x58,180329,0]
finalquery=g4query[:8]+[180330,0]
assert [int(t[3],16)for t in by('G4_QUERY_WORD')]==g4query
assert [int(t[3],16)for t in by('FOURTH_QUERY_WORD')]==finalquery
g4=rows[rotation:begin]
exports={}
for t in by('QCM',g4):exports.setdefault(int(t[1]),[]).append((int(t[2]),int(t[3],16),int(t[4])))
assert len(exports)==2 and all(g==[(i,w,int(i==9))for i,w in enumerate(g4query)]for g in exports.values())
assert all(t[2:]==['0',f'{crc(g4query):08x}','0','180329']for t in by('QCP',g4))
assert by('JP',g4)[0][2:]==['7','19','19','3','0000000100000003'] and len(by('JP',g4))==1
assert len(by('JP'))==3
assert by('G4_PUBLISHED')[0][2:]==['0000000100000004','20','6','7','180329']
assert by('G4_PREPARED_PROOF')[0][2:]==['1','1','1','0','1']
assert len(by('G4_AUTH_HELD'))==8 and all(t[2:]==['0','0','1','0']for t in by('G4_AUTH_HELD'))
assert by('CUMULATIVE_PRECONDITION',g4)[0][2:]==['1','1','1','1','0','4','0000000100000003','19','7','180329']
assert [t[2:]for t in by('CUMULATIVE_RESULT',g4)]==[
    ['1','0','4','0','0','0','0000000100000003','19'],
    ['2','0','4','4','0','0','0000000100000004','20']]
assert by('CUMULATIVE_G4_CANDIDATE')[0][2:]==['0000000100000004','20','000000a000000000','4']
assert [t[2:6]for t in by('APR',g4)]==[[s,r,o,'0000000100000004']for s,r,o in [('1','0','0'),('0','1','1'),('0','2','2'),('0','4','2'),('0','1','2'),('0','5','1')]]
assert [(int(t[2]),int(t[3]),int(t[4],16))for t in by('APQ',g4)]==[(339193,26422,0x100000003)]+[(n,net,0x100000004)for n,net in [(339193,26422),(990179,26422),(558358,26422),(558358,23916),(265324,26422)]]
assert by('FOURTH_BEGIN')[0][2:]==['7','0','180329']
assert by('FOURTH_PREPARED')[0][2:]==['7','3','180329']
assert by('FOURTH_PASS')[0][2:]==['83','82','402','231','15','180330',f'{crc(finalquery):08x}']
assert not by('RESET',fourth) and not by('JP',fourth) and not by('FI',fourth)
assert not by('BF',rows[begin:at('FOURTH_PATH_IMPORT')]),'Metadata export changed owners'

cpur=[t.split()for t in(cpu/'events.txt').read_text().splitlines()]
polls=[list(map(int,t[1:4]))for t in cpur if t[0]=='P']
candidates=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(cpur)and cpur[i+1][0]=='W')]for i,t in enumerate(cpur)if t[0]=='C']
costs=[(int(t[1]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[2:25])),sum(int(v,16)<<(32*i)for i,v in enumerate(t[25:])))for t in map(str.split,(cost/'cost_vectors.txt').read_text().splitlines())]
assert(len(polls),len(candidates),len(costs))==(83,402,231)
assert [[int(t[2]),int(t[3],16),int(t[4])]for t in by('P',search)]==polls
assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])]for t in by('O',search)]==candidates
assert [(int(t[2]),int(t[3],16),int(t[4],16))for t in by('C',search)]==costs
assert [int(t[2])for t in by('Q',search)]==list(range(100,182))
assert by('LIFECYCLE',fourth)[0][2:]==['3','0','1','4','1','3','3']
nodes=[990178,558358,265324]
routes=[[3,op,n]for op in [2,1]for n in nodes]
assert [list(map(int,t[2:]))for t in by('RO',fourth)]==routes
assert [list(map(int,t[2:5]))for t in by('J',fourth)]==[[n,26422,op]for _,op,n in routes]
assert [(int(t[2]),int(t[3]))for t in by('BF',fourth)]==[(op,n)for _,op,n in routes]
assert all(int(j[1])<int(b[1])for j,b in zip(by('J',fourth),by('BF',fourth)))

# All prefix physical transfers remain directly inspectable in original logs.
physical_prefix={}
for tag in ['graph','design','table','label','owner','cost','qstate','snapshot','copy','labelsnap','baseline','g3copy']:
    old=(rd/(tag+'_axi.txt')).read_bytes();new=(d/(tag+'_axi.txt')).read_bytes()
    assert new.startswith(old),('physical prefix',tag)
    if tag=='copy':assert new==old
    physical_prefix[tag]=len(old.splitlines())
reg=json.loads(Path(m['binding']).read_text())['regions']
initial=b''.join(Path(reg[k]['path']).read_bytes()for k in ['owners','owner_pool','owner_allocator'])
graph=ROOT/'results/graph_image_20261024'
regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),
         ('design',[(0x31fffff000,Path(reg['design']['path']))],d/'design.bin'),
         ('cost',[(0x71fffff000,Path(reg['cost_history_prices_nets']['path']))],d/'cost.bin'),
         ('owner',[(0x61fffff000,initial)],d/'owners.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),
         ('qstate',[(0x81fffff000,Path(reg['connections']['path']))],None),
         ('table',[(0x41fffff000,Path(reg['rows']['path'])),(0x51fffff000,Path(reg['columns']['path']))],None),
         ('baseline',[(0xb000000000,Path(m['baseline_image'])/'baseline.bin')],None)]
memory={tag:replay(d/(tag+'_axi.txt'),rr,final)for tag,rr,final in regions}
assert all(v['error_read_beats']==0 and v['error_write_replies']==(2 if tag=='owner'else 0)for tag,v in memory.items())
assert memory['owner']['write_beats']==31
assert sha(d/'owners.bin')==sha(d/'g3.bin')==sha(d/'pool.bin')==sha(rd/'owners.bin')
assert (d/'snapshot.bin').read_bytes()==initial

owner_tail=[t.split()for t in(d/'owner_axi.txt').read_text().splitlines()[physical_prefix['owner']:]]
writes=[]
for t in owner_tail:
    if t[0]!='W':continue
    mask=int(t[2],16);lane=(mask&-mask).bit_length()-1
    assert lane in [0,16,32,48]and mask==0xffff<<lane
    node=(int(t[1],16)-0x61fffff000+lane)//16
    value=((int(t[3],16)>>(8*lane))&((1<<128)-1)).to_bytes(16,'little');writes.append((node,value))
assert [n for n,v in writes]==nodes*2
for (n,value),count in zip(writes,[0,3,4,1,4,5]):
    with(d/'owners.bin').open('rb')as f:f.seek(n*16);expected=list(struct.unpack('<4I',f.read(16)))
    if n==990178 and count==0:expected=[0,0,0,0]
    else:expected[1]=(expected[1]&0xffff0000)|count
    assert struct.unpack('<4I',value)==tuple(expected),(n,value.hex(),expected)

g2=(rd/'pool.bin').read_bytes();g3=(d/'g3.bin').read_bytes()
def copy_replay(tag, phases):
    lines=[t.split()for t in(d/(tag+'_axi.txt')).read_text().splitlines()]
    assert len(lines)==24*len(phases)
    for phase,(src,old,dst,base)in enumerate(phases):
        buf=bytearray(old);offsets=[]
        for i in range(4):
            a,r,w,b,va,vr=lines[phase*24+i*6:phase*24+i*6+6]
            offset=int(a[1],16)-0x61fffff000;offsets.append(offset)
            assert a[0]=='A'and a[2]=='1'and offset%64==0
            data=src[offset:offset+64]
            assert r[0]=='R'and r[1]==a[1]and r[3]=='0'and int(r[2],16).to_bytes(64,'little')==data
            assert w[0]=='W'and int(w[1],16)==base+offset and int(w[2],16)==(1<<64)-1 and int(w[3],16).to_bytes(64,'little')==data
            buf[offset:offset+64]=data;assert b==['B','0']
            assert va==['A',w[1],'1']and vr==['R',w[1],w[3],'0']
        assert offsets==[n*16 for n in [339192,558356,265324,990176]]
        assert bytes(buf)==dst
    return dict(read_beats=8*len(phases),write_beats=4*len(phases),verified_bytes=146284032*len(phases))
memory['copy']=copy_replay('copy',[(g2,initial,g2,0xa000000000)])
memory['g3copy']=copy_replay('g3copy',[(g3,initial,g3,0xc000000000),(g3,g2,g3,0xa000000000)])
cut=int(by('G4_ROTATION_BEGIN')[0][2]);copied=by('G4_ROTATION_COPIED')[0]
assert by('G4_ROTATION_BEGIN')[0][3:]==['8','4']and copied[2:]==[str(cut),'16','8']
assert cut==ra['physical_memory']['snapshot']['read_beats']
pending=[];reads=0;requests=0
for t in map(str.split,(d/'snapshot_axi.txt').read_text().splitlines()):
    if t[0]=='A':
        assert not pending;address=int(t[1],16);length=int(t[2]);assert 1<=length<=3 and address%4096+length*64<=4096
        pending=[address+64*i for i in range(length)];requests+=1
    else:
        assert t[0]=='R'and pending and pending.pop(0)==int(t[1],16)and t[3]=='0'
        address=int(t[1],16);rr=[(0x91fffff000,initial),(0xa000000000,g2 if reads<cut else g3),(0xc000000000,g3)]
        matches=[buf[address-base:address-base+64]for base,buf in rr if base<=address<base+len(buf)]
        assert len(matches)==1 and int(t[2],16).to_bytes(64,'little')==matches[0]
        reads+=1
        if reads==cut:assert not pending
assert not pending and reads>cut
memory['snapshot']=dict(read_beats=reads,read_transactions=requests,g4_rotation_cut_beats=cut,versioned_a_bank=True)

# G4 native labels must match q3 CPU state and their actual frame reads.
g4labels=[(int(t[2]),int(t[3],16))for t in by('G4_LABEL_RECORD')]
assert len(g4labels)==len(dict(g4labels))==781
miss_before={int(t[2])for t in by('BM',prefix)};assert set(dict(g4labels))==miss_before
def cpu_labels(capture,nodes,sink):
    result={}
    with(capture/'search_final_nodes.u32').open('rb')as f:
        for n in nodes:
            f.seek(n*44);u=struct.unpack('<11I',f.read(44));v=[u[k]for k in [0,1,3,4,5]]
            if n==sink:v[4]=0
            result[n]=sum(w<<(32*i)for i,w in enumerate(v))
    return result
assert dict(g4labels)==cpu_labels(p.parent/'followup_iter2_third_plain_v1',miss_before,151354)
labelcrc=zlib.crc32(b''.join(struct.pack('<I',n)+v.to_bytes(20,'little')for n,v in g4labels))
assert by('G4_LABEL_DONE')[0][2:]==['781','393',f'{labelcrc:08x}']
assert by('G4_BUNDLE')[0][2:]==['781',f'{labelcrc:08x}',f'{crc(g4path):08x}',f'{crc(g4query):08x}','1','1','1']
assert [(int(t[0]),sum(int(v,16)<<(32*i)for i,v in enumerate(t[1:])))for t in map(str.split,(d/'runtime_g4_labels.txt').read_text().splitlines())]==g4labels
scans=by('G4_FRAME_REPLY');assert len(scans)==394 and scans[-1][2:]==['6','393','0000000','0']
assert [int(t[2])for t in by('G4_FRAME_REQUEST')]==list(range(394))
pages={}
for n,v in g4labels:
    pg,sl=divmod(n,8);buf=pages.setdefault(pg,bytearray(192));buf[0]|=1<<sl;buf[1+sl*20:21+sl*20]=v.to_bytes(20,'little')
frame_pages={}
for i,t in enumerate(scans[:-1]):
    owner=int(t[4],16);assert t[2]=='0'and int(t[3])==i and t[5]=='1'and owner>>21==24
    frame_pages[i]=owner&((1<<21)-1)
assert set(frame_pages.values())==set(pages)and len(set(frame_pages.values()))==393
tail=[t.split()for t in(d/'labelsnap_axi.txt').read_text().splitlines()[physical_prefix['labelsnap']:]]
assert len(tail)==2358
for i in range(1179):
    a,r=tail[2*i:2*i+2];frame,chunk=divmod(i,3);address=frame*192+chunk*64
    assert a[0]=='A'and int(a[1],16)==address and a[2]=='1'
    assert r[0]=='R'and int(r[1],16)==int(a[1],16)and r[3]=='0'and int(r[2],16).to_bytes(64,'little')==pages[frame_pages[frame]][chunk*64:(chunk+1)*64]
memory['labelsnap']=dict(prefix_lines=physical_prefix['labelsnap'],g4_read_beats=1179,g4_records=781,g4_pages=393)

misses={int(t[2])for t in by('BM')};final_labels=cpu_labels(cpu,misses,6954);pages={}
for n,v in final_labels.items():
    pg,sl=divmod(n,8);buf=pages.setdefault(pg,bytearray(192));buf[0]|=1<<sl;buf[1+sl*20:21+sl*20]=v.to_bytes(20,'little')
expected=Counter(bytes(v)for v in pages.values());expected[bytes(192)]+=16384-len(pages)
data=(d/'labels.bin').read_bytes();assert len(data)==3145728 and Counter(data[i:i+192]for i in range(0,len(data),192))==expected
native=audit_native_records(rows,d)
log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and 'FOURTH_PASS polls=83 expands=82 candidates=402 costs=231'in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),native_auditor_sha256=sha(ROOT/'scripts/audit_third_warm_records.py'),case=case,
            production_sources_match=ref.name,prefix_event_counts=transferred,physical_prefix_lines=physical_prefix,physical_memory=memory,native_labels=native,
            query_sequence=180330,connection=170791,polls=83,expansions=82,candidates=402,costs=231,
            generation=0x100000004,checkpoint=20,context=[6,0,6],g4_labels=781,g4_pages=393,path_words=156,
            g4_path_crc=f'{crc(g4path):08x}',g4_query_crc=f'{crc(g4query):08x}',g4_label_crc=f'{labelcrc:08x}',final_path_crc=f'{crc(finalpath):08x}',final_query_crc=f'{crc(finalquery):08x}',
            final_slot_mask=15,final_journal=3,final_labels=len(misses),final_pages=len(pages),new_baseline_nodes=len(misses-miss_before),owner_sha256=sha(d/'owners.bin'),final_cycle=int(by('FOURTH_PASS')[0][1]),
            scope='Native four-slot G3 warm prefix, cumulative G4 rotation into former G2 bank with versioned physical read replay, actual 156-word/label/query joint publication, natural q4 last-primary-owner removal/recommit and CPU numerical oracle. Fixed price/history and trusted initial clones/full baseline. No G4 fault recovery, natural overflow allocation/free, timing or board claim.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOURTH_SYSTEM_AUDITED',case,result['final_cycle'])
