#!/usr/bin/env python3
"""Independently accept full-depth DPI replay only against the original RTL."""
import argparse
import json
import os
import re
import shlex
import subprocess
import sys
from pathlib import Path
from owned_sim_resource_policy_v1 import POLICY,observe,abort_reason
from check_vitis_kernel import digest, require
from check_search_packet_width_rtl import cycles
from search_packet_width_rtl import golden

ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def audit(bundle,output):
    require(not output.exists(),'Refuse overwrite')
    state=json.loads((bundle/'state.json').read_text())
    require(state['status']=='complete' and state['stage']=='candidate_full_rtl_outputs_and_original_c_oracle_equal_pending_independent_audit','Actual full replay incomplete')
    plan=json.loads((bundle/'plan.json').read_text())
    require(plan['resource_policy']==POLICY and plan['free_memory_gate_removed_by_user'] and plan['original_address_environment_unchanged'],'Different resource/address environment')
    require(plan['per_process_address_space_limit_bytes']==64*1024**3 and plan['core_dump_limit_bytes']==0,'Missing enforced address-space limit')
    require(plan['transactions']==2 and plan['depths_unchanged'] and plan['pages_unchanged'] and plan['dut_unchanged'] and plan['simulation_bound_ns']==10000000000,'Scope differs')
    reference=ROOT/'build/search_packet_width64_rtl_20261025_v1/solution/sim'
    original=Path('/tmp/A_graph_compression_recovery_20261025_v1/search_read_control_staging_cosim_project_v1/solution/sim')
    require(Path(plan['original_sim'])==original and Path(plan['baseline_reference_sim'])==reference and plan['candidate_dut_differs_from_baseline'] is True,'Wrong candidate or baseline simulation')
    from snapshot_read_serial_prerequisites_v2 import validate_read
    validate_read(ROOT)
    candidate_gate=ROOT/'results/search_read_control_staging_full_depth_setup_audit_20261025_v1.json'
    candidate=json.loads(candidate_gate.read_text())
    require(candidate['transactions']==2 and len(candidate['models'])==7 and candidate['rtl_executed'] is False,'Missing full candidate setup proof')
    for p,h in candidate['files'].items():require(digest(p)==h,'Changed candidate setup evidence')
    baseline_path=ROOT/'results/search_packet_width64_rtl_audit_20261025_v1.json'
    baseline=json.loads(baseline_path.read_text())
    require(baseline['rtl_verified'] and baseline['cycles']==[2132461,12404],'Original RTL oracle missing')
    files={**baseline['files'],**plan['files']}
    for p,h in files.items():require(digest(p)==h,'Changed input/reference '+p)
    directory=bundle/'sim/verilog';pc=bundle/'sim/wrapc_pc'
    original_models={p.name for p in (original/'verilog').glob('AESL_axi_master_*.v')}
    require(len(plan['models'])==7 and {Path(m['path']).name for m in plan['models']}==original_models,'Wrong model matrix')
    ledger_audit=bundle/'independent_storage_edits.json'
    if not ledger_audit.exists():
        subprocess.run([sys.executable,str(ROOT/'scripts/check_axi_dpi_storage_edits_v1.py'),'--bundle',str(bundle),'--output',str(ledger_audit)],check=True)
    edits=json.loads(ledger_audit.read_text())
    require(edits['files'][str(bundle/'plan.json')]==digest(bundle/'plan.json'),'Stale storage audit')
    require(len(edits['models'])==7,'Incomplete storage edit audit')
    for p,h in edits['files'].items():require(digest(p)==h,'Changed storage audit input');files[p]=h
    for pattern in ['*.v','*.sv','*.dat']:
        original_set={p.name for p in (original/'verilog').glob(pattern)}
        require({p.name for p in directory.glob(pattern)}==original_set,'Different complete RTL/ROM file set')
        for name in original_set-original_models:
            a=original/'verilog'/name;b=directory/name
            require(digest(a)==digest(b),'Changed simulated DUT/ROM '+name);files[str(a)]=digest(a);files[str(b)]=digest(b)
    require(re.search(r'parameter AUTOTB_TRANSACTION_NUM = 2;', (directory/'search_kernel_top.autotb.v').read_text()),'Wrong transaction count')
    generated=[shlex.split(line) for line in (directory/'run_xsim.sh').read_text().splitlines() if line.strip() and not line.startswith('#')]
    require(len(generated)==2,'Unexpected generated simulator flow')
    prefix=['prlimit','--stack=67108864:67108864','--core=0:0','--as=68719476736:68719476736','--','taskset','-c','125']
    expected=[('xsc',prefix+[str(BIN/'xsc'),'--cppversion','14','--mt','off',str(ROOT/'hardware/sim/axi_dpi_memory_v1.cpp')],directory),
              ('elaborate',prefix+['/usr/bin/time','-v']+generated[0]+['-mt','off','--O0','--stats','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc'],directory),
              ('rtl',prefix+generated[1][:-1]+[str(bundle/'bounded.tcl')],directory),
              ('postcheck',prefix+[str(pc/'cosim.pc.exe')],pc)]
    require(plan['commands']==[dict(phase=n,command=c,cwd=str(d)) for n,c,d in expected],'Different commands')
    for phase,command,cwd in expected:
        receipt=bundle/(phase+'.receipt.json');log=bundle/(phase+'.log')
        r=json.loads(receipt.read_text());text=log.read_text(errors='replace')
        require(r['exit_code']==0 and r['resource_admission_abort'] is False and r['command']==command and r['cwd']==str(cwd) and r['log_sha256']==digest(log),'Failed or different phase '+phase)
        require(not any(t in text for t in ['ERROR:','Fatal:','FATAL_ERROR','runtime error:']),'Phase errors '+phase)
        require(r['resource_policy']==POLICY and r['resource_abort_observation'] is None and abort_reason(plan['startup_memory'],r['end_memory']) is None and r['plan_sha256']==digest(bundle/'plan.json'),'Different phase policy/OOM/plan')
        actual_path=bundle/(phase+'.actual_limits.json')
        if phase in ['elaborate','rtl']:require(actual_path.is_file(),'Missing actual compiler/kernel limits')
        if actual_path.exists():
            actual=json.loads(actual_path.read_text())
            require(actual['address_space']==[64*1024**3]*2 and actual['stack']==[64*1024**2]*2 and actual['core']==[0,0] and actual['cpu']==[125] and actual['cwd']==str(cwd),'Actual limits/cwd differ')
            require(Path(actual['command'].split()[0]).name=={'xsc':'xsc','elaborate':'xelab','rtl':'xsimk','postcheck':'cosim.pc.exe'}[phase],'Wrong actual phase process')
            files[str(actual_path)]=digest(actual_path)
        if phase=='xsc':require('Turned off multi-threading.' in text,'Wrong XSC thread policy')
        if phase=='rtl':
            allocated=re.findall(r'A_DPI_REGISTER id=(\d+) name=(\S+) bits=(\d+) depth=(\d+) pages=(\d+)',text)
            dimensions={};expected_dimensions={m['bundle']:(m['bits'],m['depth'],m['pages']) for m in candidate['models']}
            for ident,name,width,depth,pages in allocated:
                match=re.search(r'\.AESL_AXI_MASTER_(\w+)\.',name)
                require(match is not None and match[1] not in dimensions,'Unknown/repeated model allocation')
                dimensions[match[1]]=(int(width),int(depth),int(pages))
            require(len(allocated)==7 and sorted(int(r[0]) for r in allocated)==list(range(7)) and dimensions==expected_dimensions and all(v[2]==4 for v in dimensions.values()),'Incomplete actual full-depth four-page allocation')
        if phase=='postcheck':golden(text)
        if phase=='rtl':require(text.splitlines().count('DPI_REPLAY_BOUNDED_RETURNED')==1 and re.search(r'RTL Simulation :\s*2 / 2',text),'No complete RTL replay')
        for p in [receipt,log]:files[str(p)]=digest(p)
    performance=directory/'search_kernel_top.performance.result.transaction.xml'
    actual=cycles(performance.read_text())
    require(actual==state['cycles'] and len(actual)==2 and all(c>0 for c in actual),'Incomplete candidate cycles')
    original_outputs={p.name:p for p in (reference/'tv/rtldatafile').glob('rtl.*.autotvout_*.dat')}
    outputs={p.name:p for p in (bundle/'sim/tv/rtldatafile').glob('rtl.*.autotvout_*.dat')}
    require(original_outputs and outputs.keys()==original_outputs.keys(),'Incomplete complete-output file set')
    for name,p in outputs.items():
        require(digest(p)==digest(original_outputs[name]),'Complete output differs '+name)
        files[str(p)]=digest(p);files[str(original_outputs[name])]=digest(original_outputs[name])
    for p in [bundle/'plan.json',bundle/'state.json',baseline_path,ledger_audit,performance,directory/'xsim.dir/work/xsc/dpi.so',Path(__file__).resolve(),ROOT/'scripts/check_search_packet_width_rtl.py',ROOT/'scripts/search_packet_width_rtl.py',ROOT/'scripts/check_vitis_kernel.py',candidate_gate,ROOT/'scripts/snapshot_read_serial_prerequisites_v2.py']:
        files[str(p)]=digest(p)
    report=dict(status='read_control_staging_full2tx_dpi_rtl_all_output_bytes_and_original_c_oracle_independently_verified',rtl_verified=True,original_cycle_parity_claimed=False,
                cycles=actual,models=7,transactions=2,pointers=13,pages=4,resource_policy=POLICY,original_address_environment_unchanged=True,output_files=len(outputs),files=files,
                limits=['Two synthetic search-core transactions only; no full integrated batch/snapshot/real-workload equivalence inferred',
                        'Changed internal helper pipeline; complete positive candidate cycles recorded without original-cycle parity',
                        'No board throughput, physical timing or bandwidth claim'])
    temporary=output.with_suffix('.json.tmp')
    with temporary.open('x') as f:
        json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,output);print(report['status'])
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();audit(a.bundle.resolve(),a.output.resolve())
