#!/usr/bin/env python3
"""Prepare both complete encoded execution entries without requiring a future pass."""
import json
from pathlib import Path
from paired_binary_nonzero_contract_v1 import *


def main():
    require(not PREP.exists() and not PREPORT.exists(),'Refuse overwrite')
    files={};rows=[]
    for name,status in [
        ('paired_binary_nonzero_axi_structure_audit_20261029_v1.json','both_encoded_modes_complete_nonzero_address_environment_structure_independently_verified'),
        ('paired_axi_rebase_dpi_independent_audit_20261029_v1.json','both_modes_native_dpi_rebase_regression_receipts_and_full_payloads_independently_rechecked')]:
        p=ROOT/'results'/name;r=json.loads(p.read_text());require(r['status']==status,'Unaccepted wrapper prerequisite')
        files[str(p)]=digest(p)
        for n,h in r['files'].items():require(digest(n)==h,'Changed wrapper prerequisite');files[n]=h
    for mode in [0,1]:
        c=config(mode);require(not c['trial'].exists() and not c['output'].exists(),'Trial/result already exists')
        manifest,bindings,env=source_contract(mode);files.update(bindings)
        folder=PREP/c['label'];folder.mkdir(parents=True)
        rel='verilog/search_batch_trace_top_v2.prj';record=manifest[rel];old=Path(record['source']).read_text()
        p=folder/'search_batch_trace_top_v2.prj';p.write_text(old+'sv xil_defaultlib "axi_model_rebase_guard_v1.sv"\n')
        record.update(source=str(p),sha256=digest(p),kind='project_guard_append');files[str(p)]=digest(p)
        guard=ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'
        manifest['verilog/axi_model_rebase_guard_v1.sv']=dict(source=str(guard),sha256=digest(guard),kind='guard');files[str(guard)]=digest(guard)
        rows.append(dict(graph_mode=mode,manifest=manifest,commands=commands(mode),transactions=4,ports=44,models=30,pages=4,
                         encoded_modules=c['encoded_modules'],address_space_bytes=AS_BYTES,stack_bytes=STACK,core_bytes=0,
                         runtime_guard_free_bytes=GUARD_FREE,startup_gate_removed_by_user=True))
    for name in ['paired_binary_nonzero_contract_v1.py','binary_nonzero_full44_prerequisites_v1.py','prepare_paired_binary_nonzero_entries_v1.py',
                 'run_binary_nonzero_full44_v1.py','check_binary_nonzero_full44_v1.py','supervise_paired_binary_nonzero_full44_v1.py',
                 'run_compact_nonzero_native_rtl_v1.py','run_compact_native_stack_recovery_v3.py','check_hls_fsm_binary_v1.py','check_compact_nonzero_axi_models_v1.py','check_vitis_kernel.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    report=dict(status='both_nonzero_encoded_full44_execution_entries_prepared_no_trial_started',modes=rows,files=files,
                execution_started=False,full_kernel_verified=False,
                limits=['Driver/checker independently require typed actual nonzero native acceptance, plus CSR actual acceptance before compact.',
                        'Same43/45 encoded modules; complete original C input/output fixtures and full snapshots preserved.',
                        'Only pointer/model address mapping and guard-project entry change; XSC explicitly single-threaded.',
                        'AS64GiB/core0/stack64MiB/CPU122/runtime16GiB preserved; no conservative startup memory gate.'])
    with PREPORT.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    for mode in [0,1]:prepared(mode)
    print(report['status'],[(m['graph_mode'],len(m['manifest'])) for m in rows])


if __name__=='__main__':main()
