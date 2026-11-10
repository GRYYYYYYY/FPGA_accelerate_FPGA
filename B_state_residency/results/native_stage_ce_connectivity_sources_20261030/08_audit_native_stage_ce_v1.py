"""Audit literal routed leaf connectivity without treating Tcl records as code."""
from pathlib import Path
import json
import re
import subprocess
import sys
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == BASE/'native_stage_ce_connectivity_v1'
    m = read(p/'manifest.json')
    assert m['status'] == 'observed' and m['stage'] == 'complete' and m['exit_code'] == 0
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert m['runner_sha256'] == sha(ROOT/'scripts/inspect_native_stage_ce_v1.py')
    assert sha(p/'inspect.tcl') == m['tcl_sha256']
    for name, digest in m['artifact_sha256'].items(): assert sha(p/name) == digest
    source = Path(m['source_root'])
    assert sha(source/'routed.dcp') == m['dcp_sha256']
    assert sha(source/'source_bound_audit.json') == m['source_audit_sha256']
    parser = ROOT/'scripts/read_tcl_list_records.tcl'
    parsed = subprocess.run(['tclsh', str(parser), str(p/'connectivity.tcllist')],
        check=True, capture_output=True, text=True)
    rows = [[bytes.fromhex(x).decode() for x in line.split('\t')]
            for line in parsed.stdout.splitlines()]
    net = [r for r in rows if r[0] == 'NET']; assert len(net) == 1
    pins = [r for r in rows if r[0] == 'PIN']
    assert len(pins) == int(net[0][3]) == 4993
    assert len({r[1] for r in pins}) == len(pins)
    loads = [r for r in pins if r[3] == 'IN']
    drivers = [r for r in pins if r[3] == 'OUT']
    assert len(loads) == 4992 and len(drivers) == 1
    actual = set()
    for row in loads:
        assert len(row) == 10 and row[5] == 'CE' and row[9] == 'FDRE'
        match = re.fullmatch(r'inner/backend/route_join/controller/cp_stage_reg\[(\d+)\]\[(\d+)\]/CE', row[1])
        assert match, row
        assert row[7] == row[1][:-3]
        actual.add(tuple(map(int, match.groups())))
    assert actual == {(word, bit) for word in range(156) for bit in range(32)}
    driver = [r for r in rows if r[0] == 'DRIVER' and r[1] == '0']
    assert len(driver) == 1 and driver[0][4:] == ['LUT3', 'INIT', "8'h02"]
    assert drivers[0][7] == driver[0][2]
    log = (p/'stdout.log').read_text()
    assert 'NATIVE_STAGE_CE_CONNECTIVITY_DONE' in log and not re.search(r'^ERROR:', log, re.M)
    result = dict(status='passed', manifest_sha256=sha(p/'manifest.json'),
        auditor_sha256=sha(Path(__file__)), parser_sha256=sha(parser),
        net=net[0][1], actual_stage_ce_loads=len(loads), stage_words=156, bits_per_word=32,
        exact_complete_stage_ce_pin_coverage=True, driver=driver[0],
        driver_two_state_equation='O = I0 & ~I1 & ~I2 (LUT3 INIT 8h02)',
        lut_driver_records=[r for r in rows if r[0] == 'DRIVER'],
        unmatched_upstream_warnings=[l for l in log.splitlines() if 'No pins matched' in l],
        artifact_sha256=m['artifact_sha256'], dcp_sha256=m['dcp_sha256'],
        timing_qualified=False, scope='Actual single-net leaf connectivity and bounded LUT neighborhood only. '
            'Two-state LUT equation is not four-state RTL equivalence, control-event attribution, '
            'complete transitive fanin, or optimization benefit.')
    (p/'source_bound_audit.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('NATIVE_STAGE_CE_AUDITED', len(loads), 'complete bank CE pins')


if __name__ == '__main__': main()
