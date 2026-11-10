#!/usr/bin/env python3
"""Freeze complete encoded DUT-only physical inputs; never launch Vivado."""
import json
import shutil
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]


def main():
    output = ROOT / 'data/derived/paired_binary_fsm_physical_20261025_v1'
    audit = ROOT / 'results/paired_binary_fsm_physical_preparation_20261025_v1.json'
    require(not output.exists() and not audit.exists(), 'Refuse overwrite')
    evidence = ROOT / 'results/paired_binary_fsm_candidates_preparation_audit_20261025_v1.json'
    report = json.loads(evidence.read_text())
    require(report['status'] == 'both_graph_modes_matched_binary_fsm_candidate_preparations_verified_full_rtl_pending', 'Wrong paired preparation')
    for path, checksum in report['files'].items():
        require(digest(path) == checksum, 'Changed paired evidence: ' + path)
    reference = ROOT / 'data/derived/compressed_batch_bus64_physical_20261025_v1'
    base = json.loads((reference / 'plan.json').read_text())
    generated = {}
    inputs = {str(evidence): digest(evidence), str(reference / 'plan.json'): digest(reference / 'plan.json'), str(Path(__file__).resolve()): digest(__file__)}
    modes = {}
    for mode, original, candidate, expected_files, expected_modules in [
        ('csr', 'compressed_batch_bus64_physical_20261025_v1/csr', 'hls_binary_fsm_candidate_20261025_v1', 115, 43),
        ('compact', 'compressed_batch_compact_bus64_physical_20261025_v1/compact', 'hls_compact_binary_fsm_candidate_20261025_v1', 118, 45),
    ]:
        source = ROOT / 'data/derived' / original / 'source'
        candidate_dir = ROOT / 'data/derived' / candidate
        plan_path = candidate_dir / 'plan.json'
        plan = json.loads(plan_path.read_text())
        inputs[str(plan_path)] = digest(plan_path)
        files = sorted(p for p in source.iterdir() if p.is_file() and p.suffix in ('.v', '.dat'))
        require(len(files) == expected_files, 'Incomplete physical RTL/ROM set')
        names = {p.name for p in files}
        require(len(plan['modules']) == expected_modules and
                all(Path(m['candidate']).name in names for m in plan['modules']), 'Encoded module missing from physical set')
        work = output / mode
        (work / 'source').mkdir(parents=True)
        changed = []
        for original_file in files:
            before = Path(plan['original_rtl_dir']) / original_file.name
            after = candidate_dir / 'verilog' / original_file.name
            require(digest(before) == digest(original_file), 'Physical and simulation original DUT differ')
            require(plan['files'].get(str(after)) == digest(after), 'Candidate binding differs')
            inputs[str(original_file)] = digest(original_file)
            target = work / 'source' / after.name
            shutil.copyfile(after, target)
            require(digest(target) == digest(after), 'Copied candidate differs')
            generated[str(target)] = digest(target)
            if digest(original_file) != digest(after):
                changed.append(after.stem)
        require(set(changed) == {m['module'] for m in plan['modules']}, 'Unexpected physical encoding changes')
        for name in ['run_flow.tcl', 'clock.xdc']:
            before = reference / 'csr' / name
            require(base['generated'][str(before)] == digest(before), 'Changed original flow')
            shutil.copyfile(before, work / name)
            generated[str(work / name)] = digest(before)
        require({p.name for p in (work / 'source').iterdir()} == names, 'Wrong physical source membership')
        modes[mode] = dict(source_files=len(files), encoded_modules=len(changed), source_dir=str(work / 'source'))
    for path, checksum in generated.items():
        require(digest(path) == checksum, 'Post-copy mismatch')
    plan = dict(status='paired_encoded_dut_physical_inputs_prepared_not_executed', modes=modes,
                inputs=inputs, generated=generated,
                top=base['top'], part=base['part'], clock_ns=base['clock_ns'],
                setup_uncertainty_ns=base['setup_uncertainty_ns'], max_threads=base['max_threads'],
                minimum_raw_free_bytes=184 * 1024**3,
                execution_prerequisite_checker=str(ROOT / 'scripts/paired_binary_rtl_prerequisites_v1.py'),
                physical_executed=False, execution_entry_prepared=False,
                limitations=['Prepared only; full paired encoded RTL acceptance must precede execution.',
                             'A future execution entry must verify typed prerequisites and every source binding.',
                             'No encoded resource estimate, timing closure, platform fit or board measurement is established.',
                             'Simulation AXI models and testbench files are excluded by exact original synthesis source membership.'])
    atomic(output / 'plan.json', plan)
    atomic(audit, dict(status=plan['status'], physical_executed=False, execution_entry_prepared=False,
                       modes=modes, files={str(output / 'plan.json'): digest(output / 'plan.json'), **inputs, **generated},
                       limitations=plan['limitations']))
    print(audit)


if __name__ == '__main__':
    main()
