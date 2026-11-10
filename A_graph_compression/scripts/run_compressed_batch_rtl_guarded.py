#!/usr/bin/env python3
"""Execute reviewed HLS setup in isolation with conservative RO burst guards."""
import hashlib,json,os,re,shlex,shutil,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def digest(p):
    h=hashlib.sha256()
    with Path(p).open('rb') as f:
        for chunk in iter(lambda:f.read(8388608),b''):h.update(chunk)
    return h.hexdigest()
def main():
    out=BASE/'compressed_batch_rtl_guarded_v1';out.mkdir(exist_ok=False)
    state=dict(owner_pid=os.getpid(),status='running',stage='verify_inputs')
    def save():
        tmp=out/'state.tmp';tmp.write_text(json.dumps(state,indent=2)+'\n');tmp.replace(out/'state.json')
    save()
    try:
        setup_path=BASE/'compressed_batch_cosim_setup/setup.json';setup=json.loads(setup_path.read_text())
        assert setup['transactions']==4 and setup['rtl_simulated'] is False
        for p,h in setup['files'].items():assert digest(p)==h,p
        allocations_path=ROOT/'results/compressed_batch_cosim_allocations_20261025_v1.json'
        allocations=json.loads(allocations_path.read_text())
        for p,h in allocations['files'].items():assert digest(p)==h,p
        inventory=json.loads((ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json').read_text())
        ports={p['name']:p for p in inventory['ports']}
        src=Path(setup['project'])/'solution/sim';dst=out/'sim'
        state['stage']='copy_setup';save()
        shutil.copytree(src,dst,ignore=lambda d,n:[x for x in n if x in ['xsim.dir','.Xil'] or x.endswith(('.log','.jou','.pb'))])
        models=[]
        for group in allocations['allocations']:
            readonly=[r for r in group['regions'] if r['readonly']]
            if not readonly:continue
            bundle=ports[readonly[0]['name']]['bundle'];model=dst/'verilog'/f'AESL_axi_master_{bundle}.v'
            text=model.read_text();prefix='TRAN_'+bundle
            assert text.count('endmodule')==1
            guard='\n// Independent conservative read-only AXI burst guard.\nreg [64:0] a_ro_first, a_ro_last;\nalways @(posedge clk) begin\n'
            guard+=f'  if ({prefix}_AWVALID === 1\'b1 && {prefix}_AWREADY === 1\'b1) begin\n'
            guard+=f'    if ((^{prefix}_AWADDR === 1\'bx) || (^{prefix}_AWLEN === 1\'bx) || (^{prefix}_AWSIZE === 1\'bx) || (^{prefix}_AWBURST === 1\'bx)) $fatal(1,"A_RO_UNKNOWN_ADDRESS {bundle}");\n'
            guard+=f'    a_ro_first = {{1\'b0,{prefix}_AWADDR}};\n'
            guard+=f'    if ({prefix}_AWBURST == 0) a_ro_last = a_ro_first + (65\'d1 << {prefix}_AWSIZE) - 1;\n'
            guard+=f'    else if ({prefix}_AWBURST == 1) a_ro_last = a_ro_first + (({{57\'d0,{prefix}_AWLEN}} + 1) << {prefix}_AWSIZE) - 1;\n'
            guard+=f'    else $fatal(1,"A_RO_UNSUPPORTED_BURST {bundle}");\n'
            for r in readonly:
                guard+=f'    if (a_ro_first < 65\'d{r["end"]} && a_ro_last >= 65\'d{r["start"]}) $fatal(1,"A_RO_WRITE_VIOLATION {bundle} {r["name"]}");\n'
            guard+='  end\nend\n'
            model.write_text(text.replace('endmodule',guard+'endmodule'))
            models.append(dict(bundle=bundle,original_sha256=digest(src/'verilog'/model.name),guarded_sha256=digest(model),readonly=readonly))
        # All DUT RTL must remain byte-identical to the reviewed setup.
        for p in (src/'verilog').glob('*.v'):
            if p.name.startswith('AESL_axi_master_'):continue
            assert digest(p)==digest(dst/'verilog'/p.name),p
        command=shlex.split((dst/'verilog/run_xsim.sh').read_text().strip().splitlines()[0])
        assert Path(command[0]).name=='xelab'
        command=['/usr/bin/time','-v']+command+['-mt','off','--O0','--stats']
        plan=dict(setup_sha256=digest(setup_path),allocation_sha256=digest(allocations_path),models=models,command=command,cwd=str(dst/'verilog'),script_sha256=digest(__file__),transactions=4,limits=['Conservative guard rejects any AW burst overlapping RO allocation, even if all write strobes are zero','Elaboration alone does not prove guard functionality or RTL behavior'])
        (out/'plan.json').write_text(json.dumps(plan,indent=2)+'\n')
        state['stage']='elaborate';save();start=time.monotonic()
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        with (out/'elaborate.log').open('x') as log:
            child=subprocess.Popen(command,cwd=dst/'verilog',env=env,stdout=log,stderr=subprocess.STDOUT);state['child_pid']=child.pid;save();code=child.wait()
        (out/'elaborate.receipt.json').write_text(json.dumps(dict(exit_code=code,elapsed_seconds=time.monotonic()-start,log_sha256=digest(out/'elaborate.log')),indent=2)+'\n')
        assert code==0,'Elaboration failed; preserve logs'
        state.update(status='prepared',stage='elaborated_rtl_execution_pending');save()
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save();raise
if __name__=='__main__':main()
