"""Preserve the failed v6 scene; never create a functional acceptance receipt."""
import datetime
import json
import tarfile
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        assert not p.is_symlink(), p
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


def main():
    observation = ROOT/'results/stage_static_cp_shadow_v6_terminal_failure_observation_20261031.json'
    obs = read(observation)
    assert obs['status'] == 'terminal_ka_stall_coverage_failure_not_functional_acceptance'
    for name, digest in obs['evidence'].items():
        assert sha(name) == digest, name
    for pid in [1487337, 1596444, 1509620, 1487299]:
        assert identity(pid) is None, pid
    roots = [BASE/n for n in ['stage_static_cp_shadow_system_v6',
             'stage_static_cp_shadow_system_v6_followup_v1',
             'stage_static_cp_shadow_system_v6_lifecycle_v1']]
    assert read(roots[1]/'manifest.json')['status'] == 'failed'
    assert read(roots[1]/'manifest.json')['commands'] == []
    assert read(roots[2]/'manifest.json')['status'] == 'failed'
    m = read(roots[0]/'manifest.json')
    assert m['status'] == 'observation_timeout' and m['stage'] == 'simulate'
    assert [(c['stage'], c['exit_code']) for c in m['cases']['full']['commands']] == [('compile', 0), ('elaborate', 0), ('simulate', 0)]
    for name, e in m['sources'].items():
        assert sha(roots[0]/'sources'/name) == e['sha256'], name
    for name, digest in m['shadow_inputs'].items():
        assert sha(roots[0]/'sources'/name) == digest, name
    for name, e in m['bound'].items():
        assert sha(e['source']) == sha(roots[0]/'bound'/name) == e['sha256'], name
    destination = BASE/'stage_static_cp_shadow_v6_failure_preservation_v1'
    out = ROOT/'results/stage_static_cp_shadow_v6_failure_preservation_20261031.json'
    assert not destination.exists() and not out.exists()
    destination.mkdir()
    before = {p.name: inventory(p) for p in roots}
    archive = destination/'failed_scene.tar'
    with tarfile.open(archive, 'w', dereference=True) as tf:
        for p in roots:
            tf.add(p, arcname=p.name)
    restored = destination/'restored'
    restored.mkdir()
    with tarfile.open(archive, 'r') as tf:
        for member in tf.getmembers():
            assert member.isfile() or member.isdir()
            assert (restored/member.name).resolve().is_relative_to(restored.resolve())
        tf.extractall(restored)
    assert before == {p.name: inventory(restored/p.name) for p in roots}
    assert before == {p.name: inventory(p) for p in roots}, 'Original changed'
    report = dict(status='failed_v6_scene_actual_restore_byte_identical_not_functional_acceptance',
                  observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                  observation_sha256=sha(observation), tool_sha256=sha(__file__),
                  archive=str(archive), archive_sha256=sha(archive), archive_bytes=archive.stat().st_size,
                  restored_root=str(restored), files=before, files_count=sum(map(len, before.values())),
                  original_unchanged=True, actual_restore_byte_identical=True,
                  full_system_functional_netlist_validated=False, physical_gate_open=False,
                  scope='Failed KA stall coverage, stale timeout manifest and actual exit receipts preserved unchanged. This validates preservation only.')
    out.write_text(json.dumps(report, indent=2, sort_keys=True)+'\n')
    print(json.dumps({k: report[k] for k in ['status', 'files_count', 'archive_bytes', 'archive_sha256']}), flush=True)


if __name__ == '__main__':
    main()
