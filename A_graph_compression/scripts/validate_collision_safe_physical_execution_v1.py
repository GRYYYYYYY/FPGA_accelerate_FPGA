#!/usr/bin/env python3
"""Recheck new physical sources and refusal gates without starting Vivado."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import time

from check_vitis_kernel import digest, require
from collision_safe_physical_entry_v1 import validate_bundle
from prepare_collision_safe_physical_execution_v1 import ROOT, BASE, OUT as BUNDLE, RESULT as PREPARATION
from supervise_search_axi_dpi_v3 import atomic

OUT = ROOT/'data/derived/collision_safe_physical_entry_validation_20261031_v1'
RESULT = ROOT/'results/collision_safe_physical_entry_validation_20261031_v1.json'


def main():
    require(not OUT.exists() and not RESULT.exists(), 'Refuse overwrite')
    prep = json.loads(PREPARATION.read_text())
    files = {**prep['files'], str(PREPARATION): digest(PREPARATION)}
    for p, h in files.items():
        require(digest(p) == h, 'Changed physical preparation: ' + p)
    plan, _ = validate_bundle(BUNDLE, 'csr')
    old = ROOT/'scripts/check_encoded_physical_execution_v2.py'
    new = ROOT/'scripts/check_collision_safe_physical_execution_v1.py'
    def function(path, name):
        return ast.dump(next(n for n in ast.parse(path.read_text()).body
                             if isinstance(n, ast.FunctionDef) and n.name == name))
    require(function(old, 'terminal_receipts') == function(new, 'terminal_receipts'),
            'Changed exact terminal MCP receipt requirements')
    files[str(old)] = digest(old)
    sources = []
    for job in plan['jobs']:
        name = job['name']
        if name in ('csr', 'compact'):
            mode = 0 if name == 'csr' else 1
            original = BASE/f'collision_safe_bus64_pair_v1/mode_{mode}/project/solution/syn/verilog'
            template = ROOT/'data/derived/paired_binary_fsm_physical_20261025_v1'/name
        else:
            original = BASE/'search_read_control_staging_cosim_project_v1/solution/sim/verilog'
            template = ROOT/'data/derived/search_read_control_staging_physical_20261025_v2/csr'
        work = Path(job['work'])
        for filename in job['source_names']:
            physical, reference = work/'source'/filename, original/filename
            require(digest(physical) == digest(reference), 'Different current same-mode RTL/ROM')
            files[str(reference)] = digest(reference)
        for filename in ('run_flow.tcl', 'clock.xdc'):
            require((work/filename).read_bytes() == (template/filename).read_bytes(),
                    'Changed original physical commands or target constraints')
        sources.append(dict(job=name, files=len(job['source_names']), source=str(original)))
    OUT.mkdir()
    def run(label, command, code, marker):
        started = time.monotonic()
        result = subprocess.run(command, cwd=ROOT, stdout=subprocess.PIPE,
                                stderr=subprocess.STDOUT, text=True, timeout=120)
        log = OUT/(label+'.log')
        log.write_text(result.stdout)
        require(result.returncode == code and marker in result.stdout, 'Unexpected refusal/test result: ' + label)
        receipt = OUT/(label+'.receipt.json')
        atomic(receipt, dict(command=command, exit_code=result.returncode,
               elapsed_seconds=time.monotonic()-started, log_sha256=digest(log)))
        for p in (log, receipt):
            files[str(p)] = digest(p)
    run('tests', [sys.executable, '-m', 'unittest', 'discover', '-s', 'tests',
                  '-p', 'test_collision_safe_physical_execution_v1.py', '-v'], 0, 'Ran 8 tests')
    for job in plan['jobs']:
        name, work = job['name'], Path(job['work'])
        target = OUT/(name+'_must_not_exist.json')
        run(name+'_early_arm', [sys.executable, str(ROOT/'scripts/collision_safe_physical_entry_v1.py'),
            '--bundle', str(BUNDLE), '--job', name, '--owner-pid', '999999999'], 1,
            'collision_safe_recovered_native_rtl_audit_20261030_v2.json')
        run(name+'_early_audit', [sys.executable, str(new), '--bundle', str(BUNDLE), '--job', name,
            '--status', str(OUT/'missing_status'), '--history', str(OUT/'missing_history'),
            '--output', str(target)], 1, 'FileNotFoundError')
        require(not target.exists() and not any((work/n).exists() for n in
                ('state.json', 'guard', 'session.json')), 'Early check created physical execution artifacts')
    for p in (Path(__file__).resolve(), ROOT/'tests/test_collision_safe_physical_execution_v1.py'):
        files[str(p)] = digest(p)
    for p, h in files.items():
        require(digest(p) == h, 'Changed evidence during validation')
    atomic(RESULT, dict(status='corrected_three_physical_entries_sources_and_early_rejection_verified_not_executed',
           files=files, source_matrix=sources, tests=8, actual_early_rejections=6,
           terminal_receipts_ast_unchanged=True, original_flow_and_constraints_byte_identical=True,
           physical_executed=False, limitations=[
               'No actual RTL acceptance is inferred from prepared same-mode sources.',
               'No new Vivado session, synthesis, placement or routing has run.',
               'Platform/DDR/HBM/board and timing closure remain separate requirements.']))
    print(RESULT)


if __name__ == '__main__':
    main()
