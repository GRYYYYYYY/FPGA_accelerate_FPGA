#!/usr/bin/env python3
"""Freeze all six orders and the original complete workloads before any supplemental run."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import time
from training_order_control_contract_v1 import *
from supervise_integrated_rtl_recovery_v1 import source_closure
from supervise_search_axi_dpi_v3 import atomic

VALIDATION_OUT=ROOT/'data/derived/training_order_control_entry_validation_20261029_v1'

def main():
    require(not any(p.exists() for p in [PREPARATION,OUT,CONTROL,FINAL,VALIDATION_OUT]),'Refuse overwrite or prepare over active trial')
    base,files=prior_evidence()
    worker=json.loads((VALIDATION/'worker_000/report.json').read_text())
    require(len(worker['batches'])==2,'Partial original batch count')
    paths=[ROOT/'scripts'/name for name in ['run_training_order_control_v1.py','check_training_order_control_v1.py','supervise_training_order_control_v1.py','training_order_control_contract_v1.py','prepare_training_order_control_v1.py']]
    source_files=source_closure(paths,ROOT/'scripts');files.update(source_files)
    # Keep historical 21-worker integrity checks outside worker startup. The same
    # original input/reference closure plus small code manifests is used there.
    execution_files={**base['files'],**source_files,str(ORIGINAL):digest(ORIGINAL),str(VALIDATION_AUDIT):digest(VALIDATION_AUDIT),str(VALIDATION/'plan.json'):digest(VALIDATION/'plan.json')}
    files.update(execution_files)
    for p in [ROOT/'tests/test_training_order_control.py',ROOT/'results/training_order_control_unit_tests_20261029_v1.log']:files[str(p)]=digest(p)
    testlog=(ROOT/'results/training_order_control_unit_tests_20261029_v1.log').read_text();require('Ran 4 tests' in testlog and testlog.rstrip().endswith('OK'),'Order-control tests did not pass')
    old=ROOT/'scripts/check_source_to_route_training_statistics_v2.py';new=ROOT/'scripts/check_training_order_control_v1.py'
    def sequence_ast(p):return ast.dump(next(n for n in ast.parse(p.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='check_sequence'))
    require(sequence_ast(old)==sequence_ast(new),'Actual sequential execution verifier changed')
    files[str(old)]=digest(old)
    VALIDATION_OUT.mkdir()
    for label,command,marker in [
        ('driver_before_preparation',[sys.executable,str(ROOT/'scripts/run_training_order_control_v1.py')],PREPARATION.name),
        ('checker_before_trial',[sys.executable,str(new),str(OUT),'--output',str(VALIDATION_OUT/'must_not_exist.json')],str(OUT/'plan.json'))]:
        start=time.monotonic();r=subprocess.run(command,cwd=ROOT,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=20)
        log=VALIDATION_OUT/(label+'.log');log.write_text(r.stdout)
        require(r.returncode==1 and marker in r.stdout,'Wrong early rejection '+label)
        receipt=VALIDATION_OUT/(label+'.receipt.json');atomic(receipt,dict(command=command,exit_code=r.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=digest(log)))
        for p in [log,receipt]:files[str(p)]=digest(p)
    require(not OUT.exists() and not CONTROL.exists() and not FINAL.exists() and not (VALIDATION_OUT/'must_not_exist.json').exists(),'Early trial/report created')
    verify(files)
    atomic(PREPARATION,dict(status='six_permutation_full_workload_cpu_control_prepared_not_executed',orders=schedule(),conditions=base['jobs'],workers=18,batches_per_worker=2,nets_per_batch=1062,
       original_counts=worker['counts'],cpu=CPU,worker_as_bytes=AS_BYTES,resource_policy=POLICY,files=files,execution_files=execution_files,
       original_worker_sha256=digest(DRIVER),original_block_checker_sha256=digest(BLOCK_CHECKER),original_seven_block_report_sha256=digest(ORIGINAL),
       source_sequence_verifier_ast_unchanged=True,unit_tests=4,actual_early_rejections=2,executed=False,
       limitations=['Post-hoc supplemental order control, frozen before execution; all six permutations run once, not selected by outcome.',
         'Full fresh training, original generated inputs and both complete1062-net outputs; original14-instance site model/algorithm/cache4096/budgets remain.',
         'Each position is occupied twice by each condition; each pair precedes the other three times. No cache flush or exclusive machine.',
         'Original seven-block measurements retained separately. No pooling, overwritten evidence, automatic retry or reduced scope.',
         'Full historical integrity validation occurs before launch; individual worker startup retains original input/reference closure plus code manifests.',
         'Finite16GiB process AS/core0/CPU121 and new-OOM-event protection; no rawfree gate. Shared active RTL may affect timings and remains disclosed.']))
    print(PREPARATION)

if __name__=='__main__':main()
