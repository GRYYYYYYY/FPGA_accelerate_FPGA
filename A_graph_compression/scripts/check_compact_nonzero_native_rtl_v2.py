#!/usr/bin/env python3
"""Independently accept only complete nonzero-address native RTL and original C."""
import argparse
import json
from pathlib import Path
import re
from compact_nonzero_native_contract_v2 import *


def audit():
    state=json.loads((OUT/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='full4tx_original_postcheck_complete_independent_audit_pending','Actual full RTL and postcheck not complete')
    prep=verify_preparation();files,vectors,models=evidence();files.update(prep['files'])
    plan=json.loads((OUT/'plan.json').read_text())
    require(plan['preparation']==str(PREPORT) and plan['preparation_sha256']==digest(PREPORT) and plan['commands']==commands(),'Different actual trial')
    require((plan['transactions'],plan['pointers'],plan['models'])==(4,44,30) and plan['startup_gate_removed_by_user'] and plan['free_memory_gate_removed_by_user'] and plan['resource_policy']==POLICY,'Scope changed')
    require(plan['driver_sha256']==digest(ROOT/'scripts/run_compact_nonzero_native_rtl_v2.py'),'Driver changed')
    def bind(p): files[str(p)]=digest(p)
    for relative,row in prep['manifest'].items():
        actual=OUT/'sim'/relative;require(digest(actual)==row['sha256'],'Actual full input modified '+relative);bind(actual)
    for m in models['models']:
        audit_model(Path(m['source']).read_text(),(OUT/'sim/verilog'/Path(m['target']).name).read_text(),m['bundle'])
    project=OUT/'sim/verilog/search_batch_trace_top_v2.prj'
    require(project.read_text()==(OLD/'sim/verilog/search_batch_trace_top_v2.prj').read_text()+'sv xil_defaultlib "axi_model_rebase_guard_v1.sv"\n','Project changed beyond guard addition')
    require(plan['bounded_tcl_sha256']==digest(OUT/'bounded.tcl') and (OUT/'bounded.tcl').read_text()=='run 10 sec\nputs COMPACT_NONZERO_NATIVE_BOUNDED_RETURNED\nquit\n','Different simulation bound')
    for job in commands():
        phase=job['phase'];rp=OUT/(phase+'.receipt.json');lp=OUT/(phase+'.log');ap=OUT/(phase+'.actual_limits.json')
        receipt=json.loads(rp.read_text());text=lp.read_text(errors='replace');actual=json.loads(ap.read_text())
        require(all(receipt[k]==v for k,v in job.items()),'Different executed command')
        require(receipt['exit_code']==0 and receipt['resource_abort'] is False and receipt['resource_abort_observation'] is None and receipt['log_sha256']==digest(lp) and receipt['elapsed_seconds']>0,'Failed/aborted/changed phase')
        require(receipt['resource_policy']==POLICY and abort_reason(plan['startup_memory'],receipt['end_memory']) is None,'Different resource policy or OOM during trial')
        require(not any(e in text for e in ERRORS),'Execution error present')
        require(actual['address_space']==([COMPILER_AS,COMPILER_AS] if phase=='elaborate' else [RUNTIME_AS,RUNTIME_AS]) and actual['stack']==[STACK,STACK] and actual['core']==[0,0] and actual['cwd']==job['cwd'],'Actual limits/cwd mismatch')
        expected={'elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase]
        require(Path(actual['command'].split()[0]).name==expected,'Unexpected phase process')
        if phase=='rtl': require(re.search(r'RTL Simulation :\s*4 / 4',text) is not None,'Partial RTL')
        if phase=='postcheck': require('SEARCH_BATCH_PASS mode=1' in text and 'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text,'Original C postcheck missing')
        for p in [rp,lp,ap]: bind(p)
    perf=OUT/'sim/verilog/search_batch_trace_top_v2.performance.result.transaction.xml'
    rows=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
    require([i for i,c in rows]==list(range(4)) and all(c>0 for i,c in rows),'Incomplete positive actual cycles');bind(perf)
    snapshots=[]
    for i in range(4):
        actual=OUT/f'rtl_1_{i}.bin';golden=BASE/f'compressed_batch_compact_cosim_setup/hls_1_{i}.bin'
        require(actual.stat().st_size==golden.stat().st_size==946498280 and digest(actual)==digest(golden),'Different full44 output snapshot')
        bind(actual);bind(golden);snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=files[str(actual)]))
    raw=list((OUT/'sim/tv/rtldatafile').glob('rtl.*.dat'))
    oldraw=list((OLD/'sim/tv/rtldatafile').glob('rtl.*.dat'))
    require(len(raw)==25 and {p.name for p in raw}=={p.name for p in oldraw},'Missing full raw output collection')
    for p in raw: bind(p)
    for p in [OUT/'plan.json',OUT/'state.json',OUT/'bounded.tcl',PREPORT,Path(__file__).resolve()]:bind(p)
    return dict(status='compact_nonzero_native_full4tx_full44_original_DUT_and_C_oracle_verified',files=files,
                cycles=[c for i,c in rows],snapshots=snapshots,transactions=4,pointers=44,models=30,pages=4,
                resource_policy=POLICY,compiler_as_bytes=COMPILER_AS,runtime_as_bytes=RUNTIME_AS,trial=str(OUT),dut_unchanged=True,pointer_address_offset=4096,rtl_verified=True,physical_timing_verified=False,board_verified=False,
                limits=['Full original synthetic transactions and declared depths; not real routing traffic or platform execution.',
                        'Verification environment relocates physical pointers by4096; original model contents and production DUT remain unchanged.',
                        'Previous zero-address v3 failure remains a failed result; this is a new distinct trial.',
                        'No physical timing, bandwidth, power, or speedup claim.'])


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,default=ACCEPTED);args=p.parse_args()
    require(not args.output.exists(),'Refuse overwrite');result=audit()
    with args.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(result['status'])
