#!/usr/bin/env python3
"""Wait for the unique elaboration, then run bounded RTL and original C oracle."""
import json,os,subprocess,time
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
    out=BASE/'compressed_batch_rtl_guarded_execution_v1';out.mkdir(exist_ok=False)
    state=dict(owner_pid=os.getpid(),status='running',stage='waiting_existing_elaboration')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        parent=BASE/'compressed_batch_rtl_guarded_v1'
        while True:
            current=json.loads((parent/'state.json').read_text())
            if current['status']!='running':break
            pid=current['owner_pid']
            assert Path('/proc',str(pid)).exists(),'Elaboration owner missing without terminal receipt'
            assert b'run_compressed_batch_rtl_guarded.py' in Path('/proc',str(pid),'cmdline').read_bytes(),'Owner PID reused'
            time.sleep(30)
        assert current['status']=='prepared',current
        guard=ROOT/'results/compressed_axi_ro_guard_tests_20261025_v1.json'
        assert guard.exists(),'Guard negative/positive execution gate missing'
        review=json.loads(guard.read_text());assert review['cases']==9
        for p,h in review['files'].items():assert digest(p)==h,p
        receipt=json.loads((parent/'elaborate.receipt.json').read_text());assert receipt['exit_code']==0
        assert receipt['log_sha256']==digest(parent/'elaborate.log')
        plan=json.loads((parent/'plan.json').read_text())
        directory=parent/'sim/verilog';pc=parent/'sim/wrapc_pc'
        for model in plan['models']:assert digest(directory/('AESL_axi_master_'+model['bundle']+'.v'))==model['guarded_sha256']
        # Four synthetic transactions need far less than 10 simulated seconds;
        # completion still requires the generated 4-transaction performance XML.
        tcl=out/'bounded.tcl';tcl.write_text('run 10 sec\nquit\n')
        jobs=[('rtl',[str(BIN/'xsim'),'--noieeewarnings','search_batch_trace_top_v2','-tclbatch',str(tcl)],directory),('postcheck',[str(pc/'cosim.pc.exe')],pc)]
        execution=dict(elaboration_plan_sha256=digest(parent/'plan.json'),guard_gate_sha256=digest(guard),commands=[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],script_sha256=digest(__file__))
        (out/'plan.json').write_text(json.dumps(execution,indent=2)+'\n')
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_BATCH_RTL_SNAPSHOT_PREFIX':str(out/'rtl')}
        for phase,command,cwd in jobs:
            state['stage']=phase;save();start=time.monotonic()
            with (out/(phase+'.log')).open('x') as f:
                child=subprocess.Popen(command,cwd=cwd,env=env,stdout=f,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
            text=(out/(phase+'.log')).read_text(errors='replace')
            (out/(phase+'.receipt.json')).write_text(json.dumps(dict(exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/(phase+'.log'))),indent=2)+'\n')
            assert code==0 and not any(x in text for x in ['ERROR:','FATAL_ERROR','A_RO_WRITE_VIOLATION','A_RO_UNKNOWN_ADDRESS','A_RO_UNSUPPORTED_BURST']),phase+' failed'
            if phase=='postcheck':
                assert 'SEARCH_BATCH_PASS mode=0' in text and 'FULL_DEPTH_BATCH_PORT_SNAPSHOTS mode=0 ports=44 transactions=4' in text
        snapshots=[]
        for i in range(4):
            actual=out/f'rtl_0_{i}.bin';expected=BASE/f'compressed_batch_cosim_setup/hls_0_{i}.bin'
            assert actual.stat().st_size==expected.stat().st_size and digest(actual)==digest(expected),(i,'full snapshot differs')
            snapshots.append(dict(transaction=i,bytes=actual.stat().st_size,sha256=digest(actual)))
        xml=directory/'search_batch_trace_top_v2.performance.result.transaction.xml';assert xml.exists(),'Missing transaction completion evidence'
        report=dict(status='rtl_and_original_postcheck_completed_four_full44_snapshots_equal_independent_transaction_audit_pending',snapshots=snapshots,files={str(p):digest(p) for p in [xml,out/'plan.json',out/'rtl.log',out/'postcheck.log',guard]},limits=['CSR four synthetic transactions at declared capacity; not production real-batch RTL or board performance','Independent transaction XML and complete final audit still required'])
        (out/'review_pending.json').write_text(json.dumps(report,indent=2)+'\n')
        state.update(status='complete',stage='independent_final_audit_pending');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
