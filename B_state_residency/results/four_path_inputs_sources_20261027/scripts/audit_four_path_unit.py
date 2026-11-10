"""Independent path image/owner/stream audit and exact default-system transfer."""
from pathlib import Path
import json, re, runpy, struct, sys, zlib
from run_checkpoint_authority import ROOT, sha

p = Path(sys.argv[1]).resolve()
m = json.loads((p / 'manifest.json').read_text())
assert m['status'] == 'observed'
for name, record in m['sources'].items():
    assert sha(p / 'sources' / name) == (record['sha256'] if isinstance(record, dict) else record), name
builder = p / 'sources' / ('path_capacity_build.py' if 'cases' in m else 'build.py')
generated = runpy.run_path(str(builder))['make']()
for name in generated:
    if (p / 'sources' / name).exists():
        assert (p / 'sources' / name).read_text() == generated[name], name

def crc(words):
    return zlib.crc32(struct.pack('<' + 'I' * len(words), *words))

for n, h in m['artifacts'].items(): assert sha(p / n) == h, n
assert len(m['commands']) == 3 and all(x['exit_code'] == 0 for x in m['commands'])
for root, h in m['input_audits'].items(): assert sha(Path(root) / 'source_bound_audit.json') == h
log = (p / 'simulate.log').read_text(); assert 'Fatal:' not in log and '$finish called' in log
rows = [s.split() for s in (p / 'events.txt').read_text().splitlines()]
def by(tag): return [t for t in rows if t[0] == tag]
mode = m['mode']
if mode == 'path':
    base = p.parent / 'third_warm_full_v2'; third = p.parent / 'followup_iter2_fourth_v1'
    trace=[t.split()for t in(base/'full/natural_trace.txt').read_text().splitlines()]
    image=[int(t[4],16)for t in trace if t[0]=='THIRD_PATH_WORD'and t[2]=='1'];assert len(image)==117
    path = json.loads((third / 'prepare_trace_audit.json').read_text())['path_sink_to_source']
    assert path == [6954,990178,558358,265324,66893]
    image += [1,3,26422,66893,6954,0x9abcdef0,0x12345678] + path[1:-1] + [0]*29
    assert [int(s,16) for s in (p / 'image.txt').read_text().split()] == image
    labels = {}
    with (third / 'search_final_nodes.u32').open('rb') as f:
        for node in path:
            f.seek(node*44); v=struct.unpack('<11I',f.read(44))
            labels[node]=sum(v[k]<<(32*j) for j,k in enumerate([0,1,3,4,5]))
    assert [(int(t[0]),int(t[1],16)) for t in map(str.split,(p/'labels.txt').read_text().splitlines())] == list(labels.items())
    assert [(int(t[1]),int(t[2]),int(t[3],16)) for t in by('L')] == [(4,n,v) for n,v in labels.items()]
    commands = [(0,3,6954),(1,3,151354),(1,3,6954),(0,3,6954),(1,1,67922),(1,2,151354),(1,3,6954),(1,0,204279)]
    assert len(by('Q'))==len(by('R'))==8
    for i,(q,r,want) in enumerate(zip(by('Q'),by('R'),commands),1):
        assert list(map(int,q[1:4])) == [i,want[0],want[1]]
        assert int(q[4],16)==0xabc00000+i and list(map(int,q[5:]))==[want[2],180330]
        assert list(map(int,r[1:]))==[i,1 if i<=2 else 0,0 if i<=2 else 3,0 if i<=2 else 3,[15,15,7,15,13,9,1,0][i-1]]
    refs={339193:1,990179:2,558358:4,265324:5,990178:1}
    with(base/'full/owners.bin').open('rb') as f:
        for node,count in refs.items():
            f.seek(node*16); encoded_net,packed,head,reserved=struct.unpack('<4I',f.read(16))
            assert encoded_net==26423 and packed&0xffff==count and reserved==0
            assert packed>>16==({339193:1,990179:2,558358:2,265324:1,990178:1}[node])
    expected=[]
    for qid,op,chain in [(3,2,path[1:-1]),(4,1,path[1:-1]),(5,2,[990179,558358,265324]),(6,2,[990179,558358,265324]),(7,2,path[1:-1]),(8,2,[339193,558358,265324])]:
        for node in chain:
            new=refs[node]+(1 if op==1 else -1);expected.append([qid,op,node,refs[node],new]);refs[node]=new
    assert [list(map(int,t[1:])) for t in by('O')]==expected
    assert by('FINAL')==[['FINAL','5','18','0','0','0','1','0']]
    done=by('D'); assert len(done)==13
    statuses=[0,0,1,1,1,1,1,2,0,0,0,0,0]; masks=[15]*8+[7,15,15,15,0]
    assert [(int(t[1]),int(t[2]),int(t[4])) for t in done]==list(zip(range(13),statuses,masks))
    cmds=by('C');assert [int(t[1]) for t in cmds]==list(range(13))
    for cid in range(13):
        imported=[t for t in by('I') if int(t[1])==cid];exported=[t for t in by('E') if int(t[1])==cid]
        if int(cmds[cid][2]):
            assert not exported
            want=image.copy()
            if cid==3:want[125]=want[124]
            if cid==4:want[118]=33
            if cid==5:want[122]=0
            count=117 if cid==6 else 125 if cid==7 else 156
            assert [(int(t[2]),int(t[3],16),int(t[4])) for t in imported]==[(i,v,int(i==155 or cid==6 and i==116)) for i,v in enumerate(want[:count])]
            assert int(cmds[cid][3],16)==(crc(want)^(cid==2))
            assert int(done[cid][3],16)==(crc(want) if count==156 else 0)
        else:
            assert not imported
            want=image if cid in [1,9,11] else image[:117]+[0]*39 if cid==8 else [0]*156
            assert [(int(t[2]),int(t[3],16),int(t[4])) for t in exported]==[(i,w,int(i==155))for i,w in enumerate(want)]
            assert int(done[cid][3],16)==crc(want)
    checks=int(re.search(r'PATH_CAPACITY_PASS checks=(\d+) cp=13 routes=8',log).group(1))
    assert checks>2494
    result=dict(status='passed',mode=mode,checks=checks,path_slots=4,image_words=156,image_crc=f'{crc(image):08x}',native_owner_operations=18,native_label_reads=5,checkpoint_transactions=13,route_transactions=8,final_mock_refs=refs,
                scope='Native controller with registered mock owner/label services. Captured native three paths plus real q4 historical path and CPU backtrace; mock references include sole-owner removal. No live DDR or full fourth-query search/warm proof.')
elif mode.startswith('export'):
    default = mode=='export-default'; n=2 if default else 4
    image=[]
    for slot in range(n):image += [1,3,26422,66893,[204279,67922,151354,6954][slot],0x9abcdef0,0x12345678,339193 if slot==0 else 990179,558358,265324]+[0]*29
    query=[0x51435031,1,0x9abcdef0,0x12345678,3,1,5,0x57,180328,0]
    results=by('RESULT');assert len(results)==(14 if default else 16)
    expected=[[1,0,7,1],[0,0,7,0],[1,1,1,0],[1,1,3,0],[1,1,3,0],[1,1,3,0],[1,1,7,0],[1,1,7,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,0,0],[1,1,1,0]]
    if not default:expected += [[1,1,3,0],[1,1,1,0]]
    assert [list(map(int,t[2:6])) for t in results]==expected
    groups=[]
    for t in by('PATH'):
        if int(t[1])==0:groups.append([])
        groups[-1].append((int(t[1]),int(t[2],16),int(t[3])))
    assert len(groups)==(11 if default else 13)
    for j,group in enumerate(groups):
        want=[(i,w,int(i==len(image)-1))for i,w in enumerate(image)]
        if j==2:
            i=5 if default else 122;want[i]=(i,image[i]^1,0)
        if j==3:
            i=20 if default else 137;want[i]=(19,image[i],0)
        if j==11:want[118]=(118,33,0)
        if j==12:want=want[:117];want[-1]=(116,image[116],1)
        assert group==want,j
    assert int(results[0][6],16)==crc(image) and int(results[0][7],16)==crc(query)
    ref=p.parent/'export_manifest_unit_v1'
    reference_rows=[s.split()for s in(ref/'events.txt').read_text().splitlines()]
    assert by('QUERY')==[t for t in reference_rows if t[0]=='QUERY']
    if default:
        ref=p.parent/'export_manifest_unit_v1';assert json.loads((ref/'source_bound_audit.json').read_text())['status']=='passed'
        assert (p/'events.txt').read_bytes()==(ref/'events.txt').read_bytes()
    checks=114 if default else 126
    assert f'EXPORT_MANIFEST_PASS checks={checks}' in log
    result=dict(status='passed',mode=mode,checks=checks,path_slots=n,path_words=len(image),path_crc=f'{crc(image):08x}',scenarios=len(results),default_event_bytes_identical=default,
                scope='Synthetic native-export handshakes and parser/CRC; fourth slot schema/identity/length checked. No native controller or DDR persistence proof from this observer unit alone.')
result.update(manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)))
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('FOUR_PATH_AUDITED',result['mode'])
