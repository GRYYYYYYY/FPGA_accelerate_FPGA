"""Freeze the exact extended baseline/CP comparison after actual restoration."""
from pathlib import Path
import json
import shutil
from host_edit_system_common_v1 import ROOT, TARGETS, sha, read, identity, restored


def main():
    cases = {}; evidence = []
    for mode, p in TARGETS.items():
        m, a, files = restored(p)
        assert m['mode'] == mode and m['stage'] == 'complete'
        assert identity(m['runner_pid']) != str(m['runner_start_ticks']) and not m.get('active_process')
        assert a['auditor_sha256'] == sha(ROOT/'scripts/audit_host_edit_system_v1.py')
        assert a['parser_sha256'] == sha(ROOT/'scripts/check_host_edit_trace_v1.py')
        assert a['host_edit']['host_writes'] == 1 and a['host_edit']['final_dirty'] == 1 and a['host_edit']['final_pending'] == 0
        cases[mode] = dict(manifest=m,audit=a,restoration=read(files[2]))
        evidence += files
        for name, entry in m['sources'].items():
            assert sha(p/'sources'/name) == entry['sha256']
        for name, entry in m['bound'].items():
            assert sha(entry['source']) == entry['sha256'] == sha(p/'bound'/name)
    baseline, candidate = cases['baseline']['audit'], cases['cp']['audit']
    assert candidate['baseline_audit_sha256'] == sha(TARGETS['baseline']/'source_bound_audit.json')
    assert baseline['host_edit'] == candidate['host_edit'] and baseline['coverage'] == candidate['coverage']
    assert baseline['outputs'] == candidate['outputs'] == candidate['exact_comparisons']
    assert len(candidate['exact_comparisons']) == 27 and baseline['finish_time'] == candidate['finish_time']
    out = ROOT/'results/checkpoint_host_edit_system_20261030.json'
    freeze = ROOT/'results/checkpoint_host_edit_system_sources_20261030'
    assert not out.exists() and not freeze.exists()
    report = dict(status='real_host_edit_baseline_cp_exact_pair_restored',cases=cases,
        exact_file_comparisons=27,host_edit_exercised=True,production_rtl_changed=False,
        timing_qualified=False,board_acceptance=False,
        scope='Four real queries followed by one same-value native host label write. Both actual restored runs preserve the original trace prefix and match every27 output bytes/cycles. Valid clean checkpoint cannot clear dirty; valid dirty checkpoint restores pending. This single directed case is not arbitrary host edits or persistence authentication.')
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');freeze.mkdir(); entries={}
    def copy(source, relative):
        target = freeze/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
        entries[str(relative)] = dict(source=str(source),sha256=sha(source));assert sha(target)==entries[str(relative)]['sha256']
    for mode, p in TARGETS.items():
        m = cases[mode]['manifest']
        for name in m['sources']:
            copy(p/'sources'/name,Path(mode)/'sources'/name)
        for name in m['bound']:
            copy(p/'bound'/name,Path(mode)/'bound'/name)
        for name in ['manifest.json','source_bound_audit.json']:
            copy(p/name,Path(mode)/name)
        for name in ['simulate.log','compile.stdout.log','elaborate.stdout.log','simulate.stdout.log','run.tcl']:
            copy(p/'pressure'/name,Path(mode)/'logs'/name)
    for source in evidence+[out,Path(__file__).resolve()]:
        copy(source,Path('evidence')/(str(len(entries))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,
        exact_file_comparisons=27,timing_qualified=False,board_acceptance=False),indent=2,sort_keys=True)+'\n')
    print('HOST_EDIT_SYSTEM_FROZEN',len(entries))


if __name__ == '__main__':
    main()
