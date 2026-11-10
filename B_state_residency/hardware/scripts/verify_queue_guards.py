"""Mutation checks: intentionally remove one drain guard from isolated RTL copies.

Expected behavioral failures are evidence that the boundary tests distinguish
unsafe recycling. This never changes production RTL or calls a failure PASS.
"""
from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    out=Path(sys.argv[1]).resolve();out.mkdir()
    wrapper=ROOT/'hardware/rtl/queued_scratch_endpoint.sv';tb=ROOT/'hardware/tb/tb_queued_scratch_endpoint.sv'
    base=[ROOT/'hardware/rtl'/name for name in ('bounded_sync_fifo.sv','scratch_frame_store_bram.sv','scratch_page_controller.sv')]
    src=wrapper.read_text()
    mutations={
        'ignore_old_responses':('&& response_count==0','', 'retired with old response buffered'),
        'ignore_duplicate_acks':('&& fence_ack_count==0','', 'response mismatch'),
        'ignore_queued_work':('&& work_count==1','', 'response mismatch'),
        'ignore_same_cycle_ingress':('&& fence_request_count==0 && fence_ack_count==0 && !(cmd_valid && cmd_ready);','&& fence_request_count==0 && fence_ack_count==0;', 'response mismatch'),
        'seal_with_live_lease':('&& request_count==0 && work_count==0 && leases==0','&& request_count==0 && work_count==0', 'peer sealed with outstanding lease'),
    }
    inputs=base+[wrapper,tb,Path(__file__).resolve()]
    record=dict(status='running',files={str(p):sha(p) for p in inputs},mutations={})
    def save():(out/'manifest.json').write_text(json.dumps(record,indent=2)+'\n')
    save()
    try:
        for name,(old,new,expected) in mutations.items():
            if src.count(old)!=1:raise ValueError('Ambiguous mutation '+name)
            d=out/name;d.mkdir();mutant=d/'queued_scratch_endpoint.sv';mutant.write_text(src.replace(old,new))
            (d/'simulate.tcl').write_text('run 1001ms\nquit\n')
            row=dict(status='running',removed=old,replacement=new,expected_failure=expected,commands=[]);record['mutations'][name]=row;save()
            commands=[('compile',[BIN/'xvlog','--sv','--work','xil_defaultlib',*base,mutant,tb]),
                      ('elaborate',[BIN/'xelab','xil_defaultlib.tb_queued_small','--snapshot','guard_tb','--debug','typical','--mt','2']),
                      ('simulate',[BIN/'xsim','guard_tb','--tclbatch','simulate.tcl','--log','simulate.log'])]
            for stage,cmd in commands:
                with (d/(stage+'.console.log')).open('w') as log:r=subprocess.run(cmd,cwd=d,stdout=log,stderr=subprocess.STDOUT)
                row['commands'].append(dict(stage=stage,argv=list(map(str,cmd)),exit_code=r.returncode));save()
                if stage!='simulate' and r.returncode:raise RuntimeError('Mutation did not compile '+name)
            log=(d/'simulate.log').read_text()
            failures=[line for line in log.splitlines() if line.startswith('Fatal:')]
            if 'TEST_PASS' in log or len(failures)!=1 or expected not in failures[0]:raise ValueError('Wrong/missing behavioral rejection '+name)
            row.update(status='expected_failure_observed',causal_failure=failures[0],artifacts={str(p):sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.sv','.tcl','.log')});save()
            print(name+': '+failures[0],flush=True)
        for p,digest in record['files'].items():
            if sha(p)!=digest:raise ValueError('Source changed during negative tests')
        record['status']='passed';save()
    except Exception as e:record.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
