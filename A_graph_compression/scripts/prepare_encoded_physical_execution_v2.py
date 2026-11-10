#!/usr/bin/env python3
"""Prepare three protected MCP OOC entries from the exact frozen physical sources."""
import json
from pathlib import Path
import shutil

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import POLICY
from encoded_physical_entry_v2 import PHYSICAL_AS_BYTES
from supervise_integrated_rtl_recovery_v1 import source_closure
from supervise_search_axi_dpi_v3 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    out = ROOT/'data/derived/encoded_physical_execution_20261029_v2'
    result = ROOT/'results/encoded_physical_execution_preparation_20261029_v2.json'
    require(not out.exists() and not result.exists(), 'Refuse overwrite')
    pair = ROOT/'data/derived/paired_binary_fsm_physical_20261025_v1'
    pair_report = ROOT/'results/paired_binary_fsm_physical_preparation_20261025_v1.json'
    paired = json.loads(pair_report.read_text())
    require(paired['status'] == 'paired_encoded_dut_physical_inputs_prepared_not_executed', 'Wrong physical pair')
    read = ROOT/'data/derived/search_read_control_staging_physical_20261025_v2'
    staged = json.loads((read/'plan.json').read_text())
    require(staged['status'] == 'prepared_not_started_candidate_rtl_acceptance_required', 'Wrong staged physical source')
    files = {**paired['files'], **staged['inputs'], **staged['generated'], str(pair_report):digest(pair_report), str(read/'plan.json'):digest(read/'plan.json')}
    for path, checksum in files.items():
        require(digest(path) == checksum, 'Changed prepared physical evidence: '+path)
    files.update(source_closure([Path(__file__).resolve(), ROOT/'scripts/encoded_physical_entry_v2.py',
                                ROOT/'scripts/check_encoded_physical_execution_v2.py'], ROOT/'scripts'))
    jobs = []
    for name, old, relative, top, expected in [
        ('csr', pair/'csr', 'csr', 'search_batch_trace_top_v2', 115),
        ('compact', pair/'compact', 'compact', 'search_batch_trace_top_v2', 118),
        ('read_control', read/'csr', 'read_control/csr', 'search_kernel_top', staged['source_rtl_and_rom_files']),
    ]:
        work = out/relative
        source = work/'source'
        source.mkdir(parents=True)
        names = sorted(p.name for p in (old/'source').iterdir() if p.is_file())
        require(len(names) == expected and all(Path(n).suffix in ('.v', '.dat') for n in names), 'Wrong complete physical source set')
        for filename in names:
            before, after = old/'source'/filename, source/filename
            require(str(before) in files and files[str(before)] == digest(before), 'Unbound original physical source')
            shutil.copyfile(before, after)
            require(digest(after) == files[str(before)], 'Changed candidate physical copy')
            files[str(after)] = digest(after)
        for filename in ['run_flow.tcl', 'clock.xdc']:
            before, after = old/filename, work/filename
            require(files.get(str(before)) == digest(before), 'Unbound original flow/constraints')
            shutil.copyfile(before, after)
            require(digest(after) == digest(before), 'Physical commands or target constraints changed')
            files[str(after)] = digest(after)
        # The original flow is byte-identical; the wrapper gates before any Vivado operation.
        entry = work/'entry.tcl'
        entry.write_text('# Dedicated empty Vivado2022.2 Tcl session only.\n'
                         'puts [exec /usr/bin/python3 {'+str(ROOT/'scripts/encoded_physical_entry_v2.py')+
                         '} --bundle {'+str(out)+'} --job '+name+' --owner-pid [pid]]\n'
                         'source {'+str(work/'run_flow.tcl')+'}\n')
        files[str(entry)] = digest(entry)
        jobs.append(dict(name=name, work=str(work), source_names=names, top=top,
                         source_command='source {'+str(entry)+'}',
                         session_policy='New dedicated MCP Tcl session; save work/session.json {session_id,pid}, then source entry.tcl once; stop session after terminal evidence capture/audit before next mode'))
    plan = dict(status='full_scope_physical_entries_prepared_not_executed', files=files, jobs=jobs,
                part='xcu280-fsvh2892-2L-e', clock_ns=5, setup_uncertainty_ns=1.35, max_threads=2,
                startup_wait_removed_by_user=True,runtime_rawfree_gate_removed_by_user=True,resource_policy=POLICY,physical_as_bytes=PHYSICAL_AS_BYTES,
                execution_entry_prepared=True, physical_executed=False,
                prerequisite='Current nonzero native v2, both encoded full44, full50 tree, original full30 v5 and staged full2 v4 accepted with all SHA; current serial chain terminal before arming',
                limitations=['No physical run or new Vivado session has been launched.',
                             'Exact original2022.2 synthesis/place/route/report flow; no waiver, relaxed target or onehot mapped estimate substitution.',
                             'Per-process AS192GiB/core0 on the dedicated session; no rawfree gate, new actual OOM events stop the owned session.',
                             'OOC data only; actual platform shell, IO constraints, DDR/HBM, power and board execution remain required.'])
    atomic(out/'plan.json', plan)
    atomic(result, dict(status=plan['status'], files={**files, str(out/'plan.json'):digest(out/'plan.json')},
                        jobs=[dict(name=j['name'], source_files=len(j['source_names']), top=j['top']) for j in jobs],
                        execution_entry_prepared=True, physical_executed=False, limitations=plan['limitations']))
    print(result)


if __name__ == '__main__':
    main()
