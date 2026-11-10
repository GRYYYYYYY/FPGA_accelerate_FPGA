"""Independently decode every streamed word and response in three RTL modes."""
from pathlib import Path
import json
import re
import sys
import zlib
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity


def check_trace(text):
    image=[0]*156
    for slot in range(4):
        image[slot*39:slot*39+7]=[1,32,3+slot,1,2,0x9abcdef0,0x12345678]
        image[slot*39+7:slot*39+39]=list(range(10+slot*100,42+slot*100))
    statuses=[0,0,0,1,0,1,0,2,0,1,0,0]
    imports={0:(156,0),3:(156,1),5:(156,2),7:(5,3),9:(4,4)}
    groups=[];active=None;cases=[];terminal=[]
    for line in text.splitlines():
        row=line.split()
        if row[:2]==['EVT','C']:
            assert active is None and int(row[3])==len(groups)
            active=dict(command=row,inputs=[],outputs=[])
        elif row[:2]==['EVT','I']:
            assert active is not None;active['inputs'].append(row)
        elif row[:2]==['EVT','O']:
            assert active is not None;active['outputs'].append(row)
        elif row[:2]==['EVT','R']:
            assert active is not None;active['response']=row;groups.append(active);active=None
        elif row[:1]==['CASE']:cases.append(line)
        elif row[:1]==['STAGE_BANK_MATRIX_PASS']:terminal.append(line)
        else:raise AssertionError(line)
    assert active is None and len(groups)==len(cases)==12 and len(terminal)==1
    counts=dict(imports=0,exports=0)
    for i,g in enumerate(groups):
        restore=i in imports;assert int(g['command'][4])==int(restore)
        response=g['response'];assert int(response[3])==i and int(response[4])==statuses[i]
        assert response[6]==('0000' if i==11 else '1111')
        if restore:
            length,kind=imports[i];assert not g['outputs'] and len(g['inputs'])==length
            words=image.copy()
            if kind==1:words[7]=777
            if kind==2:words[38]=words[37]
            for n,row in enumerate(g['inputs']):
                assert int(row[3])==(4 if kind==4 and n==3 else n)
                assert int(row[4],16)==words[n] and int(row[5])==int(n==155)
            if length==156:
                crc=zlib.crc32(b''.join(w.to_bytes(4,'little') for w in words))
                assert int(response[5],16)==crc
            counts['imports']+=length
        else:
            words=[0]*156 if i==11 else image
            assert not g['inputs'] and len(g['outputs'])==156
            for n,row in enumerate(g['outputs']):
                assert int(row[3])==n and int(row[4],16)==words[n] and int(row[5])==int(n==155)
            assert int(response[5],16)==zlib.crc32(b''.join(w.to_bytes(4,'little') for w in words))
            counts['exports']+=156
    assert counts==dict(imports=477,exports=1092)
    assert terminal==['STAGE_BANK_MATRIX_PASS commands=12 responses=12 imports=477 exports=1092 checks=12 cycles=23245']
    return dict(commands=12,responses=12,**counts,cycles=23245,finish_ns=232450)


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'stage_bank_matrix_rtl_v2'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_bank_matrix_rtl_v2.py')
    variant=ROOT/'hardware/variants/stage_static_cp_v1';vm=read(variant/'manifest.json')
    artifacts={};traces=[];coverage={}
    for mode in ['original','default','static']:
        c=m['cases'][mode];assert c['status']=='observed'
        assert [x['stage'] for x in c['commands']]==['compile','elaborate','simulate']
        assert all(x['exit_code']==0 for x in c['commands']) and '--O0' in c['commands'][1]['argv']
        for n,h in c['inputs'].items():assert sha(p/mode/n)==h
        assert sha(p/mode/'controller.sv')==vm['baseline_sha256' if mode=='original' else 'fixed_sha256']
        assert sha(p/mode/'tb.sv')==m['tb_sha256']==sha(ROOT/'hardware/tests/tb_stage_bank_matrix_v1.sv')
        log=(p/mode/'simulate.stdout.log').read_text();assert 'Fatal:' not in log
        trace='\n'.join(re.findall(r'^(?:EVT |CASE |STAGE_BANK_MATRIX_PASS).*$',log,re.M))+'\n'
        assert trace==(p/mode/'events.txt').read_text() and sha(p/mode/'events.txt')==c['events_sha256']
        coverage[mode]=check_trace(trace);traces.append(trace)
        assert re.findall(r'\$finish called at time : (\d+) ns',log)==['232450']
        for n in list(c['inputs'])+['compile.stdout.log','elaborate.stdout.log','simulate.stdout.log','events.txt']:
            artifacts[mode+'/'+n]=sha(p/mode/n)
    assert traces[0]==traces[1]==traces[2]
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        artifact_sha256=artifacts,coverage=coverage,complete_cycle_data_event_comparisons=2,
        timing_qualified=False,scope=m['scope'],post_synthesis_functional_pending=True)
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STAGE_BANK_MATRIX_RTL_AUDITED',coverage)


if __name__=='__main__':main()
