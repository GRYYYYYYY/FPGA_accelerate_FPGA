#!/usr/bin/env python3
"""Independently check fresh paired-mode C/RTL setup, not RTL execution."""
import argparse
import json
from pathlib import Path
import shlex
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require
from owned_sim_resource_policy_v1 import abort_reason, POLICY
from prepare_collision_safe_bus64_cosim_v1 import ROOT, BASE, REVIEW, HLS
from search_kernel_memory_plan import parse_source


def audit(mode):
    out=BASE/'collision_safe_bus64_cosim_setup_v1'/f'mode_{mode}'
    require((out/'setup.json').is_file(), 'Fresh paired-mode setup report missing')
    result=json.loads((out/'setup.json').read_text());state=json.loads((out/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='fresh_setup_verified_rtl_preparation_pending', 'Setup not complete')
    require(result['status']=='collision_safe_bus64_full44_four_transaction_csim_and_fresh_setup_verified_rtl_pending' and
            (result['graph_mode'],result['transactions'],result['ports'],result['models'])==(mode,4,44,30) and
            result['rtl_executed'] is False, 'Different setup scope')
    files={}
    def bind(p):
        checksum=digest(p)
        require(str(p) not in files or files[str(p)]==checksum, 'Conflicting evidence binding')
        files[str(p)]=checksum
        return checksum
    for name,checksum in result['files'].items():require(bind(name)==checksum, 'Changed generated setup '+name)
    review=json.loads(REVIEW.read_text())
    require(review['status']=='collision_safe_bus64_pair_full8_C_and_HLS_independently_verified_RTL_pending', 'Wrong paired HLS gate')
    for name,checksum in review['files'].items():require(bind(name)==checksum, 'Changed independently reviewed pair '+name)
    original=BASE/'collision_safe_bus64_pair_v1'/f'mode_{mode}';project=out/'project'
    require(result['project']==str(project), 'Wrong fresh project')
    source=out/'source'
    require({p.name for p in source.iterdir()}=={p.name for p in (original/'source').iterdir()}, 'Different source set')
    for p in source.iterdir():require(bind(p)==bind(original/'source'/p.name), 'Changed full source/testbench')
    args=parse_source(source/'search_batch_trace_top_v2.cpp')
    require(len(args)==45 and sum(a['pointer'] for a in args)==44, 'Changed full top interface')
    expected_synthesis={}
    for p in (original/'project/solution/syn').rglob('*'):
        if not p.is_file():continue
        target=project/p.relative_to(original/'project')
        require(bind(p)==bind(target), 'Different synthesized RTL/report/ROM')
        expected_synthesis[str(p)]=files[str(p)];expected_synthesis[str(target)]=files[str(target)]
    plan=json.loads((out/'plan.json').read_text())
    require(plan['synthesis']==expected_synthesis and plan['resource_policy']==POLICY and
            (plan['transactions'],plan['ports'],plan['graph_mode'])==(4,44,mode), 'Wrong setup plan')
    for name,checksum in plan['files'].items():require(bind(name)==checksum, 'Changed setup input')
    expected_tcl='cd {'+str(out)+'}\nopen_project project\nopen_solution solution\ncsim_design -clean\nputs COLLISION_SAFE_FULL44_CSIM_COMPLETE\ncosim_design -rtl verilog -trace_level none -setup\nputs COLLISION_SAFE_FULL44_SETUP_COMPLETE\nexit\n'
    require((out/'prepare.tcl').read_text()==expected_tcl, 'Different setup-only flow')
    command=['prlimit','--as=68719476736:68719476736','--stack=67108864:67108864','--core=0:0','--',str(HLS),'-f',str(out/'prepare.tcl')]
    receipt=json.loads((out/'prepare.receipt.json').read_text());actual=json.loads((out/'actual_limits.json').read_text())
    require(plan['command']==receipt['command']==command and receipt['exit_code']==0 and receipt['abort_reason'] is None and
            receipt['actual_limits']==actual and receipt['elapsed_seconds']>0 and
            abort_reason(plan['initial_memory'],receipt['final_memory']) is None, 'Setup failed/changed or OOM/reset')
    require(actual['address_space']==[64*1024**3]*2 and actual['stack']==[64*1024**2]*2 and actual['core']==[0,0] and
            actual['pid']>0 and int(actual['start_ticks'])>0, 'Actual HLS limits/identity missing')
    argv=shlex.split(actual['command'])
    require(Path(argv[0]).name=='vitis_hls' and '-f' in argv and argv[argv.index('-f')+1]==str(out/'prepare.tcl'), 'Different actual HLS flow')
    log=out/'prepare.log';text=log.read_text(errors='replace')
    require(bind(log)==receipt['log_sha256'] and not any(x in text for x in ['ERROR:','Fatal:','LLVM ERROR','runtime error:']), 'Setup log failure')
    for marker in ['COLLISION_SAFE_FULL44_CSIM_COMPLETE','COLLISION_SAFE_FULL44_SETUP_COMPLETE',
                   f'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode={mode} ports=44 transactions=4',f'SEARCH_BATCH_PASS mode={mode}']:
        require(marker in text, 'Missing full setup marker')
    app=ET.parse(project/'hls.app').getroot();sources=app.findall('files/file')
    require(len(sources)==2, 'Wrong HLS source list')
    for entry in sources:
        name=Path(entry.attrib['name']).name;tb=entry.attrib.get('tb') in ('1','true')
        require(name==('test_compressed_batch_rtl_full_depth.cpp' if tb else 'search_batch_trace_top_v2.cpp'), 'Different DUT/testbench')
        require(Path(entry.attrib['name'])==(source/name if tb else original/'source'/name), 'Different actual source path')
        flags=shlex.split(entry.attrib.get('cflags',''))
        require([f for f in flags if f.startswith('-D')]==[f'-DSEARCH_GRAPH_MODE={mode}'], 'Different mode/extra test macros')
    comparisons=[]
    for tx in range(4):
        p=out/f'hls_{mode}_{tx}.bin';golden=BASE/'compressed_batch_rtl_tb_cpu_v2'/f'cpu_{mode}_{tx}.bin'
        require(p.stat().st_size==golden.stat().st_size==946498280 and bind(p)==bind(golden), 'Full44 snapshot mismatch')
        comparisons.append(dict(transaction=tx,target=str(p),reference=str(golden),sha256=files[str(p)]))
    require(result['comparisons']==comparisons, 'Comparison receipt differs')
    rtl=project/'solution/sim/verilog';inv=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    bundles={p['bundle'] for p in json.loads(inv.read_text())['ports']}
    require(len(bundles)==30 and {p.name for p in rtl.glob('AESL_axi_master_*.v')}=={'AESL_axi_master_'+b+'.v' for b in bundles}, 'Missing/extra AXI models')
    require('parameter AUTOTB_TRANSACTION_NUM = 4;' in (rtl/'search_batch_trace_top_v2.autotb.v').read_text(), 'Incomplete transaction count')
    for p in (project/'solution/syn/verilog').iterdir():
        if p.is_file() and p.suffix in ('.v','.dat'):require(bind(rtl/p.name)==bind(p), 'Actual simulation DUT/ROM changed')
    for p in (project/'solution/sim').rglob('*'):
        if p.is_file():bind(p)
    for p in [out/'state.json',out/'setup.json',out/'plan.json',out/'prepare.receipt.json',out/'actual_limits.json',
              project/'hls.app',REVIEW,inv,Path(__file__).resolve(),ROOT/'scripts/search_kernel_memory_plan.py']:bind(p)
    return dict(status='collision_safe_bus64_mode_full44_fresh_setup_independently_verified_RTL_pending',files=files,
                graph_mode=mode,transactions=4,ports=44,models=30,project=str(project),rtl_executed=False,
                limits=['Fresh zero-based models/vectors only; allocation, original guards and nonzero pointer mapping remain required.',
                        'No RTL, physical implementation, bandwidth, power or board acceptance.'])


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--mode',type=int,choices=[0,1],required=True)
    args=parser.parse_args();output=ROOT/f'results/collision_safe_bus64_cosim_mode_{args.mode}_audit_20261030_v1.json'
    require(not output.exists(), 'Refuse overwrite');result=audit(args.mode)
    with output.open('x') as stream:json.dump(result,stream,indent=2);stream.write('\n')
    print(result['status'])
