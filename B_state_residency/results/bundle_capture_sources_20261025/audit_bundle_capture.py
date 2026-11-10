"""Independent full CPU query/label/owner and eight AXI channel audit."""
from pathlib import Path
from collections import Counter
import json,mmap,struct,sys,types,zlib,subprocess
from decode_bundle_directory import decode
from verify_rtl_bundle import verify
from run_query_fault import sha,ROOT
from audit_route_fault_axi import replay

def main():
    out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());partial='--partial'in sys.argv[2:];before_bundle='--before-bundle'in sys.argv[2:];authority_fault=m.get('authority_fault',False);assert m['status']=='observed'or partial
    base=Path(m['base']);bm=json.loads((base/'manifest.json').read_text());inp=Path(m['input'])
    assert sha(base/'manifest.json')==m['base_manifest_sha256']and sha(base/'source_bound_audit.json')==m['base_audit_sha256']
    for n,h in m['sources'].items():assert sha(out/'sources'/n)==h['sha256']
    ns={'__file__':str(ROOT/'hardware/variants/bundle_capture_v1/build.py'),'__name__':'frozen_query_join'};exec(compile((out/'sources/capture_build.py').read_text(),'qcp_build.py','exec'),ns);ns['BASE']=base/'sources';replacements=ns['make']()
    for n,text in replacements.items():assert text==(out/'sources'/n).read_text()
    changed=set(replacements)
    for n,h in m['sources'].items():
        if n not in changed|{'runner.py','capture_build.py','capture_tb_build.py','tb_query_fault.sv','tb_directory_observer.sv'}:assert h['sha256']==bm['sources'][n]['sha256']
    tbns={'__file__':str(ROOT/'hardware/variants/bundle_capture_v1/build_tb.py'),'__name__':'frozen_join_tb'};exec(compile((out/'sources/capture_tb_build.py').read_text(),'qcp_tb_build.py','exec'),tbns);tbns['BASE']=base/'sources/tb_query_fault.sv';assert tbns['make']()==(out/'sources/tb_query_fault.sv').read_text()
    assert m['bundle_capture']and not authority_fault and m['expected_cases']==['full_5','pressure_5']
    cpu=ROOT/'results/natural_query_v2';graph=ROOT/'results/graph_image_20261024'
    oracle=Path('/tmp/B_state_residency_offer_20261025/continuous_oracle_v1')
    def records(p):return {r[0]:list(r[1:]) for r in struct.iter_unpack('<6I',p.read_bytes())}
    imports=records(oracle/'initial_label_imports.u32');final=records(oracle/'expected_label_reads.u32');final[150697][4]=0
    lines=[l.split() for l in (cpu/'events.txt').read_text().splitlines()]
    expected_p=[[int(x) for x in t[1:4]] for t in lines if t[0]=='P']
    expected_o=[[int(t[1]),int(t[2]),int(t[3]),int(i+1<len(lines) and lines[i+1][0]=='W')] for i,t in enumerate(lines) if t[0]=='C']
    costs=[]
    for t in map(str.split,(inp/'cost_vectors.txt').read_text().splitlines()):
        costs.append((int(t[1]),sum(int(v,16)<<(32*j) for j,v in enumerate(t[2:25])),sum(int(v,16)<<(32*j) for j,v in enumerate(t[25:]))))
    with (cpu/'search_final_nodes.u32').open('rb') as f,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ) as mm:
        chain=[150697]
        while chain[-1]!=65185:
            n=struct.unpack_from('<I',mm,chain[-1]*44+12)[0];assert n!=0xffffffff and len(chain)<32;chain.append(n)
    interiors=chain[1:-1];assert len(interiors)==6
    original=(inp/'owners.bin').read_bytes()+(inp/'owner_allocator.bin').read_bytes()
    committed=bytearray(original)
    for n in interiors:
        assert struct.unpack_from('<4I',committed,n*16)==(0,0,0,0)
        struct.pack_into('<4I',committed,n*16,2718,65537,0,0)
    report={}
    if not partial:
        expected=m.get('expected_cases',['full_1','full_3','full_4','full_5','full_6','pressure_1','pressure_2','pressure_3','pressure_4','pressure_5','pressure_6'])
        assert set(m['cases'])==set(expected)
    for name,cm in m['cases'].items():
        if partial and cm['status']!='observed':continue
        d=out/name;assert cm['status']=='observed'
        if m.get('route_fix') or m.get('search_fix'):assert cm['outcome']=='recovered_retry'
        for n,h in cm['artifacts'].items():assert sha(d/n)==h
        ts=[l.split() for l in (d/'natural_trace.txt').read_text().splitlines()]
        def by(tag):return [t for t in ts if t[0]==tag]
        assert len(by('FI'))==1
        fi=by('FI')[0];fc=cm['faultcase'];assert int(fi[2])==fc
        if m.get('search_fix') and fc in [3,4] and 'fault_after' in cm:assert len(by('FAULT_OWNER'))==1 and int(by('FAULT_OWNER')[0][3])==cm['fault_after']
        expected_phase={1:(2,0),3:(4,4),4:(4,4),5:(6,4),6:(2,6)}
        if fc==2:assert int(fi[3])==2 and 1<=int(fi[4])<=4 and cm['mode']=='pressure'
        else:assert tuple(map(int,fi[3:5]))==expected_phase[fc]
        assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)] for t in by('I')}==imports
        memory={}
        regions=[('graph',[(0x1fffff000,graph/'offsets.u32le'),(0x10fffff000,graph/'edges.u32le'),(0x20fffff000,graph/'nodes.rrt32')],None),
                 ('design',[(0x31fffff000,inp/'design.bin')],d/'design.bin'),('label',[(0,bytes(3145728))],d/'labels.bin'),
                 ('owner',[(0x61fffff000,original)],d/'owners.bin'),('cost',[(0x71fffff000,inp/'cost.bin')],None),
                 ('qstate',[(0x81fffff000,inp/'connections.bin')],None),('table',[(0x41fffff000,inp/'rows.bin'),(0x51fffff000,inp/'columns.bin')],None)]
        for tag,rr,ff in regions:memory[tag]=replay(d/(tag+'_axi.txt'),rr,ff)
        assert sha(d/'cost.bin')==sha(inp/'cost.bin')
        expected_error={1:('label','error_read_beats'),2:('label','error_write_replies'),3:('graph','error_read_beats'),4:('cost','error_read_beats'),5:('owner','error_write_replies'),6:('label','error_write_replies')}[fc]
        for tag,v in memory.items():
            for key in ['error_read_beats','error_write_replies']:assert v[key]==int((tag,key)==expected_error),(name,tag,key,v[key])
        assert sha(d/'primary.bin')==sha(inp/'owners.bin')and sha(d/'allocator.bin')==sha(inp/'owner_allocator.bin')and (d/'pool.bin').stat().st_size==0
        snapshot=replay(d/'snapshot_axi.txt',[(0x91fffff000,d/'primary.bin'),(0x9208aaef40,d/'allocator.bin')]);assert snapshot['error_read_beats']==int(authority_fault)and snapshot['error_write_replies']==snapshot['write_beats']==0
        bind=by('AS_BIND');assert len(bind)==1 and [int(bind[0][2],16),int(bind[0][3]),int(bind[0][4],16)]==[0x123456789abcdef0,17,0x100000001]
        aa=by('KA');ab=by('AS_REPLY');assert len(aa)==len(ab)==2+int(authority_fault)and snapshot['read_transactions']==4+int(authority_fault)
        for a,b in zip(aa,ab):
            cp,node,net,cookie=map(int,a[2:]);key,packed,head,rsv=struct.unpack_from('<4I',original,node*16);assert cp==17 and head==rsv==0 and int(a[1])<int(b[1]);assert list(map(int,b[2:5]))==([9,0,0]if authority_fault and a==aa[0]else [0,(packed&65535)if key==net+1 else 0,packed>>16])and int(b[5],16)==0x100000001
        memory['snapshot']=snapshot
        # The added ledger flow may not alter any of the existing physical services.
        equal_files=['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin']
        for f in equal_files:assert sha(d/f)==sha(base/name/f),(name,f)
        qcp={}
        by_id=lambda tag,i:[t for t in by(tag)if int(t[1])==i]
        image=[0x51435031,1,0x9abcdef0,0x12345678,2,1,4,82,1,0];current=image.copy();current[4]=1;cr=lambda w:zlib.crc32(struct.pack('<10I',*w))
        for i,w in [(1,image),(3,current)]:assert [(int(t[2]),int(t[3],16),int(t[4]))for t in by_id('QCM',i)]==[(j,x,int(j==9))for j,x in enumerate(w)]
        for i,w in [(2,image),(4,current)]:assert [(int(t[2]),int(t[3],16),int(t[4]))for t in by_id('QCS',i)]==[(j,x,int(j==9))for j,x in enumerate(w)]
        cp=by('QCP');assert len(cp)==5 and [int(t[2])for t in cp]==[1,0,1,0,0]and [int(t[4])for t in cp]==[0,0,1,1,1]and all(t[5]=='1'for t in cp)
        assert [int(t[3],16)for t in cp]==[0,cr(image),cr(image),cr(current),cr(current)]
        assert len(by('BREADY'))==len(by('BCFG'))==len(by('BCONTEXT'))==len(by('BFLOORS'))==1
        ready=by('BREADY')[0];assert ready[4:]==['6','1','0','0']and int(ready[2],16)==cr(image)
        pw=[int(t[2],16)for t in by('BPATH')];assert len(pw)==78 and all(int(t[1])==i and int(t[3])==int(i==77)for i,t in enumerate(by('BPATH')))
        expectedpath=[1,6,2717,65185,150697,0x9abcdef0,0x12345678]+interiors+[0]*26+[0]*39
        assert pw==expectedpath and int(ready[3],16)==zlib.crc32(struct.pack('<78I',*pw))
        assert by('BCONTEXT')[0][1:]==['123456789abcdef0','0000000100000002','17','4','2','4','4','1','1']and by('BFLOORS')[0][1:]==['4','2','4','4','2']
        assert [(int(t[2]),int(t[3]))for t in by('BJ')]==[(n,2717)for n in interiors]
        directory,recordmap=decode(d/'directory.txt',d/'labels.bin',2,4);assert directory['allocated']==120 and len(recordmap)==328 and recordmap==final
        assert sha(out/'sources/tb_directory_observer.sv')==m['sources']['tb_directory_observer.sv']['sha256']and all('--define'in x['argv']and 'BUNDLE_TRACE'in x['argv']for x in m['builds'][cm['mode']]['commands']if x['stage']=='compile')
        if not before_bundle:
            bundle=verify(d/'bundle');assert bundle['source_hashes']['natural_trace.txt']==sha(d/'natural_trace.txt')and bundle['source_hashes']['directory.txt']==sha(d/'directory.txt')
            assert (d/'bundle/owner_primary.bin').read_bytes()+(d/'bundle/owner_allocator.bin').read_bytes()==(d/'owners.bin').read_bytes()
            for f in ['labels.bin','design.bin','cost.bin']:assert sha(d/'bundle'/f)==sha(d/f)
        qcp={'target_generation':0x100000002,'current_generation_preserved':0x100000001,'query_crc32':cr(image),'path_crc32':int(ready[3],16),'absorbed_journal_count':6,'directory_frames':120,'label_records':328,'directory_commands':directory['protocol_commands'],'directory_reconstruction':'passive real RTL request/response trace; not a production export port','bundle_committed':not before_bundle}
        entry={'query_checkpoint':qcp,'outcome':cm['outcome'],'fault_cycle':int(fi[1]),'memory':memory,'owner_sha256':sha(d/'owners.bin')}
        if cm['outcome']=='stalled':
            assert len(by('STALLED'))==len(by('OWNED'))==1
            assert not by('RESET') and not by('FK') and not by('RETRY') and not by('LIFECYCLE')
            if fc==5:
                assert [[int(t[3]),int(t[4])] for t in by('RO')]==[[1,interiors[0]]]
                partial_owner=bytearray(original);struct.pack_into('<4I',partial_owner,interiors[0]*16,2718,65537,0,0)
                assert (d/'owners.bin').read_bytes()==partial_owner
            else:assert (d/'owners.bin').read_bytes()==original
            entry['stalled_state']=' '.join(by('STALLED')[0]);entry['owned_state']=' '.join(by('OWNED')[0])
        else:
            assert cm['outcome']=='recovered_retry'
            for tag in ['FAILED_QUERY','FK','RESET','KD','LD','RETRY','LIFECYCLE']:assert len(by(tag))==(2 if authority_fault and tag in ['FK','RESET']else 1),(name,tag)
            if authority_fault:
                af=by('AS_FAIL');ar=by('AS_REARM');assert len(af)==len(ar)==1 and af[0][2:]==['6','0','1']and int(ar[0][2],16)==0x100000001
                assert int(by('RESET')[0][1])<int(af[0][1])<int(ar[0][1])<int(by('RESET')[1][1])<int(by('KD')[0][1])
            else:assert not by('AS_FAIL')and not by('AS_REARM')
            fq=by('FAILED_QUERY')[0];assert int(fq[3])!=0
            assert int(fi[1])<int(fq[1])<int(by('FK')[0][1])<int(by('RESET')[0][1])<int(by('KD')[0][1])<int(by('RETRY')[0][1])
            assert by('LD')[0][2:]==['0','328','328'] and by('KD')[0][2]=='0' and by('RETRY')[0][2:]==(['3','5']if authority_fault else ['2','4'])
            repairs=1 if fc==5 else 6 if fc==6 else 0
            assert int(by('KD')[0][3])==repairs
            owner_state=bytearray(original);write_replies=0
            for t in map(str.split,(d/'owner_axi.txt').read_text().splitlines()):
                if t[0]=='W':
                    offset=int(t[1],16)-0x61fffff000;mask=int(t[2],16);data=int(t[3],16).to_bytes(64,'little')
                    for j in range(64):
                        if mask>>j&1:owner_state[offset+j]=data[j]
                elif t[0]=='B':
                    write_replies+=1
                    if repairs and write_replies==2*repairs:assert owner_state==original
            assert write_replies==2*repairs+6
            assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)] for t in by('CHECK')}==imports
            retry=int(by('RETRY')[0][1])
            def after(tag):return [t for t in by(tag) if int(t[1])>retry]
            assert [[int(t[2]),int(t[3],16),int(t[4])] for t in after('P')]==expected_p
            assert [[int(t[3]),int(t[4]),int(t[6]),int(t[5])] for t in after('O')]==expected_o
            assert [(int(t[2]),int(t[3],16),int(t[4],16)) for t in after('C')]==costs
            assert len(after('Q'))==72 and after('SEARCH')[0][2:]==['0','0','73','72','271']
            assert by('LIFECYCLE')[0][2:]==['0','0','1','4','1','6','6']
            assert [int(t[3]) for t in after('RL')]==chain
            assert [[int(t[3]),int(t[4])] for t in after('RO')]==[[1,n] for n in interiors]
            assert [t[3:] for t in after('RB')]==[['0','1','1']]*6
            assert {int(t[2]):[(int(t[3],16)>>(32*j))&0xffffffff for j in range(5)] for t in by('Z')}==final
            assert (d/'owners.bin').read_bytes()==committed
            entry.update(repairs=int(by('KD')[0][3]),failure_status=int(fq[3]),failure_detail=int(fq[4]),reported_committed=int(fq[5]),confirmed_acks=int(fq[6]),retry_polls=len(after('P')),retry_candidates=len(after('O')),retry_costs=len(after('C')))
        report[name]=entry
        print(name,cm['outcome'],'audited',flush=True)
    assert all(c['outcome']=='recovered_retry'for c in m['cases'].values()if not partial or c['status']=='observed')
    integrity_sha=None
    if not before_bundle and not partial:
        completed=subprocess.run([sys.executable,str(ROOT/'scripts/test_rtl_bundle_integrity.py'),str(out)],capture_output=True,text=True);assert completed.returncode==0,completed.stderr
        integrity=json.loads((out/'bundle_integrity_tests.json').read_text());assert integrity['status']=='passed'and integrity['checks']==24 and integrity['source_bundles_unchanged']and integrity['verifier_sha256']==sha(ROOT/'scripts/verify_rtl_bundle.py')and integrity['script_sha256']==sha(ROOT/'scripts/test_rtl_bundle_integrity.py');integrity_sha=sha(out/'bundle_integrity_tests.json')

    result={'checkpoint_inactive':False,'query_checkpoint_join':False,'bundle_capture':True,'integrity_tests_sha256':integrity_sha,'status':'passed','meaning':'Evidence integrity and stated outcomes verified; stalled cases are recovery failures.',
            'manifest_sha256':sha(out/'manifest.json'),'audit_script_sha256':sha(Path(__file__)),
            'replay_script_sha256':sha(ROOT/'scripts/audit_route_fault_axi.py'),'directory_decoder_sha256':sha(ROOT/'scripts/decode_bundle_directory.py'),'bundle_verifier_sha256':sha(ROOT/'scripts/verify_rtl_bundle.py'),'package_script_sha256':sha(ROOT/'scripts/package_rtl_bundle.py'),
            'outcomes':dict(Counter(v['outcome'] for v in report.values())),'cases':report,
            'limits':['Healthy-boundary reference bundle capture, not cold restore or runtime namespace activation; directory metadata uses passive protocol tracing.','Whole physical memories replayed; no general proof of retained design cache validity after arbitrary failures.','No timing/board performance evidence.']}
    if partial:result['status']='partial';result['meaning']='Only finished cases audited; manifest still may change.'
    (out/('partial_audit.json' if partial else 'prebundle_audit.json' if before_bundle else 'source_bound_audit.json')).write_text(json.dumps(result,indent=2)+'\n')
if __name__=='__main__':main()
