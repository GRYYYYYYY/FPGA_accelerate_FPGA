#!/usr/bin/env python3
"""Accept only actual completed CSR RTL, original postcheck, and full44 equality."""
import argparse,json,os,re,tempfile
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def audit():
    parent=BASE/'compressed_batch_rtl_guarded_v1';out=BASE/'compressed_batch_rtl_guarded_execution_v1'
    state=json.loads((out/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='independent_final_audit_pending','Actual RTL/postcheck execution not complete')
    preparation=json.loads((parent/'state.json').read_text());require(preparation['status']=='prepared','Elaboration incomplete')
    plan=json.loads((parent/'plan.json').read_text());execution=json.loads((out/'plan.json').read_text())
    require(execution['elaboration_plan_sha256']==digest(parent/'plan.json'),'Changed elaboration plan')
    setup_path=BASE/'compressed_batch_cosim_setup/setup.json';setup=json.loads(setup_path.read_text())
    require(digest(setup_path)==plan['setup_sha256'],'Setup changed')
    require(digest(ROOT/'scripts/run_compressed_batch_rtl_guarded.py')==plan['script_sha256'],'Elaboration driver changed')
    require(digest(ROOT/'scripts/supervise_compressed_batch_rtl_guarded.py')==execution['script_sha256'],'Execution driver changed')
    files={}
    def bind(p):files[str(p)]=digest(p)
    for p,h in setup['files'].items():require(digest(p)==h,'Changed prepared input '+p);files[p]=h
    allocation_path=ROOT/'results/compressed_batch_cosim_allocations_20261025_v1.json'
    require(digest(allocation_path)==plan['allocation_sha256'],'Allocation proof changed')
    allocation=json.loads(allocation_path.read_text());inventory=json.loads((ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json').read_text());ports={p['name']:p for p in inventory['ports']}
    expected={ports[g['regions'][0]['name']]['bundle']:[r for r in g['regions'] if r['readonly']] for g in allocation['allocations'] if any(r['readonly'] for r in g['regions'])}
    require({m['bundle']:m['readonly'] for m in plan['models']}==expected,'Read-only protection coverage differs from allocation proof')
    directory=parent/'sim/verilog';original=Path(setup['project'])/'solution/sim/verilog'
    guarded={m['bundle']:m for m in plan['models']}
    for p in original.glob('*.v'):
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
    pc=parent/'sim/wrapc_pc/cosim.pc.exe';require(digest(pc)==digest(Path(setup['project'])/'solution/sim/wrapc_pc/cosim.pc.exe'),'Different original C postcheck executable');bind(pc)
    guard_path=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json';guard=json.loads(guard_path.read_text())
    require(execution['guard_gate_sha256']==digest(guard_path) and guard['cases']==9,'Missing guard execution evidence')
    for p,h in guard['files'].items():require(digest(p)==h,'Changed isolated guard test input');files[p]=h
    for record in guard['records']:
        p=BASE/'compressed_axi_guard_tests_v2'/(record['name']+'.log');require(digest(p)==record['log_sha256'],'Changed guard execution log');bind(p)
    for stage,base in [('elaborate',parent),('rtl',out),('postcheck',out)]:
        receipt=json.loads((base/(stage+'.receipt.json')).read_text());log=base/(stage+'.log');text=log.read_text(errors='replace')
        require(receipt['exit_code']==0 and receipt['log_sha256']==digest(log),'Failed/changed execution receipt')
        require(not any(s in text for s in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST']),'Execution failure present')
        if stage=='rtl':require(re.search(r'RTL Simulation :\s*4 / 4',text) is not None,'Incomplete four RTL transactions')
        if stage=='postcheck':require('SEARCH_BATCH_PASS mode=0' in text and 'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=0 ports=44 transactions=4' in text,'Missing original C oracle')
        bind(log);bind(base/(stage+'.receipt.json'))
    performance=directory/'search_batch_trace_top_v2.performance.result.transaction.xml'
    rows=[tuple(map(int,x)) for x in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',performance.read_text(),re.M)]
    require([i for i,_ in rows]==list(range(4)) and all(c>0 for _,c in rows),'Missing/invalid actual transaction cycles');bind(performance)
    snapshots=[]
    for i in range(4):
        actual=out/f'rtl_0_{i}.bin';reference=BASE/f'compressed_batch_cosim_setup/hls_0_{i}.bin'
        require(actual.stat().st_size==reference.stat().st_size==946498280 and digest(actual)==digest(reference),'Full44 post-RTL payload differs')
        bind(actual);bind(reference);snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=files[str(actual)]))
    for p in (parent/'sim/tv/rtldatafile').glob('*'):
        if p.is_file():bind(p)
    for p in [parent/'plan.json',out/'plan.json',out/'state.json',parent/'state.json',out/'bounded.tcl',allocation_path,guard_path,setup_path,Path(__file__).resolve(),ROOT/'scripts/check_vitis_kernel.py']:bind(p)
    return dict(status='compressed_batch_csr_four_transaction_guarded_rtl_and_original_postcheck_full44_payloads_verified',cycles=[c for _,c in rows],snapshots=snapshots,readonly_bundles=sorted(expected),files=files,rtl_verified=True,physical_timing_verified=False,board_verified=False,limits=['Four synthetic CSR transactions with full declared pointer capacities; not complete real workload or compact RTL','Read-only guard is conservative AW burst overlap rejection; WSTRB does not exempt overlapping requests','Trace guard separately executed with nine cases; other bundle guards use the same generated logic with verified allocation ranges','No platform utilization, timing closure, device bandwidth, power, or speedup claim'])
def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'Refuse overwrite');r=audit()
    fd,tmp=tempfile.mkstemp(dir=a.output.parent)
    with os.fdopen(fd,'w') as f:json.dump(r,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,a.output);print(r['status'])
if __name__=='__main__':main()
