#!/usr/bin/env python3
"""Independently audit full30 snapshot RTL, original C contract and every output word."""
import argparse,json,os,re,shlex
from pathlib import Path
from check_vitis_kernel import digest,require
from snapshot_read_serial_prerequisites_v1 import validate_snapshot as validate_paired_predecessors, TREE
from resident_snapshot_rtl_contract import golden,transactions
from snapshot_dpi_output_oracle_v1 import verify
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
from run_snapshot_dpi_rtl_v5 import READONLY,monitor
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def audit(bundle,output):
    require(not output.exists(),'Refuse overwrite')
    paired_bindings=validate_paired_predecessors()
    state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='full30_snapshot_dpi_rtl_c_and_complete_output_oracles_pending_independent_audit','Actual full30 snapshot execution incomplete')
    plan=json.loads((bundle/'plan.json').read_text())
    require(plan['transactions']==30 and plan['pointers']==13 and plan['simulation_bound_ns']==10000000000 and plan['core_dump_limit_bytes']==0 and plan['per_process_address_space_limit_bytes']==64*1024**3,'Different snapshot scope/resources')
    require(plan['resource_policy']==POLICY and plan['free_memory_gate_removed_by_user'] and plan['original_address_environment_unchanged'],'Different resource/address environment')
    files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed frozen execution input '+p)
    require(plan['paired_graph_modes_verified']==[0,1],'Wrong serialized predecessor scope')
    files.update(paired_bindings)
    original=Path(plan['original_sim']);directory=bundle/'sim/verilog';pc=bundle/'sim/wrapc_pc'
    preflight=ROOT/'data/derived/snapshot_dpi_models_preflight_20261025_v1';conversion=json.loads((preflight/'plan.json').read_text())
    require(conversion['transactions']==30 and conversion['pointers']==13 and len(plan['models'])==len(conversion['models'])==10,'Wrong model matrix')
    require({m['bundle'] for m in plan['models']}==READONLY|{'packet_mem','result_mem'},'Different output/RO bundles')
    for model in plan['models']:
        reference=next(m for m in conversion['models'] if m['bundle']==model['bundle'])
        require(model['readonly_monitor']==(model['bundle'] in READONLY),'Incorrect RO monitor coverage')
        require(digest(original/'verilog'/Path(model['path']).name)==reference['before_sha256'],'Original model changed')
        text=Path(reference['path']).read_text();require(digest(reference['path'])==reference['after_sha256'],'Converted storage model changed')
        if model['readonly_monitor']:text=text.replace('endmodule',monitor(model['bundle'])+'endmodule')
        target=directory/Path(model['path']).name
        require(Path(model['path'])==target and target.read_text()==text and digest(target)==model['monitored_sha256'],'Unapproved model/monitor modification')
    for pattern in ['*.v','*.sv','*.dat']:
        require({p.name for p in directory.glob(pattern)}=={p.name for p in (original/'verilog').glob(pattern)},'Different full RTL/ROM file set')
        for p in (original/'verilog').glob(pattern):
            q=directory/p.name
            if not p.name.startswith('AESL_axi_master_'):require(digest(q)==digest(p),'Modified DUT/ROM')
            files[str(q)]=digest(q)
    require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 30;', (directory/'search_resident_snapshot_top.autotb.v').read_text()),'Different actual transaction count')
    commands=[shlex.split(s) for s in (directory/'run_xsim.sh').read_text().splitlines() if s.strip() and not s.startswith('#')]
    require(len(commands)==2,'Different original simulator flow')
    prefix=['prlimit','--stack=67108864:67108864','--core=0:0','--as=68719476736:68719476736','--','taskset','-c','120']
    jobs=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14','--mt','off',str(ROOT/'hardware/sim/axi_dpi_memory_v1.cpp')],directory),('elaborate',prefix+['/usr/bin/time','-v']+commands[0]+['-mt','off','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),('rtl',prefix+commands[1][:-1]+[str(bundle/'bounded.tcl')],directory),('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
    require(plan['commands']==[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],'Different execution commands')
    for phase,command,cwd in jobs:
        receipt=bundle/(phase+'.receipt.json');log=bundle/(phase+'.log');r=json.loads(receipt.read_text());text=log.read_text(errors='replace')
        require(r['exit_code']==0 and r['resource_admission_abort'] is False and r['command']==command and r['cwd']==str(cwd) and r['log_sha256']==digest(log) and r['plan_sha256']==digest(bundle/'plan.json'),'Failed/different phase '+phase)
        require(not any(x in text for x in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','SNAPSHOT_RO_WRITE']),'Execution failure '+phase)
        require(r['resource_policy']==POLICY and r['resource_abort_observation'] is None and abort_reason(plan['startup_memory'],r['end_memory']) is None,'Different phase policy or new OOM')
        actual_path=bundle/(phase+'.actual_limits.json')
        if phase in ['elaborate','rtl']:require(actual_path.is_file(),'Missing actual compiler/kernel limits')
        if actual_path.exists():
            actual=json.loads(actual_path.read_text())
            require(actual['address_space']==[64*1024**3]*2 and actual['stack']==[64*1024**2]*2 and actual['core']==[0,0] and actual['cpu']==[120] and actual['cwd']==str(cwd),'Actual limits/cwd differ')
            require(Path(actual['command'].split()[0]).name=={'xsc':'xsc','elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase],'Wrong actual phase process')
            files[str(actual_path)]=digest(actual_path)
        if phase=='xsc':require('Turned off multi-threading.' in text,'Wrong XSC thread policy')
        if phase=='rtl':
            allocated=re.findall(r'A_DPI_REGISTER id=(\d+) name=(\S+) bits=(\d+) depth=(\d+) pages=(\d+)',text)
            dimensions={};expected_dimensions={m['bundle']:(m['width_bits'],m['declared_depth'],m['pages']) for m in conversion['models']}
            for ident,name,width,depth,pages in allocated:
                match=re.search(r'\.AESL_AXI_MASTER_(\w+)\.',name)
                require(match is not None and match[1] not in dimensions,'Unknown/repeated model allocation')
                dimensions[match[1]]=(int(width),int(depth),int(pages))
            require(len(allocated)==10 and sorted(int(r[0]) for r in allocated)==list(range(10)) and dimensions==expected_dimensions and all(v[2]==4 for v in dimensions.values()),'Incomplete actual full-depth four-page allocation')
        if phase=='postcheck':golden(text)
        if phase=='rtl':require(text.splitlines().count('SNAPSHOT_DPI_BOUNDED_RETURNED')==1 and re.search(r'RTL Simulation :\s*30 / 30',text),'Incomplete30 RTL transactions')
        for p in [receipt,log]:files[str(p)]=digest(p)
    performance=directory/'search_resident_snapshot_top.performance.result.transaction.xml';cycles=transactions(performance.read_text());require(cycles==state['cycles'],'Changed observed transaction cycles')
    outputs=verify(original,bundle/'sim')
    for p in [*outputs,performance,bundle/'plan.json',bundle/'state.json',directory/'xsim.dir/work/xsc/dpi.so',Path(__file__).resolve(),ROOT/'scripts/resident_snapshot_rtl_contract.py',ROOT/'scripts/snapshot_dpi_output_oracle_v1.py',ROOT/'scripts/run_snapshot_dpi_rtl_v5.py',ROOT/'scripts/check_vitis_kernel.py']:files[str(p)]=digest(p)
    result=dict(status='full30_snapshot_dpi_rtl_original_c_and_every_complete_output_word_independently_verified',transactions=30,pointers=13,models=10,pages=4,readonly_models=8,output_files=2,resource_policy=POLICY,original_address_environment_unchanged=True,cycles=cycles,files=files,rtl_verified=True,
                limits=['Full declared-capacity synthetic snapshot contract only, not complete real routing workload or board timing/bandwidth',
                        'All original30 transactions retained; no comparison with unavailable native snapshot RTL cycle baseline'])
    temporary=output.with_suffix('.json.tmp')
    with temporary.open('x') as f:json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,output);print(result['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
