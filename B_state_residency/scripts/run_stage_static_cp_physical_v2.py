"""Run one fresh static-stage physical attempt with preserved child wait ownership."""
from pathlib import Path
import json
import os
import shutil
import subprocess
import sys
import time
from prepare_stage_static_cp_physical_v4 import OUTPUT
from check_stage_static_cp_physical_inputs_v4 import evidence
from config_native_publication_synth_common_v1 import (
    ROOT, BIN, sha, read, identity, runtime_environment, memory_admission, wait_preserving,
)


def main():
    p = Path(sys.argv[1]).resolve()
    assert p == OUTPUT
    # Gate before accessing a future physical root or any restoring synthesis root.
    proof = evidence()
    m = read(p/'manifest.json')
    assert m['status'] == 'prepared' and m['stage'] == 'awaiting_validated_runner'
    for name, digest in proof.items():
        assert m['external_evidence_sha256'][name] == digest
    template = ROOT/'hardware/scripts/implement_state_ooc.tcl'
    assert (p/'run.tcl').read_text() == template.read_text().replace('@OUT@', str(p))
    env, runtime = runtime_environment()

    def validate():
        for name, digest in m['inputs'].items():
            assert sha(p/name) == digest, name
        for name, digest in m['external_evidence_sha256'].items():
            assert sha(name) == digest, name
        assert sha(p/'run.tcl') == m['tcl_sha256']
        assert sha(template) == m['template_sha256']
        assert runtime_environment()[1] == runtime

    validate()
    shutil.copyfile(Path(__file__), p/'runner.py')
    m.update(status='running', stage='wait_memory', runner_pid=os.getpid(),
             runner_start_ticks=identity(os.getpid()), runner_sha256=sha(p/'runner.py'),
             runtime=runtime, commands=[], execution='local_batch')

    def save():
        tmp = p/'manifest.pending.json'
        tmp.write_text(json.dumps(m, indent=2, sort_keys=True)+'\n')
        tmp.replace(p/'manifest.json')

    save()
    start = time.monotonic()
    try:
        memory_admission(m, save)
        phases = [('version', [str(BIN), '-version'], 60),
                  ('implementation', [str(BIN), '-mode', 'batch', '-source', str(p/'run.tcl'),
                    '-log', str(p/'vivado.log'), '-journal', str(p/'vivado.jou')], 14400)]
        for stage, argv, timeout in phases:
            validate()
            m['stage'] = stage
            save()
            out = p/('version.stdout.log' if stage == 'version' else 'stdout.log')
            with out.open('w') as log:
                child = subprocess.Popen(argv, cwd=p, env=env, stdout=log, stderr=subprocess.STDOUT)
                ticks = identity(child.pid)
                m['active_process'] = dict(stage=stage, pid=child.pid, start_ticks=ticks, argv=argv)
                save()
                code = wait_preserving(child, timeout, m, save)
            m.pop('active_process', None)
            m['commands'].append(dict(stage=stage, argv=argv, pid=child.pid,
                start_ticks=ticks, exit_code=code, stdout_sha256=sha(out)))
            m['status'] = 'running'
            save()
            assert code == 0, stage
            if stage == 'version':
                assert 'Vivado v2022.2' in out.read_text()
            else:
                m['exit_code'] = code
        validate()
        log = (p/'vivado.log').read_text()
        assert 'STATE_FULL_PHYSICAL_DONE' in log
        assert not any(line.startswith('ERROR:') for line in log.splitlines())
        outputs = ['optimized.dcp', 'placed.dcp', 'routed.dcp', 'completed.txt', 'milestones.txt',
            'clocks_input.rpt', 'utilization_input.rpt', 'methodology_input.rpt',
            'check_timing_input.rpt', 'loops_input.rpt', 'constraints_input.xdc',
            'utilization_placed.rpt', 'timing_placed.rpt', 'route_status.rpt',
            'utilization_routed.rpt', 'utilization_routed_hier.rpt', 'methodology_routed.rpt',
            'drc_routed.rpt', 'loops_routed.rpt', 'check_timing_routed.rpt', 'clocks_routed.rpt',
            'timing_routed.rpt', 'constraints_routed.xdc', 'internal_paths.tsv',
            'vivado.log', 'vivado.jou', 'stdout.log', 'version.stdout.log']
        for name in outputs:
            assert (p/name).is_file() and (p/name).stat().st_size > 0, name
        m.update(status='observed', stage='implementation_complete_pending_independent_inspection',
                 artifact_sha256={name: sha(p/name) for name in outputs})
    except Exception as error:
        m.update(status='failed', error=repr(error))
        raise
    finally:
        m['elapsed_s'] = time.monotonic()-start
        save()
    print('STATIC_STAGE_PHYSICAL_IMPLEMENTATION_OBSERVED', p)


if __name__ == '__main__':
    main()
