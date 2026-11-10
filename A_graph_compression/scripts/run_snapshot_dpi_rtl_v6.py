#!/usr/bin/env python3
"""Execute the full30-transaction snapshot DUT with reviewed storage and original C checks."""
import json,os,re,shlex,shutil,signal,subprocess,time
from pathlib import Path
from check_vitis_kernel import digest,require
from snapshot_read_serial_prerequisites_v2 import validate_snapshot as validate_paired_predecessors, TREE
from supervise_search_axi_dpi_v3 import atomic
from resident_snapshot_rtl_contract import golden,transactions
from run_full_scope_phase_v1 import run_phase
from snapshot_dpi_output_oracle_v1 import verify
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
READONLY={'control_mem','static_mem','meta_mem','count_mem','node_history_mem','node_table_mem','site_table_mem','site_history_mem'}
def monitor(bundle):
    prefix='TRAN_'+bundle
    return '\n// Independent snapshot read-only AXI monitor.\nalways @(posedge clk) begin\n  if ('+prefix+"_AWVALID === 1'b1 && "+prefix+"_AWREADY === 1'b1) $fatal(1,\"SNAPSHOT_RO_WRITE "+bundle+'\");\nend\n'
def main():
    def interrupted(signum, frame):
        raise SystemExit(128 + signum)
    signal.signal(signal.SIGTERM, interrupted)
    paired_bindings=validate_paired_predecessors()
    gate=ROOT/'results'/TREE
    initial_memory=observe()
    audit_path=ROOT/'results/snapshot_dpi_storage_preflight_audit_20261025_v1.json';audit=json.loads(audit_path.read_text())
    preflight=ROOT/'data/derived/snapshot_dpi_models_preflight_20261025_v1';conversion=json.loads((preflight/'plan.json').read_text())
    require(conversion['transactions']==30 and conversion['pointers']==13 and len(conversion['models'])==10,'Different snapshot scope')
    files={str(p):digest(p) for p in [gate,audit_path,preflight/'plan.json',Path(__file__).resolve(),ROOT/'scripts/resident_snapshot_rtl_contract.py',ROOT/'scripts/snapshot_dpi_output_oracle_v1.py']}
    files.update(paired_bindings)
    for name in ['run_full_scope_phase_v1.py','owned_sim_resource_policy_v1.py','snapshot_read_serial_prerequisites_v2.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    for review in [audit]:
        for p,h in review['files'].items():require(digest(p)==h,'Changed accepted prerequisite '+p);files[p]=h
    parent=BASE/'snapshot_rtl_local_recovery';old=json.loads((parent/'plan.json').read_text());source=Path(old['project'])/'solution/sim'
    out=BASE/'snapshot_dpi_rtl_v6';out.mkdir(exist_ok=False);state=dict(owner_pid=os.getpid(),status='running',stage='copy_original_full30_setup');atomic(out/'state.json',state)
    try:
        dst=out/'sim';shutil.copytree(source,dst,ignore=lambda d,n:[x for x in n if x in ['xsim.dir','.Xil','rtldatafile'] or x.endswith(('.log','.pb','.jou')) or 'performance.result' in x or x.startswith('core.')])
        (dst/'tv/rtldatafile').mkdir(exist_ok=True)
        for p,h in old['copied'].items():
            a=Path(p);b=dst/a.relative_to(source)
            if 'rtldatafile' in a.parts or 'performance.result' in a.name or a.suffix in ['.log','.pb','.jou']:continue
            require(digest(b)==h,'Copied original fixture/RTL/C postcheck differs');files[str(b)]=h
        directory=dst/'verilog';models=[]
        require({m['bundle'] for m in conversion['models']}==READONLY|{'packet_mem','result_mem'},'Different RO model matrix')
        for m in conversion['models']:
            p=directory/Path(m['path']).name;require(digest(p)==m['before_sha256'],'Changed original model')
            text=Path(m['path']).read_text();require(digest(m['path'])==m['after_sha256'] and text.count('endmodule')==1,'Changed converted model')
            if m['bundle'] in READONLY:text=text.replace('endmodule',monitor(m['bundle'])+'endmodule')
            p.write_text(text);files[str(p)]=digest(p);models.append({**m,'path':str(p),'monitored_sha256':digest(p),'readonly_monitor':m['bundle'] in READONLY})
        for pattern in ['*.v','*.sv','*.dat']:
            require({p.name for p in directory.glob(pattern)}=={p.name for p in (source/'verilog').glob(pattern)},'Changed full RTL/ROM matrix')
            for p in (source/'verilog').glob(pattern):
                if not p.name.startswith('AESL_axi_master_'):require(digest(p)==digest(directory/p.name),'Changed DUT or ROM')
        commands=[shlex.split(s) for s in (directory/'run_xsim.sh').read_text().splitlines() if s.strip() and not s.startswith('#')];require(len(commands)==2,'Unknown original flow')
        bounded=out/'bounded.tcl';bounded.write_text('run 10 sec\nputs SNAPSHOT_DPI_BOUNDED_RETURNED\nquit\n');files[str(bounded)]=digest(bounded)
        cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp';files[str(cpp)]=digest(cpp)
        prefix=['prlimit','--stack=67108864:67108864','--core=0:0','--as=68719476736:68719476736','--','taskset','-c','120'];pc=dst/'wrapc_pc'
        jobs=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14','--mt','off',str(cpp)],directory),('elaborate',prefix+['/usr/bin/time','-v']+commands[0]+['-mt','off','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),('rtl',prefix+commands[1][:-1]+[str(bounded)],directory),('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
        plan=dict(files=files,models=models,paired_graph_modes_verified=[0,1],transactions=30,pointers=13,original_sim=str(source),commands=[dict(phase=n,command=c,cwd=str(d)) for n,c,d in jobs],simulation_bound_ns=10000000000,per_process_address_space_limit_bytes=64*1024**3,core_dump_limit_bytes=0,compiler_optimization='Original generated default; no --O0 override',resource_policy=POLICY,startup_memory=initial_memory,free_memory_gate_removed_by_user=True,original_address_environment_unchanged=True)
        atomic(out/'plan.json',plan);env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'}
        for phase,command,cwd in jobs:
            text=run_phase(out,phase,command,cwd,state,initial_memory,env,120)
            require(not any(x in text for x in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:','SNAPSHOT_RO_WRITE']),'Full snapshot phase failed '+phase)
            if phase=='rtl':require('SNAPSHOT_DPI_BOUNDED_RETURNED' in text and re.search(r'RTL Simulation :\s*30 / 30',text),'Incomplete30 RTL transactions')
            if phase=='postcheck':golden(text)
        cycles=transactions((directory/'search_resident_snapshot_top.performance.result.transaction.xml').read_text());verify(source,dst)
        for p,h in files.items():require(digest(p)==h,'Frozen input changed')
        state.update(status='complete',stage='full30_snapshot_dpi_rtl_c_and_complete_output_oracles_pending_independent_audit',cycles=cycles);atomic(out/'state.json',state)
    except BaseException as e:state.update(status='failed',error=str(e));atomic(out/'state.json',state);raise
if __name__=='__main__':main()
