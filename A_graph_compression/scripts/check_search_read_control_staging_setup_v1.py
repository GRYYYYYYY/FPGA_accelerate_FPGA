#!/usr/bin/env python3
"""Verify full-depth candidate setup against the original complete C vectors."""
import json,re
from pathlib import Path
from check_vitis_kernel import digest,require
from search_packet_width_rtl import golden
from run_compact_native_stack_recovery_v1 import atomic
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    bundle=BASE/'search_read_control_staging_cosim_setup_v1';state=json.loads((bundle/'state.json').read_text());require(state['status']=='complete' and state['stage']=='full_depth_cosim_setup_verified_rtl_not_executed','Setup incomplete')
    plan=json.loads((bundle/'execution_plan.json').read_text());require(plan['transactions']==2 and plan['depths_unchanged'] and plan['rtl_executed'] is False,'Wrong scope')
    files=dict(plan['files'])
    for p,h in files.items():require(digest(p)==h,'Changed setup input '+p)
    log=bundle/'setup.log';r=json.loads((bundle/'setup.receipt.json').read_text());require(r['exit_code']==0 and r['log_sha256']==digest(log),'Failed setup receipt')
    text=log.read_text();before,after=text.split('Running: cosim_design',1);golden(before);golden(after);require(text.splitlines().count('READ_CONTROL_RTL_SETUP_COMPLETE')==1,'Missing setup completion')
    project=BASE/'search_read_control_staging_cosim_project_v1';original=ROOT/'build/search_packet_width64_rtl_20261025_v1/solution/sim';directory=project/'solution/sim/verilog';tv=project/'solution/sim/tv/cdatafile'
    actual={p.name:p for p in tv.glob('*.dat')};expected={p.name:p for p in (original/'tv/cdatafile').glob('*.dat')};require(actual.keys()==expected.keys(),'Different full C-vector file set')
    for name,p in actual.items():require(digest(p)==digest(expected[name]),'Full C-vector differs '+name);files[str(p)]=digest(p);files[str(expected[name])]=digest(expected[name])
    models=[]
    old_models={p.name:p for p in (original/'verilog').glob('AESL_axi_master_*.v')};new_models={p.name:p for p in directory.glob('AESL_axi_master_*.v')};require(old_models.keys()==new_models.keys() and len(new_models)==7,'Wrong model set')
    for name,p in new_models.items():
        bundle_name=p.stem.removeprefix('AESL_axi_master_');params=[]
        for source in [old_models[name],p]:
            t=source.read_text();values=[]
            for key in [bundle_name+'_DATA_BITWIDTH',bundle_name+'_mem_depth','mem_page_num']:
                m=re.search(r'parameter\s+'+re.escape(key)+r"\s*=\s*32'd\s*(\d+)",t);require(m is not None,'Missing model dimension');values.append(int(m[1]))
            params.append(values)
        require(params[0]==params[1] and params[1][2]==4,'Changed depth/width/pages');models.append(dict(bundle=bundle_name,bits=params[1][0],depth=params[1][1],pages=4));files[str(p)]=digest(p);files[str(old_models[name])]=digest(old_models[name])
    for p in [bundle/'state.json',bundle/'plan.json',bundle/'execution_plan.json',bundle/'setup.receipt.json',log,Path(__file__).resolve(),ROOT/'scripts/search_packet_width_rtl.py',ROOT/'scripts/check_vitis_kernel.py']:files[str(p)]=digest(p)
    output=ROOT/'results/search_read_control_staging_full_depth_setup_audit_20261025_v1.json';require(not output.exists(),'Refuse overwrite');atomic(output,dict(status='control_staging_full2tx_full_workspace_setup_all_c_vectors_byte_equal_original_model_dimensions_verified_rtl_pending',files=files,c_vector_files=len(actual),models=models,transactions=2,rtl_executed=False,limits=['Setup only; no candidate xelab/RTL/postcheck yet','Internal helper changes cycle counts; no original-cycle parity claimed']))
    print('Full C-vector files byte equal:',len(actual),'models:',len(models),'transactions:2')
if __name__=='__main__':main()
