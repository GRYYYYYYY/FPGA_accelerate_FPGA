"""Independently compare both logger runs to explicit five-beat gold tuples/times."""
from pathlib import Path
import json,re,sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity
from check_shadow_payload_transfer_logs_v1 import check_ka,check_pw


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'shadow_payload_monitor_controls_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete'
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert m['runner_sha256']==sha(ROOT/'scripts/run_shadow_payload_monitor_controls_v1.py')
    assert m['checker_sha256']==sha(ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5/shadow.sv')
    assert m['payload_monitor_sha256']==sha(ROOT/'hardware/tests/tb_shadow_payload_transfer_monitor_v1.sv')
    assert m['cp_monitor_sha256']==sha(ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv')
    assert m['parent_control_report_sha256']==sha(ROOT/'results/shadow_payload_contract_controls_20261030.json')
    assert set(m['cases'])=={'matching','ready_nba'}
    gold_ka=[(17,0xa0000000+i,0xb0000000+i,0x11110000+i) for i in range(5)]
    gold_w=[(0x1000+64*i,0xffffffffffffffff,0xc0000000+i) for i in range(5)]
    cases={}
    for name in ['matching','ready_nba']:
        c=m['cases'][name];d=p/name;assert c['status']=='observed'
        for n,h in {**c['inputs'],**c['transfer_log_sha256']}.items():assert sha(d/n)==h
        assert sha(d/'shadow.sv')==m['checker_sha256']
        assert sha(d/'payload_monitor.sv')==m['payload_monitor_sha256'] and sha(d/'cp_monitor.sv')==m['cp_monitor_sha256']
        for cmd in c['commands']:assert cmd['exit_code']==0 and sha(d/(cmd['stage']+'.stdout.log'))==cmd['stdout_sha256']
        assert [cmd['stage'] for cmd in c['commands']]==['compile','elaborate','simulate']
        a=c['commands'][0]['argv'];macros=[a[i+1] for i,v in enumerate(a) if v=='-d'];assert macros==['SHADOW_NETLIST_TOP=protocol_gate']+(['READY_NBA'] if name=='ready_nba' else [])
        log=(d/'simulate.stdout.log').read_text();assert 'Fatal:' not in log and '$finish called at time : 1202 ns' in log
        assert re.findall(r'^PAYLOAD_TRANSFER_MONITOR_END ka=(\d+) pw=(\d+) aw=(\d+)$',log,re.M)==[('5','5','1')]
        assert re.findall(r'^CP_TRANSFER_MONITOR_END words=(\d+)$',log,re.M)==['5']
        first=415000 if name=='ready_nba' else 405000
        expected_times=list(range(first,first+50000,10000))
        ka=(d/'shadow_ka_requests.log').read_text();pw=(d/'shadow_pw_beats.log').read_text()
        kr=check_ka(ka,gold_ka,0x1234);wr=check_pw(pw,gold_w)
        assert [int(line.split()[1]) for line in ka.splitlines()]==expected_times
        assert [int(line.split()[1]) for line in pw.splitlines() if line.startswith('PW_W ')]==expected_times
        assert [int(line.split()[1]) for line in pw.splitlines() if line.startswith('PW_AW ')]==[first]
        rows=re.findall(r'^CP_WORD (\d+) (\d+) ([0-9a-fA-F]{8}) ([01])$',(d/'shadow_cp_export.log').read_text(),re.M)
        assert len(rows)==5 and [int(r[0]) for r in rows]==expected_times
        assert [(int(i),int(data,16),int(last)) for _,i,data,last in rows]==[(i,0xd00d0000+i,int(i==4)) for i in range(5)]
        cases[name]=dict(authority=kr,pager_write=wr,cp_words=5,transfer_times_ps=expected_times)
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),parser_sha256=sha(ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py'),cases=cases,payload_monitor_sha256=m['payload_monitor_sha256'],cp_monitor_sha256=m['cp_monitor_sha256'],full_system_functional_netlist_validated=False,scope='Read-only logger calibration on two legal5-beat fake-model streams; explicit independent gold times, authority fields, AXI addresses/data/strobes/last, CP index/data/last. No actual FPGA netlist result.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print('THREE_STREAM_LOGGER_CONTROLS_INDEPENDENTLY_AUDITED')


if __name__=='__main__':main()
