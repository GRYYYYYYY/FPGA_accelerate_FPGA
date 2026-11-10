"""Independently reopen the fresh static-stage routed checkpoint in Vivado 2022.2."""
from pathlib import Path
import json
import os
import subprocess
import sys
import time
from prepare_stage_static_cp_physical_v5 import OUTPUT
from check_stage_static_cp_physical_inputs_v5 import evidence
from config_native_publication_synth_common_v1 import (
    ROOT, BIN, sha, read, identity, runtime_environment, memory_admission, wait_preserving,
)


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == OUTPUT
    proof = evidence()
    m = read(p/'manifest.json')
    assert m['status'] == 'observed'
    assert m['stage'] == 'implementation_complete_pending_independent_inspection'
    assert identity(m['runner_pid']) != str(m['runner_start_ticks'])
    assert not m.get('active_process') and m['exit_code'] == 0
    for name, digest in proof.items():
        assert m['external_evidence_sha256'][name] == digest
    for name, digest in m['inputs'].items():
        assert sha(p/name) == digest
    for name, digest in m['artifact_sha256'].items():
        assert sha(p/name) == digest
    d = p/'inspection'
    assert not d.exists(), 'Preserve prior inspection attempts'
    template = ROOT/'hardware/scripts/inspect_state_route_v1.tcl'
    env, runtime = runtime_environment()
    assert runtime == m['runtime']
    d.mkdir()
    script = d/'inspect.tcl'
    script.write_text(template.read_text().replace('@OUT@', str(p)))
    record = dict(status='running', stage='wait_memory', inspector_pid=os.getpid(),
        inspector_start_ticks=identity(os.getpid()), inspector_sha256=sha(Path(__file__)),
        implementation_manifest_sha256=sha(p/'manifest.json'), runtime=runtime,
        template_sha256=sha(template), script_sha256=sha(script),
        routed_checkpoint_sha256=sha(p/'routed.dcp'))

    def save():
        tmp = d/'manifest.pending.json'
        tmp.write_text(json.dumps(record, indent=2, sort_keys=True)+'\n')
        tmp.replace(d/'manifest.json')

    save()
    start = time.monotonic()
    try:
        memory_admission(record, save)
        assert runtime_environment()[1] == runtime
        assert sha(p/'manifest.json') == record['implementation_manifest_sha256']
        assert sha(p/'routed.dcp') == record['routed_checkpoint_sha256']
        argv = [str(BIN), '-mode', 'batch', '-source', str(script),
                '-log', str(d/'vivado.log'), '-journal', str(d/'vivado.jou')]
        record.update(stage='independent_reopen', command=argv)
        save()
        with (d/'stdout.log').open('w') as log:
            child = subprocess.Popen(argv, cwd=p, env=env, stdout=log, stderr=subprocess.STDOUT)
            record['active_process'] = dict(pid=child.pid, start_ticks=identity(child.pid), argv=argv)
            save()
            code = wait_preserving(child, 3600, record, save)
        record.pop('active_process', None)
        record['exit_code'] = code
        save()
        assert code == 0
        log = (d/'stdout.log').read_text()
        assert 'STATE_ROUTE_RECOVERY_REOPENED' in log
        assert not any(line.startswith('ERROR:') for line in log.splitlines())
        assert sha(p/'routed.dcp') == record['routed_checkpoint_sha256']
        assert sha(p/'manifest.json') == record['implementation_manifest_sha256']
        outputs = ['route_status.rpt', 'utilization.rpt', 'timing.rpt', 'methodology.rpt',
                   'drc.rpt', 'check_timing.rpt', 'constraints.xdc', 'stdout.log', 'vivado.log',
                   'vivado.jou', 'inspect.tcl']
        for name in outputs:
            assert (d/name).is_file() and (d/name).stat().st_size > 0
        record.update(status='observed', stage='complete',
                      artifact_sha256={name: sha(d/name) for name in outputs})
    except Exception as error:
        record.update(status='failed', error=repr(error))
        raise
    finally:
        record['elapsed_s'] = time.monotonic()-start
        save()
    print('STATIC_STAGE_PHYSICAL_INDEPENDENT_REOPEN_OBSERVED')


if __name__ == '__main__':
    main()
