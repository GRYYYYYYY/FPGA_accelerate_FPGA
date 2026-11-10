#!/usr/bin/env python3
"""Audit actual full44 batch execution; prepared models never imply RTL acceptance."""
import argparse
import json
import os
import re
import shlex
from pathlib import Path
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def audit(bundle,output):
    require(not output.exists(),'Refuse overwrite')
    state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='full44_four_transaction_dpi_rtl_and_c_oracle_pending_independent_audit','Actual full44 DPI RTL execution incomplete')
    plan=json.loads((bundle/'plan.json').read_text())
    require(plan['per_process_address_space_limit_bytes']==160*1024**3 and plan['core_dump_limit_bytes']==0,'Missing full-batch resource limits')
    require(plan['transactions']==4 and plan['ports']==44 and plan['graph_mode']==0 and plan['depths_unchanged'] and plan['pages_unchanged'] and plan['simulation_bound_ns']==10000000000,'Different execution scope')
    files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed frozen execution input '+p)
    gate_path=ROOT/'results/search_axi_dpi_replay_audit_20261025_v3.json'
    gate=json.loads(gate_path.read_text())
    require(gate['status']=='full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified','Missing prerequisite parity')
    preflight=ROOT/'data/derived/compressed_bus64_dpi_models_preflight_20261025_v1'
    conversion=json.loads((preflight/'plan.json').read_text())
    preaudit_path=ROOT/'results/compressed_bus64_dpi_storage_preflight_audit_20261025_v1.json'
    preaudit=json.loads(preaudit_path.read_text())
    require(len(preaudit['models'])==30 and len(plan['models'])==30,'Different AXI model matrix')
    for r in [gate,preaudit]:
        for p,h in r['files'].items():require(digest(p)==h,'Changed parity/preflight proof '+p);files[p]=h
    directory=bundle/'sim/verilog';parent=BASE/'compressed_batch_bus64_rtl_guarded_v1'
    originals=parent/'sim/verilog';prepared=json.loads((parent/'plan.json').read_text())
    allocation_path=ROOT/'results/compressed_batch_bus64_cosim_allocations_20261025_v1.json'
    require(digest(allocation_path)==prepared['allocation_sha256'],'Changed allocation proof')
    allocation=json.loads(allocation_path.read_text())
    inventory_path=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    inventory=json.loads(inventory_path.read_text());ports={r['name']:r for r in inventory['ports']}
    expected_ro={ports[g['regions'][0]['name']]['bundle']:[r for r in g['regions'] if r['readonly']] for g in allocation['allocations'] if any(r['readonly'] for r in g['regions'])}
    require({m['bundle']:m['readonly'] for m in prepared['models']}==expected_ro,'Different readonly guard coverage')
    setup_path=ROOT/'results/compressed_batch_bus64_full_depth_cosim_setup_20261025_v1.json';setup=json.loads(setup_path.read_text())
    original_sim=Path(setup['project'])/'solution/sim/verilog'
    for m in prepared['models']:
        name='AESL_axi_master_'+m['bundle']+'.v';text=(originals/name).read_text()
        marker='\n// Independent conservative read-only AXI burst guard.\n'
        require(text.count(marker)==1 and text.split(marker)[0]+'endmodule'+text.rsplit('endmodule',1)[1]==(original_sim/name).read_text(),'Modification beyond readonly guard')
    guard_path=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json';guard=json.loads(guard_path.read_text())
    require(guard['cases']==9,'Missing executed guard cases')
    for record in guard['records']:
        p=BASE/'compressed_axi_guard_tests_v2'/(record['name']+'.log')
        require(digest(p)==record['log_sha256'],'Changed executed guard log');files[str(p)]=digest(p)
    for p in [allocation_path,inventory_path,guard_path]:files[str(p)]=digest(p)
    expected={Path(m['path']).name:m for m in conversion['models']}
    require(len(expected)==30 and {Path(m['path']).name for m in plan['models']}==set(expected),'Incomplete converted model set')
    for name,m in expected.items():
        target=directory/name
        require(digest(target)==m['after_sha256'] and digest(originals/name)==m['before_sha256'],'Different executed model '+name)
        record=next(r for r in plan['models'] if Path(r['path']).name==name)
        require(record=={**m,'path':str(target)},'Model record changed')
    for pattern in ['*.v','*.dat']:
        require({p.name for p in directory.glob(pattern)}=={p.name for p in originals.glob(pattern)},'Different complete RTL/ROM file set')
        for source in originals.glob(pattern):
            target=directory/source.name
            if source.name not in expected:require(digest(target)==digest(source),'Changed DUT/ROM '+source.name)
            files[str(target)]=digest(target)
    for p,h in prepared['copied_files'].items():
        source=Path(p);target=bundle/'sim'/source.relative_to(parent/'sim')
        if 'rtldatafile' in source.parts or 'performance.result' in source.name or source.suffix in ['.log','.pb','.jou']:continue
        require(digest(target)==h,'Changed full input fixture/C postcheck '+str(target));files[str(target)]=h
    require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 4;', (directory/'search_batch_trace_top_v2.autotb.v').read_text()),'Wrong actual transaction count')
    commands=[shlex.split(line) for line in (directory/'run_xsim.sh').read_text().splitlines() if line.strip() and not line.startswith('#')]
    require(len(commands)==2,'Different generated flow')
    prefix=['prlimit','--stack=67108864:67108864','--core=0:0','--as=171798691840:171798691840','--','taskset','-c','122'];pc=bundle/'sim/wrapc_pc'
    expected_commands=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14',str(ROOT/'hardware/sim/axi_dpi_memory_v1.cpp')],directory),
        ('elaborate',prefix+['/usr/bin/time','-v']+commands[0]+['-mt','off','--O0','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),
        ('rtl',prefix+commands[1][:-1]+[str(bundle/'bounded.tcl')],directory),('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
    require(plan['commands']==[dict(phase=n,command=c,cwd=str(d)) for n,c,d in expected_commands],'Different actual commands')
    for phase,command,cwd in expected_commands:
        receipt=bundle/(phase+'.receipt.json');log=bundle/(phase+'.log');r=json.loads(receipt.read_text());text=log.read_text(errors='replace')
        require(r['exit_code']==0 and r['resource_admission_abort'] is False and r['command']==command and r['cwd']==str(cwd) and r['plan_sha256']==digest(bundle/'plan.json') and r['log_sha256']==digest(log),'Failed/different phase '+phase)
        require(not any(x in text for x in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST']),'Execution failure '+phase)
        if phase=='rtl':require(re.search(r'RTL Simulation :\s*4 / 4',text) and text.splitlines().count('FULL44_DPI_BOUNDED_RETURNED')==1,'Incomplete bounded RTL execution')
        if phase=='postcheck':require('SEARCH_BATCH_PASS mode=0' in text and text.splitlines().count('FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=0 ports=44 transactions=4')==1,'Original full44 C oracle missing')
        for p in [receipt,log]:files[str(p)]=digest(p)
    performance=directory/'search_batch_trace_top_v2.performance.result.transaction.xml'
    rows=[tuple(map(int,m)) for m in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',performance.read_text(),re.M)]
    require([i for i,c in rows]==list(range(4)) and all(c>0 for i,c in rows) and state['cycles']==[c for i,c in rows],'Incomplete/different cycles')
    snapshots=[]
    for i in range(4):
        actual=bundle/f'rtl_0_{i}.bin';reference=BASE/f'compressed_batch_bus64_cosim_setup/hls_0_{i}.bin'
        require(setup['files'][str(reference)]==digest(reference),'Changed accepted full snapshot reference')
        require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==digest(reference),'Complete full44 snapshot differs')
        for p in [actual,reference]:files[str(p)]=digest(p)
        snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=digest(actual)))
    outputs=list((bundle/'sim/tv/rtldatafile').glob('*'));require(outputs,'Missing actual RTL outputs')
    for p in [*outputs,bundle/'plan.json',bundle/'state.json',performance,setup_path,gate_path,preaudit_path,directory/'xsim.dir/work/xsc/dpi.so',Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py']:
        if p.is_file():files[str(p)]=digest(p)
    result=dict(status='compressed_bus64_full44_four_transaction_dpi_rtl_c_postcheck_and_complete_snapshots_independently_verified',
                cycles=[c for i,c in rows],snapshots=snapshots,models=30,ports=44,files=files,
                limits=['Four synthetic transactions at original declared capacities, not full production workload RTL',
                        'No mapped platform fit, timing closure, board bandwidth, power or acceleration claim'])
    temporary=output.with_suffix('.json.tmp')
    with temporary.open('x') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,output);print(result['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
