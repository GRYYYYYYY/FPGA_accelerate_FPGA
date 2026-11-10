#!/usr/bin/env python3
"""Freeze complete existing inputs and validate new full30/read entries without launching a solver."""
import ast
import json
from pathlib import Path
import subprocess
from check_vitis_kernel import digest,require
from snapshot_read_serial_prerequisites_v1 import ROOT,SNAPSHOT,READ,ADDRESS

BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
OUT=ROOT/'data/derived/snapshot_read_entry_validation_20261029_v1'
REPORT=ROOT/'results/snapshot_read_serial_preparation_20261029_v1.json'


def function(path,name):
    return next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name)


def phase_tail(path):
    main=function(path,'main')
    body=next(n.body for n in main.body if isinstance(n,ast.Try))
    index=next(i for i,n in enumerate(body) if isinstance(n,ast.For) and ast.unparse(n.target)=='(phase, command, cwd)')
    return ast.dump(ast.Module(body=body[index+1:],type_ignores=[]),include_attributes=False)


def main():
    require(not REPORT.exists(),'Refuse overwrite')
    files={};validation=[]
    def bind(path):files[str(path)]=digest(path)
    for name in ['snapshot_dpi_storage_preflight_audit_20261025_v1.json','search_read_control_staging_full_depth_setup_audit_20261025_v1.json',ADDRESS]:
        path=ROOT/'results'/name;r=json.loads(path.read_text());bind(path)
        for p,h in r['files'].items():
            require(p not in files or files[p]==h,'Conflicting prepared evidence')
            if p not in files:require(digest(p)==h,'Changed full-scope evidence '+p)
            files[p]=h
    parent=BASE/'snapshot_rtl_local_recovery/plan.json';old=json.loads(parent.read_text());bind(parent)
    for p,h in old['copied'].items():
        path=Path(p)
        if 'rtldatafile' in path.parts or 'performance.result' in path.name or path.suffix in ['.log','.pb','.jou']:continue
        require(digest(path)==h,'Changed original snapshot input');files[p]=h
    scripts=['run_snapshot_dpi_rtl_v3.py','check_snapshot_dpi_rtl_v3.py','run_snapshot_dpi_rtl_v5.py','check_snapshot_dpi_rtl_v5.py',
             'run_search_read_control_staging_dpi_rtl_v2.py','check_search_read_control_staging_dpi_rtl_v2.py',
             'run_search_read_control_staging_dpi_rtl_v4.py','check_search_read_control_staging_dpi_rtl_v4.py',
             'run_full_scope_phase_v1.py','owned_sim_resource_policy_v1.py','snapshot_read_serial_prerequisites_v1.py',
             'supervise_snapshot_read_serial_v1.py','prepare_snapshot_read_serial_v1.py','route_tree_serial_prerequisites_v1.py',
             'binary_nonzero_full44_prerequisites_v2.py','resident_snapshot_rtl_contract.py','snapshot_dpi_output_oracle_v1.py',
             'check_vitis_kernel.py','run_compact_nonzero_native_rtl_v2.py','run_compact_native_stack_recovery_v3.py',
             'check_search_packet_width_rtl.py','search_packet_width_rtl.py','transform_axi_memory_dpi_v2.py',
             'check_axi_dpi_storage_edits_v1.py']
    for name in scripts:bind(ROOT/'scripts'/name)
    for a,b in [('run_snapshot_dpi_rtl_v3.py','run_snapshot_dpi_rtl_v5.py'),('run_search_read_control_staging_dpi_rtl_v2.py','run_search_read_control_staging_dpi_rtl_v4.py')]:
        require(phase_tail(ROOT/'scripts'/a)==phase_tail(ROOT/'scripts'/b),'Original complete final oracle sequence changed')
        validation.append(dict(old=a,new=b,final_full_output_oracle_tail_ast_identical=True))
    require(ast.dump(function(ROOT/'scripts/run_snapshot_dpi_rtl_v3.py','monitor'))==ast.dump(function(ROOT/'scripts/run_snapshot_dpi_rtl_v5.py','monitor')),'RO monitor function changed')
    for driver,checker,stage in [
        ('run_snapshot_dpi_rtl_v5.py','check_snapshot_dpi_rtl_v5.py','full30_snapshot_dpi_rtl_c_and_complete_output_oracles_pending_independent_audit'),
        ('run_search_read_control_staging_dpi_rtl_v4.py','check_search_read_control_staging_dpi_rtl_v4.py','candidate_full_rtl_outputs_and_original_c_oracle_equal_pending_independent_audit')]:
        for name in [driver,checker]:
            tree=ast.parse((ROOT/'scripts'/name).read_text())
            require(stage in [n.value for n in ast.walk(tree) if isinstance(n,ast.Constant) and isinstance(n.value,str)],'Driver/checker completion contract differs')
    receipts=[]
    for label,driver,checker,trial,report in [
        ('snapshot','run_snapshot_dpi_rtl_v5.py','check_snapshot_dpi_rtl_v5.py',BASE/'snapshot_dpi_rtl_v5',ROOT/'results'/SNAPSHOT),
        ('read','run_search_read_control_staging_dpi_rtl_v4.py','check_search_read_control_staging_dpi_rtl_v4.py',BASE/'search_read_control_staging_dpi_rtl_v4',ROOT/'results'/READ)]:
        require(not trial.exists() and not report.exists(),'Trial/report already exists')
        fake=OUT/(label+'_running_rejection');fake.mkdir()
        (fake/'state.json').write_text(json.dumps(dict(owner_pid=0,status='running',stage='rtl'))+'\n')
        for phase,command in [('driver',['python3',str(ROOT/'scripts'/driver)]),('checker',['python3',str(ROOT/'scripts'/checker),'--bundle',str(fake),'--output',str(fake/'unexpected_acceptance.json')])]:
            lp=OUT/(label+'_'+phase+'_early_rejection.log')
            with lp.open('x') as log:code=subprocess.run(command,cwd=ROOT,stdout=log,stderr=subprocess.STDOUT).returncode
            require(code==1 and not report.exists() and not trial.exists() and not (fake/'unexpected_acceptance.json').exists(),'Premature execution/acceptance')
            text=lp.read_text();require('prerequisite missing: compact_nonzero_native_rtl_audit_20261029_v2.json' in text or phase=='checker' and label=='read' and 'Actual full replay incomplete' in text,'Unexpected rejection failure')
            receipts.append(dict(label=label,phase=phase,command=command,exit_code=code,log=str(lp),log_sha256=digest(lp)))
    (OUT/'early_rejection_receipts.json').write_text(json.dumps(receipts,indent=2)+'\n')
    for p in OUT.rglob('*'):
        if p.is_file():bind(p)
    for name in ['test_snapshot_read_serial_prerequisites.py','test_full_scope_phase_resource_abort.py']:bind(ROOT/'tests'/name)
    result=dict(status='full30_snapshot_and_full2tx_read_original_scope_serial_entries_prepared',files=files,
                transactions=[30,2],pointers=[13,13],models=[10,7],pages=[4,4],snapshot_readonly_models=8,
                unchanged_final_oracles=validation,actual_early_rejection_cases=4,
                resource_policy='no_free_memory_gate_finite_process_as_abort_on_new_oom_v1',process_as_bytes=64*1024**3,
                startup_and_runtime_rawfree_gate_removed=True,xsc_single_threaded=True,
                execution_started=False,full_rtl_verified=False,
                limits=['Preparation retains the original source, pointer environments, dimensions and complete output oracles; no full RTL acceptance inferred.',
                        'Actual typed current native/CSR/compact/full50 acceptance is required before snapshot; full30 acceptance before read-control.',
                        'Four prerequisite unit tests and one owned-process injected-OOM test passed via exec_command this turn; source files bound here.'])
    with REPORT.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'],len(files),'bindings')


if __name__=='__main__':main()
