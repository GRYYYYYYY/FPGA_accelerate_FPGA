#!/usr/bin/env python3
"""Audit the actual complete encoded DUT, address environment and original C oracle."""
import argparse
import json
import os
from pathlib import Path
import re
from paired_binary_nonzero_contract_v2 import *
from binary_nonzero_full44_prerequisites_v1 import validate,ENCODED_STATUS,encoded_scope


def audit(mode):
    bindings=validate(mode);c=config(mode);out=c['trial'];state=json.loads((out/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='binary_nonzero_full44_original_C_and_snapshots_complete_independent_audit_pending','Actual full4tx execution incomplete')
    entry,prepared_files=prepared(mode);expected,original_files,env=source_contract(mode)
    plan=json.loads((out/'plan.json').read_text());require(plan['preparation_sha256']==digest(PREPORT) and plan['commands']==commands(mode),'Different execution plan')
    require((plan['graph_mode'],plan['transactions'],plan['ports'],plan['models'],plan['pages'],plan['encoded_modules'])==(mode,4,44,30,4,c['encoded_modules']),'Different complete interface')
    require(plan['candidate_encoding_changed'] is True and plan['native_cycle_parity_claimed'] is False and plan['pointer_address_offset']==4096,'Wrong candidate identity')
    require(plan['address_space_bytes']==AS_BYTES and plan['stack_bytes']==STACK and plan['core_bytes']==0 and plan['runtime_guard_free_bytes']==GUARD_FREE and plan['startup_gate_removed_by_user'],'Different resource limits')
    files={**bindings,**prepared_files,**original_files}
    for p,h in plan['files'].items():require(digest(p)==h,'Changed executed input '+p);files[p]=h
    guard_rel='verilog/axi_model_rebase_guard_v1.sv'
    require(set(entry['manifest'])==set(expected)|{guard_rel},'Incomplete prepared full input set')
    for rel,record in expected.items():
        actual=out/'sim'/rel
        if rel=='verilog/search_batch_trace_top_v2.prj':
            require(actual.read_text()==Path(record['source']).read_text()+'sv xil_defaultlib "axi_model_rebase_guard_v1.sv"\n','Project modified beyond wrapper guard')
        else:require(digest(actual)==record['sha256'],'Actual DUT/model/pointer/fixture differs '+rel)
        files[str(actual)]=digest(actual)
    guard=out/'sim'/guard_rel;require(digest(guard)==digest(ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'),'Guard changed');files[str(guard)]=digest(guard)
    candidate=json.loads((c['candidate']/'plan.json').read_text());directory=out/'sim/verilog'
    for record in candidate['modules']:
        actual=directory/Path(record['candidate']).name
        check_delta(Path(record['original']).read_text(),actual.read_text(),json.loads(Path(record['ledger']).read_text()))
    for m in env['models']:audit_model(Path(m['source']).read_text(),(directory/Path(m['target']).name).read_text(),m['bundle'])
    expected_names={p.name for p in (c['candidate']/'verilog').iterdir() if p.is_file()}|{'axi_model_rebase_guard_v1.sv'}
    require({p.name for p in directory.iterdir() if p.is_file() and p.suffix in ['.v','.sv','.dat']}==expected_names,'Changed complete RTL/ROM/model set')
    require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 4;', (directory/'search_batch_trace_top_v2.autotb.v').read_text()),'Changed TB transaction count')
    bounded=out/'bounded.tcl';require(bounded.read_text()=='run 10 sec\nputs FULL44_NONZERO_DPI_BOUNDED_RETURNED\nquit\n','Different finite simulation bound')
    def bind(p):files[str(p)]=digest(p)
    for job in commands(mode):
        phase=job['phase'];rp=out/(phase+'.receipt.json');lp=out/(phase+'.log');receipt=json.loads(rp.read_text());text=lp.read_text(errors='replace')
        require(all(receipt[k]==v for k,v in job.items()) and receipt['plan_sha256']==digest(out/'plan.json'),'Different executed command')
        require(receipt['exit_code']==0 and receipt['resource_abort'] is False and receipt['resource_abort_observation'] is None and receipt['elapsed_seconds']>0 and receipt['log_sha256']==digest(lp),'Failed/aborted/changed phase')
        require(not any(e in text for e in ERRORS),'Execution error present')
        ap=out/(phase+'.actual_limits.json')
        if phase in ['elaborate','rtl']:require(ap.is_file(),'Actual compiler/kernel limits missing')
        if ap.exists():
            actual=json.loads(ap.read_text());require(actual['address_space']==[AS_BYTES,AS_BYTES] and actual['stack']==[STACK,STACK] and actual['core']==[0,0] and actual['cpu']==[122] and actual['cwd']==job['cwd'],'Wrong actual limits/cwd')
            require(Path(actual['command'].split()[0]).name=={'xsc':'xsc','elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase],'Different observed process');bind(ap)
        if phase=='xsc':require('Turned off multi-threading.' in text,'Different XSC thread policy')
        if phase=='rtl':
            require(re.search(r'RTL Simulation :\s*4 / 4',text) and text.splitlines().count('FULL44_NONZERO_DPI_BOUNDED_RETURNED')==1,'Incomplete actual4tx')
            allocated=re.findall(r'A_DPI_REGISTER id=(\d+) name=(\S+) bits=(\d+) depth=(\d+) pages=(\d+)',text)
            expected_dims={m['bundle']:tuple(m['width_depth_pages']) for m in env['models']};actual_dims={}
            for ident,name,width,depth,pages in allocated:
                match=re.search(r'\.AESL_AXI_MASTER_(\w+)\.original_model\.',name)
                require(match is not None and match[1] not in actual_dims,'Unknown/repeated full model allocation')
                actual_dims[match[1]]=(int(width),int(depth),int(pages))
            require(len(allocated)==30 and sorted(int(a[0]) for a in allocated)==list(range(30)) and actual_dims==expected_dims,'Incomplete actual30-model/4page allocation')
        if phase=='postcheck':require('SEARCH_BATCH_PASS mode='+str(mode) in text and text.splitlines().count(f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4')==1,'Missing complete original C oracle')
        bind(rp);bind(lp)
    perf=directory/'search_batch_trace_top_v2.performance.result.transaction.xml'
    cycles=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',perf.read_text(),re.M)]
    require([i for i,v in cycles]==list(range(4)) and all(v>0 for i,v in cycles) and state['cycles']==[v for i,v in cycles],'Incomplete cycles');bind(perf)
    snapshots=[]
    for i in range(4):
        actual=out/f'rtl_{mode}_{i}.bin';golden=c['golden']/f'hls_{mode}_{i}.bin'
        require(actual.stat().st_size==golden.stat().st_size==946498280 and digest(actual)==digest(golden),'Full44 snapshot differs')
        bind(actual);bind(golden);snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=files[str(actual)]))
    outputs=list((out/'sim/tv/rtldatafile').glob('rtl.*.dat'));refs=list((c['parent']/'sim/tv/cdatafile').glob('c.*.autotvout_*.dat'))
    require(len(outputs)==len(refs)==25 and {p.name for p in outputs}=={'rtl.'+p.name[2:] for p in refs},'Missing complete output file set')
    for p in [*outputs,out/'plan.json',out/'state.json',bounded,PREPORT,directory/'xsim.dir/work/xsc/dpi.so',Path(__file__).resolve()]:bind(p)
    report=dict(status=ENCODED_STATUS,files=files,graph_mode=mode,transactions=4,ports=44,models=30,pages=4,encoded_modules=c['encoded_modules'],
                cycles=[v for i,v in cycles],snapshots=snapshots,rtl_verified=True,candidate_encoding_changed=True,native_cycle_parity_claimed=False,
                pointer_address_offset=4096,general_formal_equivalence_proven=False,physical_timing_verified=False,board_verified=False,
                limits=['Complete original synthetic full44 transactions and full capacities; not real workload/platform execution.',
                        'Existing43/45-module encoding plus reviewed verification-only address relocation; previous failed/unfinished trials remain separate.',
                        'No physical resource fit, timing closure, bandwidth, power or acceleration claim.'])
    encoded_scope(report,mode);return report


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--mode',type=int,choices=[0,1],required=True);args=p.parse_args();output=config(args.mode)['output']
    require(not output.exists(),'Refuse overwrite');report=audit(args.mode);temporary=output.with_suffix('.json.tmp')
    with temporary.open('x') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,output);print(report['status'])
