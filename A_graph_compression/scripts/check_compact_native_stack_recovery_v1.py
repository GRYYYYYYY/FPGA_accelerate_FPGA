#!/usr/bin/env python3
"""Accept only actual completed CSR RTL, original postcheck, and full44 equality."""
import argparse,json,os,re,tempfile
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def audit():
    parent=BASE/'compressed_batch_compact_rtl_guarded_v1';out=BASE/'compact_native_stack_recovery_v1'
    state=json.loads((out/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='independent_final_audit_pending','Actual RTL/postcheck execution not complete')
    preparation=json.loads((parent/'state.json').read_text());require(preparation['status']=='prepared','Elaboration incomplete')
    plan=json.loads((parent/'plan.json').read_text());execution=json.loads((out/'plan.json').read_text())
    require(execution['files'][str(parent/'plan.json')]==digest(parent/'plan.json'),'Changed elaboration plan')
    setup_path=BASE/'compressed_batch_compact_cosim_setup/setup.json';setup=json.loads(setup_path.read_text())
    require(digest(setup_path)==plan['setup_sha256'],'Setup changed')
    require(digest(ROOT/'scripts/run_compressed_batch_compact_rtl_guarded.py')==plan['script_sha256'],'Elaboration driver changed')
    require(digest(ROOT/'scripts/run_compact_native_stack_recovery_v1.py')==execution['files'][str(ROOT/'scripts/run_compact_native_stack_recovery_v1.py')],'Recovery driver changed')
    require(execution['stack_bytes']==268435456 and execution['address_space_bytes']==103079215104 and execution['core_bytes']==0 and execution['transactions']==4 and execution['pointers']==44 and execution['dut_unchanged'] and execution['compiled_snapshot_unchanged'],'Different recovery controls')
    for target,record in execution['copied'].items():
        require(Path(target).is_relative_to(out/'sim') and Path(record['source'])==parent/'sim'/Path(target).relative_to(out/'sim'),'Copy provenance escaped original snapshot')
        require(digest(record['source'])==record['sha256'],'Changed original snapshot input')
        if not target.endswith('xsim_script.tcl'):
            require(digest(target)==record['sha256'],'Changed cloned snapshot input')
    prefix=['prlimit','--stack=268435456:268435456','--core=0:0','--as=103079215104:103079215104','--']
    binary='/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/xsim'
    expected_jobs=[dict(phase='rtl',command=prefix+[binary,'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(out/'bounded.tcl')],cwd=str(out/'sim/verilog')),
                   dict(phase='postcheck',command=prefix+[str(out/'sim/wrapc_pc/cosim.pc.exe')],cwd=str(out/'sim/wrapc_pc'))]
    require(execution['commands']==expected_jobs,'Changed runtime recovery commands')
    require(str(out/'sim/verilog/xsim.dir/search_batch_trace_top_v2/xsimk') in execution['copied'],'Missing original compiled snapshot binding')
    actual_limits=json.loads((out/'actual_runtime_limits.json').read_text())
    require(actual_limits['cwd']==str(out/'sim/verilog') and actual_limits['command'].startswith('xsim.dir/search_batch_trace_top_v2/xsimk '),'Different observed runtime')
    require('268435456' in actual_limits['limits'] and '103079215104' in actual_limits['limits'],'Actual runtime limits missing')
    files={}
    def bind(p):files[str(p)]=digest(p)
    for p,h in setup['files'].items():require(digest(p)==h,'Changed prepared input '+p);files[p]=h
    allocation_path=ROOT/'results/compressed_batch_compact_cosim_allocations_20261025_v1.json'
    require(digest(allocation_path)==plan['allocation_sha256'],'Allocation proof changed')
    allocation=json.loads(allocation_path.read_text());inventory=json.loads((ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json').read_text());ports={p['name']:p for p in inventory['ports']}
    expected={ports[g['regions'][0]['name']]['bundle']:[r for r in g['regions'] if r['readonly']] for g in allocation['allocations'] if any(r['readonly'] for r in g['regions'])}
    require({m['bundle']:m['readonly'] for m in plan['models']}==expected,'Read-only protection coverage differs from allocation proof')
    directory=out/'sim/verilog';original=Path(setup['project'])/'solution/sim/verilog'
    guarded={m['bundle']:m for m in plan['models']}
    for p in original.iterdir():
        if not p.is_file() or p.suffix not in ['.v','.dat']:continue
        target=directory/p.name
        if p.name.startswith('AESL_axi_master_'):
            bundle=p.stem.removeprefix('AESL_axi_master_')
            if bundle in guarded:
                record=guarded[bundle];require(digest(p)==record['original_sha256'] and digest(target)==record['guarded_sha256'],'Guard model changed')
                text=target.read_text();marker='\n// Independent conservative read-only AXI burst guard.\n'
                require(text.count(marker)==1 and text.split(marker)[0]+'endmodule'+text.rsplit('endmodule',1)[1]==p.read_text(),'Model modification beyond appended guard')
            else:require(digest(target)==digest(p),'Unapproved model modification')
        else:require(digest(target)==digest(p),'DUT RTL differs from reviewed synthesis')
        bind(target)
    pc=out/'sim/wrapc_pc/cosim.pc.exe';require(digest(pc)==digest(Path(setup['project'])/'solution/sim/wrapc_pc/cosim.pc.exe'),'Different original C postcheck executable');bind(pc)
    guard_path=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json';guard=json.loads(guard_path.read_text())
    require(guard['cases']==9,'Missing guard execution evidence')
    for p,h in guard['files'].items():require(digest(p)==h,'Changed isolated guard test input');files[p]=h
    for record in guard['records']:
        p=BASE/'compressed_axi_guard_tests_v2'/(record['name']+'.log');require(digest(p)==record['log_sha256'],'Changed guard execution log');bind(p)
    for stage,base in [('elaborate',parent),('rtl',out),('postcheck',out)]:
        receipt=json.loads((base/(stage+'.receipt.json')).read_text());log=base/(stage+'.log');text=log.read_text(errors='replace')
        require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Failed/changed execution receipt')
        if stage!='elaborate':
            job=next(j for j in expected_jobs if j['phase']==stage)
            require(receipt['command']==job['command'] and receipt['cwd']==job['cwd'] and receipt['resource_abort'] is False,'Different or aborted recovery phase')
        require(not any(s in text for s in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','Simulator command interrupted','engine not responding','unexpected manner','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST']),'Execution failure present')
        if stage=='rtl':require(re.search(r'RTL Simulation :\s*4 / 4',text) is not None,'Incomplete four RTL transactions')
        if stage=='postcheck':require('SEARCH_BATCH_PASS mode=1' in text and 'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=1 ports=44 transactions=4' in text,'Missing original C oracle')
        bind(log);bind(base/(stage+'.receipt.json'))
    performance=directory/'search_batch_trace_top_v2.performance.result.transaction.xml'
    rows=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',performance.read_text(),re.M)]
    require([i for i,_ in rows]==list(range(4)) and all(c>0 for _,c in rows),'Missing/invalid actual transaction cycles');bind(performance)
    snapshots=[]
    for i in range(4):
        actual=out/f'rtl_1_{i}.bin';reference=BASE/f'compressed_batch_compact_cosim_setup/hls_1_{i}.bin'
        require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==digest(reference),'Full44 post-RTL payload differs')
        bind(actual);bind(reference);snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=files[str(actual)]))
    for p in (out/'sim/tv/rtldatafile').glob('*'):
        if p.is_file():bind(p)
    for p in [out/'actual_runtime_limits.json',parent/'plan.json',out/'plan.json',out/'state.json',parent/'state.json',out/'bounded.tcl',allocation_path,guard_path,setup_path,Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py']:bind(p)
    return dict(status='compact_native_stack256_full4tx_full44_rtl_and_original_postcheck_verified',cycles=[c for _,c in rows],snapshots=snapshots,readonly_bundles=sorted(expected),files=files,rtl_verified=True,physical_timing_verified=False,board_verified=False,limits=['Four synthetic compact transactions with full declared pointer capacities; not complete real workload or platform execution','Read-only guard is conservative AW burst overlap rejection; WSTRB does not exempt overlapping requests','Trace guard separately executed with nine cases; other bundle guards use the same generated logic with verified allocation ranges','No platform utilization, timing closure, device bandwidth, power, or speedup claim'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'Refuse overwrite');r=audit()
    fd,tmp=tempfile.mkstemp(dir=a.output.parent)
    with os.fdopen(fd,'w') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,a.output);print(r['status'])
if __name__=='__main__':main()
