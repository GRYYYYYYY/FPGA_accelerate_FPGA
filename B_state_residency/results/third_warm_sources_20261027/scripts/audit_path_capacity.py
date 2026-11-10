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

if 'cases' in m:
    assert len(m['cases']) == 1
    case = next(iter(m['cases'])); c = m['cases'][case]
    assert c['status'] == 'observed' and len(c['commands']) == 3 and all(x['exit_code'] == 0 for x in c['commands'])
    ref = p.parent / ('owner_g3_retired_' + case + '_v3')
    a = json.loads((ref / 'source_bound_audit.json').read_text())
    report = json.loads((ROOT / 'results/owner_g3_publish_20261027.json').read_text())
    assert a == report['cases'][ref.name]
    assert report['restores'][ref.name]['audit_sha256'] == sha(ref / 'source_bound_audit.json')
    assert a['manifest_sha256'] == sha(ref / 'manifest.json')
    rm = json.loads((ref / 'manifest.json').read_text())
    assert m['rtl'] == rm['rtl'] and m['binding_sha256'] == rm['binding_sha256']
    assert m['scoreboards'] == rm['scoreboards'] and m['next_scoreboards'] == rm['next_scoreboards']
    assert m['baseline_manifest_sha256'] == rm['baseline_manifest_sha256']
    changed = []
    for n, v in m['sources'].items():
        if n in generated or n in ['runner.py', 'path_capacity_build.py']:
            changed.append(n)
        else:
            assert v['sha256'] == rm['sources'][n]['sha256'], n
    # Reconstruct the same audit-extracted native byte artifacts from the new
    # raw stream only after that entire trace has matched the reference.
    assert (p/case/'natural_trace.txt').read_bytes()==(ref/case/'natural_trace.txt').read_bytes()
    trace=[t.split()for t in(p/case/'natural_trace.txt').read_text().splitlines()]
    for tag,name,count in [('G3_PATH_WORD','native_g3_path.bin',78),('G3_QUERY_WORD','native_g3_query.bin',10)]:
        words=[int(t[3],16)for t in trace if t[0]==tag];assert len(words)==count
        (p/case/name).write_bytes(struct.pack('<'+'I'*count,*words))
    records=[t for t in trace if t[0]=='G3_LABEL_RECORD'];assert len(records)==781
    (p/case/'native_g3_labels.bin').write_bytes(b''.join(struct.pack('<I',int(t[2]))+int(t[3],16).to_bytes(20,'little')for t in records))
    compared = {}
    for q in (ref / case).iterdir():
        if q.is_file() and q.suffix in ['.txt', '.bin', '.dat']:
            target = p / case / q.name
            assert sha(q) == sha(target), q.name
            compared[q.name] = sha(target)
    assert all(name + '_axi.txt' in compared for name in ['graph','design','table','label','owner','cost','qstate','snapshot','copy','labelsnap','baseline','g3copy'])
    assert 'natural_trace.txt' in compared and 'owners.bin' in compared and 'g3.bin' in compared
    log = (p / case / 'simulate.log').read_text()
    assert 'G3_PUBLISH_PASS' in log and '$finish called' in log and 'Fatal:' not in log
    result = dict(status='passed', case=case, reference_audit_sha256=sha(ref / 'source_bound_audit.json'),
                  default_path_slots=2, byte_identical_files=compared, axi_interfaces=12,
                  native_trace_and_cycles_identical=True, changed_sources=changed,
                  scope='Default two-path full G3 fixture compatibility by exact raw trace, all12AXI and image identity to restored audited reference. Does not exercise slot2 in the complete hierarchy.')
else:
    for n, h in m['artifacts'].items(): assert sha(p / n) == h, n
    assert len(m['commands']) == 3 and all(x['exit_code'] == 0 for x in m['commands'])
    for root, h in m['input_audits'].items(): assert sha(Path(root) / 'source_bound_audit.json') == h
    log = (p / 'simulate.log').read_text(); assert 'Fatal:' not in log and '$finish called' in log
    rows = [s.split() for s in (p / 'events.txt').read_text().splitlines()]
    def by(tag): return [t for t in rows if t[0] == tag]
    mode = m['mode']
    if mode == 'path':
        base = p.parent / 'owner_g3_retired_full_v3'; third = p.parent / 'followup_iter2_third_v1'
        image = list(struct.unpack('<78I', (base / 'full/native_g3_path.bin').read_bytes()))
        path = json.loads((third / 'prepare_trace_audit.json').read_text())['path_sink_to_source']
        assert path == [151354,990179,558358,265324,66893]
        image += [1,3,26422,66893,151354,0x9abcdef0,0x12345678] + path[1:-1] + [0]*29
        assert [int(s,16) for s in (p / 'image.txt').read_text().split()] == image
        labels = {}
        with (third / 'search_final_nodes.u32').open('rb') as f:
            for node in path:
                f.seek(node*44); v=struct.unpack('<11I',f.read(44))
                labels[node]=sum(v[k]<<(32*j) for j,k in enumerate([0,1,3,4,5]))
        assert [(int(t[0]),int(t[1],16)) for t in map(str.split,(p/'labels.txt').read_text().splitlines())] == list(labels.items())
        assert [(int(t[1]),int(t[2]),int(t[3],16)) for t in by('L')] == [(5,n,v) for n,v in labels.items()]
        commands = [(0,3,151354),(1,3,151354),(1,2,67922),(1,2,151354),(0,2,151354),(1,1,67922),(1,2,151354),(1,0,204279)]
        assert len(by('Q'))==len(by('R'))==8
        for i,(q,r,want) in enumerate(zip(by('Q'),by('R'),commands),1):
            assert list(map(int,q[1:4])) == [i,want[0],want[1]]
            assert int(q[4],16)==0xabc00000+i and list(map(int,q[5:]))==[want[2],180329]
            assert list(map(int,r[1:]))==[i,1 if i<=3 else 0,0 if i<=3 else 3,0 if i<=3 else 3,[7,7,7,3,7,5,1,0][i-1]]
        refs={339193:1,990179:2,558358:4,265324:5}
        with(base/'full/owners.bin').open('rb') as f:
            for node,count in refs.items():
                f.seek(node*16); encoded_net,packed,head,reserved=struct.unpack('<4I',f.read(16))
                assert encoded_net==26423 and packed&0xffff==count and reserved==0
                assert packed>>16==({339193:1,990179:2,558358:2,265324:1}[node])
        expected=[]
        for qid,op,chain in [(4,2,path[1:-1]),(5,1,path[1:-1]),(6,2,path[1:-1]),(7,2,path[1:-1]),(8,2,[339193,558358,265324])]:
            for node in chain:
                new=refs[node]+(1 if op==1 else -1);expected.append([qid,op,node,refs[node],new]);refs[node]=new
        assert [list(map(int,t[1:])) for t in by('O')]==expected
        assert by('FINAL')==[['FINAL','5','15','0','0','1','2']]
        done=by('D'); assert len(done)==13
        statuses=[0,0,1,1,1,1,1,2,0,0,0,0,0]; masks=[7]*8+[3,7,7,7,0]
        assert [(int(t[1]),int(t[2]),int(t[4])) for t in done]==list(zip(range(13),statuses,masks))
        cmds=by('C');assert [int(t[1]) for t in cmds]==list(range(13))
        for cid in range(13):
            imported=[t for t in by('I') if int(t[1])==cid];exported=[t for t in by('E') if int(t[1])==cid]
            if int(cmds[cid][2]):
                assert not exported
                want=image.copy()
                if cid==3:want[86]=want[85]
                if cid==4:want[79]=33
                if cid==5:want[83]=0
                count=78 if cid==6 else 86 if cid==7 else 117
                assert [(int(t[2]),int(t[3],16),int(t[4])) for t in imported]==[(i,v,int(i==116 or cid==6 and i==77)) for i,v in enumerate(want[:count])]
                assert int(cmds[cid][3],16)==(crc(want)^(cid==2))
                assert int(done[cid][3],16)==(crc(want) if count==117 else 0)
            else:
                assert not imported
                want=image if cid in [1,9,11] else image[:78]+[0]*39 if cid==8 else [0]*117
                assert [(int(t[2]),int(t[3],16),int(t[4])) for t in exported]==[(i,w,int(i==116))for i,w in enumerate(want)]
                assert int(done[cid][3],16)==crc(want)
        assert 'PATH_CAPACITY_PASS checks=2494 cp=13 routes=8' in log
        result=dict(status='passed',mode=mode,checks=2494,path_slots=3,image_words=117,image_crc=f'{crc(image):08x}',native_owner_operations=15,native_label_reads=5,checkpoint_transactions=13,route_transactions=8,final_mock_refs=refs,
                    scope='Native controller with registered mock owner/label services. Captured G3 two paths plus real q3 historical path and CPU backtrace. No live DDR or full third-query search/warm proof.')
    elif mode.startswith('export'):
        default = mode=='export-default'; n=2 if default else 3
        image=[]
        for slot in range(n):image += [1,3,26422,66893,[204279,67922,151354][slot],0x9abcdef0,0x12345678,339193 if slot==0 else 990179,558358,265324]+[0]*29
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
                i=5 if default else 83;want[i]=(i,image[i]^1,0)
            if j==3:
                i=20 if default else 98;want[i]=(19,image[i],0)
            if j==11:want[79]=(79,33,0)
            if j==12:want=want[:78];want[-1]=(77,image[77],1)
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
                    scope='Synthetic native-export handshakes and parser/CRC; third slot schema/identity/length checked. No native controller or DDR persistence proof from this observer unit alone.')
    else:
        assert mode=='query'
        done=by('DONE');search={int(t[1]):tuple(map(int,t[2:]))for t in by('SEARCH')}
        modes=[0,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,0,21,0,22,23,25,26,27]
        statuses={0:0,1:1,2:1,3:2,4:2,5:3,6:4,7:4,8:4,9:5,10:5,11:5,12:6,13:6,14:7,15:8,16:7,17:7,18:7,19:0,21:1,22:1,23:7,25:0,26:1,27:1}
        assert len(done)==len(modes)
        for i,(t,scenario)in enumerate(zip(done,modes),1):
            d=list(map(int,t[1:]));assert d[:3]==[i,scenario,statuses[scenario]]
            assert d[3]==int(scenario in [0,11,12,13,18,19,25])
            ios=[t for t in by('IO')if int(t[1])==i]
            count=7 if scenario in [0,13,19,25]else 0 if scenario in [1,2,21,22,26,27]else 1 if scenario in [3,4,14,15,23]else 3 if scenario==5 else 6 if scenario==12 else 5
            source,sink,seq=(11,21,8)if i==2 else(10,10,7)if scenario==25 else(10,20,7)
            wanted=[(8,source<<1),(8,1|(sink<<1)|(1<<33)|(4<<65)),(8,1|(source<<1)),(8,1|(source<<1)|(1<<65)),(8,1|(source<<1)|(seq<<33)|(3<<65)),(8,1|(sink<<1)|(4<<65)),(6,1|(1<<2)|(3<<4)|(3<<8))]
            assert [(int(t[3]),int(t[4],16))for t in ios]==wanted[:count]
            assert sum(int(t[1])==i for t in by('SEARCH'))==int(scenario in [0,6,7,8,9,10,11,12,13,16,17,18,19,25])
            assert sum(int(t[1])==i for t in by('ROUTE'))==int(scenario in [0,9,10,11,12,13,18,19,25])
        packets=by('ROUTE');assert packets
        for t in packets:
            cmd=int(t[1]);v=int(t[2],16);source,sink,sequence=search[cmd]
            assert v&1==0 and (v>>1)&3==(1 if cmd==2 else 2)
            assert (v>>3)&0xffffffff==100+cmd
            assert [(v>>off)&0xffffffff for off in [35,67,99,131]]==[source,sink,5,sequence]
            assert v>>163==0
        assert done[-1][2:]==['27','1','0','0','0','0','0','0','0','0']
        assert not any(int(t[1])==int(done[-1][1]) for t in by('IO')+by('SEARCH')+by('ROUTE'))
        assert all(int(t[3])==0 and int(t[4])==1 for t in done if int(t[2]) in [0,19,25])
        checks=int(re.search(r'QUERY_LIFECYCLE_PASS checks=(\d+)',log).group(1));assert checks==len(done)
        result=dict(status='passed',mode=mode,checks=checks,path_slots=3,actual_route_offers=len(packets),unused_slot_encoding_rejected=True,
                    scope='Native query lifecycle with mock label/search/route responders; actual slot2 route payload and shifted cookie/source/sink/net/sequence verified. Not a full slot2 route backend integration.')

result.update(manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)))
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n')
print('PATH_CAPACITY_AUDITED',result.get('case',result.get('mode')))
