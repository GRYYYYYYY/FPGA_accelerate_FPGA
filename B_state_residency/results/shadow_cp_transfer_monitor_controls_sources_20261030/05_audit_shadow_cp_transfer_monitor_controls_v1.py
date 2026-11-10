"""Check transfer logger values against an independent fixed5-word sequence."""
from pathlib import Path
import json
import re
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,restored


def main():
    p=Path(sys.argv[1]).resolve();assert p==BASE/'shadow_cp_transfer_monitor_controls_v1'
    m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and not m.get('active_process')
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert m['runner_sha256']==sha(ROOT/'scripts/run_shadow_cp_transfer_monitor_controls_v1.py')
    assert m['monitor_sha256']==sha(ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv')
    ref=BASE/'shadow_cp_protocol_controls_v5';rm,_,_=restored(ref)
    assert set(m['cases'])=={'matching','ready_nba'};cases={}
    for mode,c in m['cases'].items():
        d=p/mode;assert c['status']=='observed'
        for name,h in c['inputs'].items():assert sha(d/name)==h
        for name in ['control.sv','shadow.sv','run.tcl']:
            assert sha(d/name)==rm['cases'][mode]['inputs'][name]
        assert sha(d/'monitor.sv')==m['monitor_sha256']
        assert [x['stage'] for x in c['commands']]==['compile','elaborate','simulate']
        for command in c['commands']:
            assert command['exit_code']==0 and sha(d/(command['stage']+'.stdout.log'))==command['stdout_sha256']
        log=(d/'simulate.stdout.log').read_text()
        assert 'Fatal:' not in log and log.count('CP_TRANSFER_MONITOR_END words=5')==1
        assert 'FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=345 qualified=cp_m_data' in log
        data=(d/'shadow_cp_export.log').read_text()
        rows=re.findall(r'^CP_WORD (\d+) (\d+) ([0-9a-f]{8}) ([01])$',data,re.M)
        assert len(rows)==len(data.splitlines())==5
        first=405000 if mode=='matching' else 415000
        expected=[(str(first+i*10000),str(i),f'{0xd00d0000+i:08x}',str(int(i==4))) for i in range(5)]
        assert rows==expected,(mode,rows)
        cases[mode]=dict(words=5,first_time_ps=first,last_time_ps=first+40000,log_sha256=sha(d/'shadow_cp_export.log'))
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(__file__),
                monitor_sha256=m['monitor_sha256'],cases=cases,full_system_functional_netlist_validated=False,
                scope='Read-only gate transfer logger captured each actual pre-clock payload/index/last for two legal5-word fake producers, including NBA-ready. Not actual FPGA netlist validation.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('CP_TRANSFER_LOGGER_CONTROLS_AUDITED',len(cases))


if __name__=='__main__':main()
