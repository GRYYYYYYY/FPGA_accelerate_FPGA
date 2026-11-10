"""Specialize only NORMAL-gated admission expressions; keep full fault semantics."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/combined_loops_synth_v1')

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def source(fixed):
    p = BASE / 'sources/recovery_coordinator.sv'
    m = json.loads((BASE / 'manifest.json').read_text())
    a = json.loads((BASE / 'source_bound_audit.json').read_text())
    proof = json.loads((ROOT / 'results/recovery_normal_identity_20261027.json').read_text())
    assert a['status'] == 'passed' and a['manifest_sha256'] == sha(BASE / 'manifest.json')
    assert sha(p) == m['sources'][p.name] == proof['source_sha256']
    assert proof['status'] == 'normal_admission_boolean_identity_not_rtl_validation'
    assert proof['valuations'] == 65536
    s = p.read_text()
    if fixed:
        marker = ' assign staged_valid='
        assert s.count(marker) == 1
        s = s.replace(marker, ''' // Only used under the existing state==NORMAL and !cold_rst gates.
 // No request is in AS/AW/OS/OW here; READY cannot qualify a reply.
 wire normal_unexpected=a_rsp_valid||o_rsp_valid;
 wire normal_fault=stopped||abort||timeout||normal_unexpected;
 assign staged_valid=''', 1)
        for name in ['staged_valid', 'permit_work', 'j_ready', 'recover_ready', 'cfg_ready']:
            lines = s.splitlines(keepends=True)
            matches = [i for i, line in enumerate(lines) if line.startswith(' assign ' + name + '=')]
            assert len(matches) == 1
            i = matches[0]
            assert 'state==NORMAL' in lines[i] and '!cold_rst' in lines[i] and '!fault' in lines[i]
            lines[i] = lines[i].replace('!fault', '!normal_fault')
            if name == 'recover_ready':
                assert '!unexpected' in lines[i]
                lines[i] = lines[i].replace('!unexpected', '!normal_unexpected')
            s = ''.join(lines)
    return s

if __name__ == '__main__':
    for mode in ['baseline', 'fixed']:
        d = HERE / mode
        d.mkdir()
        (d / 'recovery_coordinator.sv').write_text(source(mode == 'fixed'))
    print('RECOVERY_NORMAL_SOURCE_PREPARED')
