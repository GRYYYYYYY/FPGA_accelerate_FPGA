"""Future-run receipt helpers. Never mutate a historical run or signal a child."""
from collections.abc import MutableMapping, Sequence
import subprocess


def record_child_exit(manifest: MutableMapping, exit_code: int) -> None:
    """Call only after wait/poll has returned an actual child exit code."""
    if not isinstance(exit_code, int):
        raise ValueError('child exit code required')
    manifest.pop('active_process', None)
    # Observation timeout described a prior live-child observation, not its exit.
    manifest['status'] = 'running'
    manifest['last_child_exit_code'] = exit_code


def validate_simulation_log(log: str, markers: Sequence[str]) -> None:
    failures = [line for line in log.splitlines()
                if 'Fatal:' in line or 'ERROR:' in line]
    if failures:
        raise RuntimeError('Simulation failure: ' + failures[0])
    missing = [marker for marker in markers if marker not in log]
    if missing:
        raise RuntimeError('Missing simulation evidence: ' + repr(missing))


def record_exception(manifest: MutableMapping, error: Exception,
                     child: subprocess.Popen | None = None) -> None:
    """Preserve a still-live child; otherwise write a definite failure receipt."""
    live = child is not None and child.poll() is None
    manifest['error'] = repr(error)
    if live:
        manifest['status'] = 'observation_timeout'
        manifest['child_preserved'] = True
    else:
        manifest['status'] = 'failed'
        manifest.pop('active_process', None)
        for case in manifest.get('cases', {}).values():
            if case.get('status') in ('running', 'observation_timeout'):
                case['status'] = 'failed'
