"""Classify a previously executed negative caught by an earlier equivalent guard.

No RTL, simulation, checker, or original failed runner artifact is modified.
"""
from pathlib import Path
import json
import sys
from verify_indexed_endpoint import ROOT, sha


def main():
    out = Path(sys.argv[1]).resolve()
    folder = out / 'negative_guards'
    path = folder / 'manifest.json'
    original = json.loads(path.read_text())
    assert original['status'] == 'running'
    assert original['simulation_manifest_sha256'] == sha(out / 'simulation_manifest.json')
    for name, digest in original['sources'].items():
        assert sha(Path(name)) == digest
    classified = json.loads(path.read_text())
    expected = {'drop_overflow_scan': 'host mismatch',
                'respond_before_index_scrub': 'index scrub exposed incomplete directory',
                'expose_query_during_recycle': 'accepted query during fence recycle'}
    assert set(original['cases']) == set(expected)
    for name, row in classified['cases'].items():
        d = folder / name
        assert len(row['commands']) == 3 and all(c['exit_code'] == 0 for c in row['commands'][:2])
        module = row['module']
        text = (out / 'sources/hardware/rtl' / (module + '.sv')).read_text()
        assert text.count(row['before']) == 1
        assert (d / (module + '.sv')).read_text() == text.replace(row['before'], row['after'])
        log = (d / 'simulate.log').read_text()
        fatal = [line for line in log.splitlines() if line.startswith('Fatal:')]
        assert len(fatal) == 1 and expected[name] in fatal[0] and 'TEST_PASS' not in log
        if name == 'expose_query_during_recycle':
            # The original test actively offers QUERY while FINISH is pending.
            # Its negedge assertion precedes the generic posedge protocol guard.
            tb = (out / 'sources/hardware/tb/tb_memory_endpoint_indexed.sv').read_text()
            assert 'while(!rsp_valid)begin @(negedge clk);if(cmd_ready)$fatal(1,"accepted query during fence recycle");end' in tb
            assert 'Process: /tb_memory_endpoint_indexed_small/test/fence_and_next_query' in log
            assert 'Time: 100440 ns' in log
            row['original_expected_failure'] = row['expected_failure']
            row['classification_reason'] = 'Active-query negedge guard caught the same illegal ready exposure before the generic posedge guard.'
        row.update(status='detected', expected_failure=expected[name], first_failure=fatal[0],
                   artifacts={p.name: sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ['.sv', '.log', '.tcl']})
    classified.update(status='passed', original_runner_exit_code=1, original_manifest_sha256=sha(path),
                      classification_source={str(Path(__file__).resolve()): sha(Path(__file__).resolve())})
    target = folder / 'classified_manifest.json'
    assert not target.exists()
    target.write_text(json.dumps(classified, indent=2) + '\n')
    (folder / 'classification_audit.json').write_text(json.dumps({'status': 'passed', 'manifest_sha256': sha(target),
        'scope': 'Existing negative evidence reclassified without rerunning or weakening checks.'}, indent=2) + '\n')
    print(sha(target))


if __name__ == '__main__':
    main()
