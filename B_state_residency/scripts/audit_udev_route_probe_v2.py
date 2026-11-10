"""Independently audit allocator controls and actual Vivado route/reopen observations."""
from pathlib import Path
import json
import re
import sys
from run_checkpoint_authority import ROOT, sha
from audit_state_ooc_physical_v2 import route_status, timing_summary

def main():
    p=Path(sys.argv[1]).resolve()
    m=json.loads((p/'manifest.json').read_text())
    assert m['status']=='observed' and m['stage']=='complete'
    assert not Path('/proc',str(m['pid'])).exists(), 'Runtime probe owner must finish'
    assert sha(p/'runner.py')==m['runner_sha256']==sha(ROOT/'scripts/run_udev_route_probe_v2.py')
    assert sha(ROOT/'hardware/scripts/probe_udev_route_v1.tcl')==m['tcl_sha256']
    assert sha(ROOT/'hardware/tests/udev_route_probe_v1.v')==m['fixture_sha256']
    for name,digest in m['libraries'].items(): assert sha(Path(name))==digest
    old=Path(m['predecessor'])
    assert sha(old/'manifest.json')==m['predecessor_manifest_sha256']
    om=json.loads((old/'manifest.json').read_text())
    assert om['status']=='failed' and om['stage']=='baseline' and om['cases']==m['cases'][:1]
    for name,digest in m['baseline_files_sha256'].items():
        assert sha(old/'baseline'/name)==digest==sha(p/'baseline'/name)
    controls=p.parent/'udev_allocator_probe_v1'
    cm=json.loads((controls/'manifest.json').read_text())
    assert cm['status']=='observed' and len(cm['cases'])==6
    assert cm['source_sha256']==sha(ROOT/'hardware/tests/probe_udev_allocator_v1.c')==sha(controls/'probe_udev_allocator_v1.c')
    assert cm['runner_sha256']==sha(ROOT/'scripts/run_udev_allocator_probe_v1.py')==sha(controls/'runner.py')
    assert cm['binary_sha256']==sha(controls/'probe')
    for name,entry in cm['libraries'].items():
        assert entry['sha256']==sha(Path(name))==m['libraries'][name]
    enumerations=[]
    for case in cm['cases']:
        assert sha(controls/case['log'])==case['sha256']
        text=(controls/case['log']).read_text()
        if case['label']=='tcmalloc_deepbind':
            assert case['exit_code']==-6 and 'realloc(): invalid pointer' in text
            assert 'ENUMERATED' not in text
        else:
            assert case['exit_code']==0
            match=re.search(r'ENUMERATED count=(\d+) ordered_syspath_fnv64=([0-9a-f]{16})',text)
            assert match and int(match[1])>0
            enumerations.append(match.groups())
    assert len(enumerations)==4 and len(set(enumerations))==1
    assert [c['label'] for c in m['cases']]==['baseline','preloaded_udev']
    observations={}
    for case in m['cases']:
        root=p/case['label']
        assert sha(root/'run.tcl')==m['tcl_sha256'] and sha(root/'fixture.v')==m['fixture_sha256']
        assert sha(root/'stdout.log')==case['stdout_sha256']
        text=(root/'stdout.log').read_text()
        if case['label']=='baseline' and case['exit_code']!=0:
            assert case['exit_code'] in [134,-6] and any(msg in text for msg in ['realloc(): invalid pointer','realloc(): invalid old size'])
            crashes=list(root.glob('hs_err_pid*.log')); assert len(crashes)==1
            crash=crashes[0].read_text()
            assert 'udev_enumerate_scan_devices' in crash and 'prepAndTransmitWebtalkData' in crash
            assert not (root/'routed.dcp').exists()
            observations[case['label']]=dict(exit_code=case['exit_code'],reopened=False,crash_sha256=sha(crashes[0]))
            continue
        assert case['exit_code']==0 and case['reopened']
        assert (root/'completed.txt').read_text().strip()=='UDEV_ROUTE_PROBE_REOPENED'
        assert not re.search(r'^ERROR:',text,re.M)
        assert 'Router Completed Successfully' in text
        assert 'implementation' in text and 'Got license' in text
        assert (root/'routed.dcp').stat().st_size>0
        route=route_status(root/'route_status.rpt')
        assert route==route_status(root/'route_status_reopened.rpt')
        assert route['routable nets']==route['fully routed nets']>0 and route['nets with routing errors']==0
        timing=timing_summary(root/'timing_routed.rpt')
        assert timing==timing_summary(root/'timing_reopened.rpt')
        if case['label']=='preloaded_udev':
            assert case['preload']==':'.join(cm['libraries'].keys()) or set(case['preload'].split(':'))==set(cm['libraries'])
            maps=(root/'runtime_maps.txt').read_text()
            assert 'libudev.so.' in maps and 'libtcmalloc.so.4' in maps
        observations[case['label']]=dict(exit_code=0,reopened=True,route=route,timing=timing)
    wt=p.parent/'webtalk_runtime_probe_v1'
    assert json.loads((wt/'manifest.json').read_text())['exit_code']==0
    wlog=(wt/'stdout.log').read_text()
    assert 'WebTalk has been disabled by the current user.' in wlog
    assert 'WebTalk has been disabled for the current installation.' in wlog
    files={str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and not f.is_symlink() and f.name!='source_bound_audit.json'}
    external={str(f):sha(f) for root in [controls,wt] for f in sorted(root.rglob('*')) if f.is_file() and not f.is_symlink()}
    result=dict(status='passed',audit_kind='runtime workaround control evidence, not full-system acceptance',
                manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
                report_parser_sha256=sha(ROOT/'scripts/audit_state_ooc_physical_v2.py'),
                allocator_controls=dict(crashes=2,normal_passes=2,preloaded_passes=2,
                                        enumerated_count=int(enumerations[0][0]),ordered_syspath_fnv64=enumerations[0][1]),
                vivado_controls=observations,artifact_sha256=files,external_evidence_sha256=external,
                runtime_library_sha256=m['libraries'],timing_qualified=False,board_acceptance=False,
                scope='Original libudev and bundled tcmalloc are preloaded only in new child processes. '
                      'No device enumeration stub, license change, persistent setting or tool binary patch. '
                      'Small fixture success does not prove full-system recovery or identical physical timing.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('UDEV_ROUTE_RUNTIME_AUDITED',observations,flush=True)

if __name__=='__main__': main()
