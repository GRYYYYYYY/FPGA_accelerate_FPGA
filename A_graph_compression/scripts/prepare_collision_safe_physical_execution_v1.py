#!/usr/bin/env python3
"""Prepare protected OOC entries from naming-corrected HLS and original staged read RTL."""
import json
from pathlib import Path
import shutil

from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import POLICY
from collision_safe_physical_entry_v1 import PHYSICAL_AS_BYTES
from supervise_integrated_rtl_recovery_v1 import source_closure
from supervise_search_axi_dpi_v3 import atomic

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUT = ROOT / 'data/derived/collision_safe_physical_execution_20261031_v1'
RESULT = ROOT / 'results/collision_safe_physical_execution_preparation_20261031_v1.json'


def main():
    require(not OUT.exists() and not RESULT.exists(), 'Refuse overwrite')
    hls_path = ROOT / 'results/collision_safe_bus64_pair_hls_audit_20261030_v3.json'
    hls = json.loads(hls_path.read_text())
    require(hls['status'] == 'collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending'
            and hls['full44_transactions_per_mode'] == 4 and
            [m['mode'] for m in hls['modes']] == [0, 1], 'Missing exact new paired HLS audit')
    flow_pair = ROOT / 'data/derived/paired_binary_fsm_physical_20261025_v1'
    flow_report = ROOT / 'results/paired_binary_fsm_physical_preparation_20261025_v1.json'
    templates = json.loads(flow_report.read_text())
    read = ROOT / 'data/derived/search_read_control_staging_physical_20261025_v2'
    staged = json.loads((read/'plan.json').read_text())
    require(staged['status'] == 'prepared_not_started_candidate_rtl_acceptance_required',
            'Different original staged read preparation')
    files = {}
    for bindings in (hls['files'], staged['inputs'], staged['generated']):
        for p, checksum in bindings.items():
            require(p not in files or files[p] == checksum, 'Conflicting physical input binding')
            if p not in files:
                require(digest(p) == checksum, 'Changed physical prerequisite: ' + p)
            files[p] = checksum
    for p in (hls_path, flow_report, read/'plan.json'):
        files[str(p)] = digest(p)
    files.update(source_closure([
        Path(__file__).resolve(), ROOT/'scripts/collision_safe_physical_entry_v1.py',
        ROOT/'scripts/check_collision_safe_physical_execution_v1.py'], ROOT/'scripts'))
    jobs = []
    definitions = [
        ('csr', BASE/'collision_safe_bus64_pair_v1/mode_0/project/solution/syn/verilog',
         flow_pair/'csr', 'csr', 'search_batch_trace_top_v2', 115),
        ('compact', BASE/'collision_safe_bus64_pair_v1/mode_1/project/solution/syn/verilog',
         flow_pair/'compact', 'compact', 'search_batch_trace_top_v2', 118),
        ('read_control', read/'csr/source', read/'csr', 'read_control/csr',
         'search_kernel_top', staged['source_rtl_and_rom_files'])]
    for name, original, template, relative, top, expected in definitions:
        names = sorted(p.name for p in original.iterdir() if p.is_file())
        require(len(names) == expected and all(Path(n).suffix in ('.v', '.dat') for n in names),
                'Different complete same-mode RTL/ROM set')
        work = OUT/relative
        source = work/'source'
        source.mkdir(parents=True)
        for filename in names:
            before, after = original/filename, source/filename
            require(files.get(str(before)) == digest(before), 'Unbound physical RTL/ROM input')
            shutil.copyfile(before, after)
            require(digest(after) == files[str(before)], 'Changed physical source copy')
            files[str(after)] = digest(after)
        for filename in ('run_flow.tcl', 'clock.xdc'):
            before, after = template/filename, work/filename
            expected_hash = (templates['files'].get(str(before)) if name != 'read_control'
                             else files.get(str(before)))
            require(expected_hash == digest(before), 'Unbound original flow/constraints')
            files[str(before)] = expected_hash
            shutil.copyfile(before, after)
            require(digest(after) == expected_hash, 'Flow/constraint copy differs')
            files[str(after)] = expected_hash
        entry = work/'entry.tcl'
        entry.write_text('# Dedicated empty Vivado2022.2 Tcl session only.\n'
                         'puts [exec /usr/bin/python3 {'+str(ROOT/'scripts/collision_safe_physical_entry_v1.py')+
                         '} --bundle {'+str(OUT)+'} --job '+name+' --owner-pid [pid]]\n'
                         'source {'+str(work/'run_flow.tcl')+'}\n')
        files[str(entry)] = digest(entry)
        jobs.append(dict(name=name, work=str(work), source_names=names, top=top,
                         source_command='source {'+str(entry)+'}',
                         session_policy='New dedicated MCP Tcl session; save session.json; source entry once; capture terminal evidence and audit before the next mode'))
    plan = dict(status='full_scope_physical_entries_prepared_not_executed', files=files, jobs=jobs,
                source_family='naming-corrected native bus64 pair and original staged read',
                part='xcu280-fsvh2892-2L-e', clock_ns=5, setup_uncertainty_ns=1.35, max_threads=2,
                startup_wait_removed_by_user=True, runtime_rawfree_gate_removed_by_user=True,
                resource_policy=POLICY, physical_as_bytes=PHYSICAL_AS_BYTES,
                execution_entry_prepared=True, physical_executed=False,
                prerequisite='Corrected native, both corrected bus64 full4, full50, full30 v6 and read v5 independently accepted; serial chain owner exited; exact actual same-mode RTL/ROM binding required.',
                limitations=['Preparation only; no new Vivado session or synthesis/place/route operation.',
                             'Same original2022.2 commands and constraints; no timing/DRC waiver.',
                             'AS192GiB/core0 on the dedicated session; new actual OOM/reset stops only that owned session.',
                             'OOC measurement only; platform shell/IO, DDR/HBM, transfer, power and board results remain required.',
                             'Legacy encoded/FSM candidate results remain separate and unaccepted.'])
    atomic(OUT/'plan.json', plan)
    atomic(RESULT, dict(status=plan['status'], files={**files, str(OUT/'plan.json'): digest(OUT/'plan.json')},
                       jobs=[dict(name=j['name'], source_files=len(j['source_names']), top=j['top']) for j in jobs],
                       execution_entry_prepared=True, physical_executed=False, limitations=plan['limitations']))
    print(RESULT)


if __name__ == '__main__':
    main()
