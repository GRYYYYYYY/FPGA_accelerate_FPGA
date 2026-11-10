"""Archive an interrupted experiment without altering or accepting its manifest."""
from pathlib import Path
import datetime
import hashlib
import json
import os
import subprocess
import tarfile

from host_edit_system_common_v1 import ROOT, BASE, sha, read, identity


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


def main():
    observation = ROOT/'results/stage_static_cp_shadow_v5_interruption_observation_20261030.json'
    observed = read(observation)
    assert observed['status'] == 'interrupted_without_terminal_receipt_not_accepted'
    roots = [BASE/'stage_static_cp_shadow_system_v5', BASE/'stage_static_cp_shadow_system_v5_followup_v1']
    for filename, digest in observed['evidence'].items():
        assert sha(filename) == digest, filename
    for pid in observed['missing_pids']:
        assert identity(int(pid)) is None, pid
    m = read(roots[0]/'manifest.json')
    assert m['status'] == 'observation_timeout' and m['stage'] == 'simulate'
    assert [(c['stage'], c['exit_code']) for c in m['cases']['full']['commands']] == [('compile', 0), ('elaborate', 0)]
    assert read(roots[1]/'manifest.json')['commands'] == []
    for name, entry in m['sources'].items():
        assert sha(roots[0]/'sources'/name) == entry['sha256'], name
    for name, digest in m['shadow_inputs'].items():
        assert sha(roots[0]/'sources'/name) == digest, name
    for name, entry in m['bound'].items():
        assert sha(entry['source']) == sha(roots[0]/'bound'/name) == entry['sha256'], name
    out = ROOT/'results/stage_static_cp_shadow_v5_interruption_preservation_20261030.json'
    destination = BASE/'stage_static_cp_shadow_v5_interruption_preservation_v1'
    assert not out.exists() and not destination.exists()
    destination.mkdir()
    before = {p.name: inventory(p) for p in roots}
    archive = destination/'interrupted_scene.tar'
    with tarfile.open(archive, 'w') as tf:
        for p in roots:
            tf.add(p, arcname=p.name)
    restored = destination/'restored'
    restored.mkdir()
    with tarfile.open(archive, 'r') as tf:
        for member in tf.getmembers():
            assert not member.issym() and not member.islnk()
            target = (restored/member.name).resolve()
            assert target.is_relative_to(restored.resolve())
            assert member.isfile() or member.isdir()
        tf.extractall(restored)
    after = {p.name: inventory(restored/p.name) for p in roots}
    assert before == after
    assert before == {p.name: inventory(p) for p in roots}, 'Original changed during preservation'
    cg = Path('/sys/fs/cgroup')
    resource = {n: (cg/n).read_text() for n in ['memory.current', 'memory.max', 'memory.stat', 'memory.events']}
    resource['df_bytes'] = subprocess.check_output(['df', '-B1', str(ROOT), '/tmp'], text=True)
    resource['df_inodes'] = subprocess.check_output(['df', '-i', str(ROOT), '/tmp'], text=True)
    report = dict(status='interrupted_scene_actual_restore_byte_identical_not_functional_acceptance',
                  observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  observation_sha256=sha(observation), tool_sha256=sha(__file__),
                  archive=str(archive), archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
                  restored_root=str(restored), files=before, files_count=sum(map(len, before.values())),
                  original_unchanged=True, actual_restore_byte_identical=True,
                  full_system_functional_netlist_validated=False, exit_cause='unknown',
                  resources=resource,
                  scope='Preserves incomplete v5 and followup only. No complete simulation receipt or functional acceptance. Cumulative OOM counters do not identify this job.')
    out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps(dict(report=str(out), files=report['files_count'], archive_bytes=report['archive_bytes'], status=report['status'])), flush=True)


if __name__ == '__main__':
    main()
