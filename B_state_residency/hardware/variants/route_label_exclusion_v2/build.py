"""Prepare an isolated default-off label-only route exclusion candidate."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_synth_v1')
NAMES = ['route_commit_controller.sv', 'route_commit_host_adapter.sv', 'residency_system.sv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(fixed):
    proof = json.loads((ROOT/'results/route_label_exclusion_20261028.json').read_text())
    assert proof['status'] == 'native_route_label_two_state_exclusion_not_rtl_validation'
    assert proof['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_label_exclusion.py')
    manifest = json.loads((BASE/'manifest.json').read_text())
    result = {}
    for name in NAMES:
        path = BASE/'sources'/name
        assert sha(path) == proof['source_sha256'][name] == manifest['sources'][name]
        original = path.read_text()
        text = original
        if fixed and name in NAMES[:2]:
            old = 'parameter integer PATH_SLOTS=2,'
            assert text.count(old) == 1
            text = text.replace(old, 'parameter integer LABEL_RESPONSE_EXCLUSIVE=0,PATH_SLOTS=2,')
        if fixed and name == NAMES[0]:
            old = '(l_rsp_valid&&state!=LW&&!(state==LS&&l_ready))'
            assert text.count(old) == 1
            text = text.replace(old, '(LABEL_RESPONSE_EXCLUSIVE!=0?(l_rsp_valid&&state!=LW):'+old+')')
            # Leave owner semantics and every sequential statement intact.
            assert text.split(' always @(posedge clk)begin', 1)[1] == original.split(' always @(posedge clk)begin', 1)[1]
        elif fixed and name == NAMES[1]:
            old = 'route_commit_controller #(.PATH_SLOTS(PATH_SLOTS),'
            assert text.count(old) == 1
            text = text.replace(old, 'route_commit_controller #(.LABEL_RESPONSE_EXCLUSIVE(LABEL_RESPONSE_EXCLUSIVE),.PATH_SLOTS(PATH_SLOTS),')
        elif fixed:
            assert 'EXCLUSIVE_BACKEND_RESPONSES=0' in text
            old = 'route_commit_host_adapter #(.PATH_SLOTS(PATH_SLOTS),'
            assert text.count(old) == 1
            text = text.replace(old, 'route_commit_host_adapter #(.LABEL_RESPONSE_EXCLUSIVE(EXCLUSIVE_BACKEND_RESPONSES),.PATH_SLOTS(PATH_SLOTS),')
        result[name] = text
    return result


if __name__ == '__main__':
    entries = {}
    for mode in ['baseline', 'fixed']:
        for name, text in sources(mode == 'fixed').items():
            path = HERE/mode/name
            assert not path.exists()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            entries.setdefault(name, {})[mode] = sha(path)
    (HERE/'manifest.json').write_text(json.dumps(dict(
        status='prepared_not_compiled_or_simulated', sources=entries,
        builder_sha256=sha(HERE/'build.py'), proof_sha256=sha(ROOT/'results/route_label_exclusion_20261028.json'),
        scope='Only label unexpected READY guard specialized. Owner term and sequential logic unchanged. '
              'Default off in controller/adapter; native residency uses existing default-off exclusivity flag. '
              'Requires default compatibility, legal native tests, explicit overlap counterexample, '
              'full-system actual port monitoring/exact replay and matched OOC before selection.'
    ), indent=2, sort_keys=True)+'\n')
    print('ROUTE_LABEL_CANDIDATE_PREPARED_NOT_VALIDATED')
