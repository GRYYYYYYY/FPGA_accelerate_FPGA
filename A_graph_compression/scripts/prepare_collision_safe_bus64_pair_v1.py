#!/usr/bin/env python3
"""Freeze matched CSR/compact full44 HLS inputs; do not launch compilation."""
import json
from pathlib import Path
import shutil
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
SOURCE = BASE/'collision_safe_batch_hls_v1'
OUT = BASE/'collision_safe_bus64_pair_v1'
REPORT = ROOT/'results/collision_safe_bus64_pair_preparation_20261030_v1.json'


def main():
    require(not OUT.exists() and not REPORT.exists(), 'Refuse duplicate preparation')
    files = {}
    gates = [
        ('collision_safe_batch_full44_cpu_20261030_v1.json',
         'identifier_only_candidate_matches_all8_original_full44_C_snapshots'),
        ('collision_safe_compact_hls_audit_20261030_v1.json',
         'collision_safe_native_compact_hls_all9_dynamic_connections_and_full44_C_verified_rtl_pending')]
    for name, status in gates:
        path = ROOT/'results'/name
        obj = json.loads(path.read_text())
        require(obj['status'] == status, 'Missing independent prerequisite '+name)
        for filename, checksum in obj['files'].items():
            require(digest(filename) == checksum, 'Changed prerequisite '+filename)
            require(filename not in files or files[filename] == checksum, 'Conflicting binding')
            files[filename] = checksum
        files[str(path)] = digest(path)
    help_path = BASE/'hls_interface_options_20261025_v1/help.log'
    require('-m_axi_max_widen_bitwidth' in help_path.read_text(), 'Unsupported local configuration')
    files[str(help_path)] = digest(help_path)
    native = (SOURCE/'flow.tcl').read_text()
    require(native.count('csynth_design\n') == 1 and native.count('SEARCH_GRAPH_MODE=1') == 2 and
            'config_interface' not in native, 'Unexpected original native flow')
    OUT.mkdir()
    jobs = []
    for mode in [0, 1]:
        work = OUT/f'mode_{mode}'; work.mkdir()
        shutil.copytree(SOURCE/'source', work/'source')
        for p in (work/'source').iterdir():
            original = SOURCE/'source'/p.name
            require(original.is_file() and str(original) in files and
                    digest(p) == files[str(original)], 'Source differs from accepted candidate')
            files[str(p)] = digest(p)
        # Add only the matching interface cap and full C replay to the
        # accepted native Tcl. The mode is the sole paired difference.
        flow = native.replace('SEARCH_GRAPH_MODE=1', f'SEARCH_GRAPH_MODE={mode}')
        flow = flow.replace('config_compile -pipeline_loops 0\n',
                            'config_interface -m_axi_max_widen_bitwidth 64\nconfig_compile -pipeline_loops 0\n')
        flow = flow.replace('csynth_design\n', 'csim_design -clean\nputs COLLISION_SAFE_BUS64_CSIM_COMPLETE\ncsynth_design\n')
        flow = flow.replace('COLLISION_SAFE_FULL_BATCH_CSYNTH_COMPLETE', 'COLLISION_SAFE_BUS64_CSYNTH_COMPLETE')
        path = work/'flow.tcl'; path.write_text(flow)
        files[str(path)] = digest(path)
        jobs.append(dict(mode=mode, cwd=str(work), source=str(work/'source'), project=str(work/'project'),
                         flow=str(path), snapshot_prefix=str(work/'csim'), transactions=4, pointers=44,
                         command=['prlimit', '--as=68719476736:68719476736', '--stack=67108864:67108864',
                                  '--core=0:0', '--',
                                  '/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls',
                                  '-f', str(path)]))
    require((OUT/'mode_1/flow.tcl').read_text().replace('SEARCH_GRAPH_MODE=1', 'SEARCH_GRAPH_MODE=0') ==
            (OUT/'mode_0/flow.tcl').read_text(), 'Unmatched paired configuration')
    for p in [SOURCE/'flow.tcl', Path(__file__).resolve()]: files[str(p)] = digest(p)
    report = dict(status='collision_safe_bus64_CSR_compact_matched_full44_inputs_prepared_not_executed',
                  files=files, jobs=jobs, source_changes_from_accepted_candidate=[],
                  paired_difference='SEARCH_GRAPH_MODE only', part='xcu280-fsvh2892-2L-e',
                  clock_ns=5, uncertainty_ns=1.35, max_axi_widen_bitwidth=64,
                  startup_free_memory_gate=False, hls_executed=False, rtl_verified=False,
                  physical_verified=False, board_verified=False,
                  next='Run the two jobs serially under owned OOM protection; independently audit C snapshots and HLS outputs before fresh RTL setup.')
    with REPORT.open('x') as stream:
        json.dump(report, stream, indent=2); stream.write('\n')
    print(report['status'])


if __name__ == '__main__': main()
