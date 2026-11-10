#!/usr/bin/env python3
"""Recheck prepared physical inputs and reject early execution; no Vivado flow."""
import ast
import json
from pathlib import Path
import subprocess
import sys
import time
from check_vitis_kernel import digest,require
from encoded_physical_entry_v2 import validate_bundle
from supervise_search_axi_dpi_v3 import atomic

ROOT=Path(__file__).resolve().parents[1]
BUNDLE=ROOT/'data/derived/encoded_physical_execution_20261029_v2'
OUT=ROOT/'data/derived/encoded_physical_entry_validation_20261029_v2'
RESULT=ROOT/'results/encoded_physical_entry_validation_20261029_v2.json'

def main():
    require(not OUT.exists() and not RESULT.exists(),'Refuse overwrite')
    prep_path=ROOT/'results/encoded_physical_execution_preparation_20261029_v2.json'
    prep=json.loads(prep_path.read_text());files={**prep['files'],str(prep_path):digest(prep_path)}
    for p,h in files.items():require(digest(p)==h,'Changed prepared evidence '+p)
    plan,_=validate_bundle(BUNDLE,'csr')
    def function(path,name):
        return ast.dump(next(n for n in ast.parse(path.read_text()).body if isinstance(n,ast.FunctionDef) and n.name==name))
    old=ROOT/'scripts/check_encoded_physical_execution_v1.py';new=ROOT/'scripts/check_encoded_physical_execution_v2.py'
    require(function(old,'terminal_receipts')==function(new,'terminal_receipts'),'Changed exact terminal MCP acceptance')
    files[str(old)]=digest(old)
    pair_path=ROOT/'results/paired_binary_nonzero_entries_preparation_20261029_v3.json'
    pair=json.loads(pair_path.read_text());files[str(pair_path)]=digest(pair_path)
    sources=[]
    for job in plan['jobs']:
        for name in job['source_names']:
            actual=Path(job['work'])/'source'/name
            if job['name'] in ['csr','compact']:
                mode=0 if job['name']=='csr' else 1
                row=pair['modes'][mode]['manifest']['verilog/'+name]
                require(row['sha256']==digest(actual)==digest(row['source']),'Different current same-mode prepared DUT')
                files[row['source']]=row['sha256']
            else:
                original=Path('/tmp/A_graph_compression_recovery_20261025_v1/search_read_control_staging_cosim_project_v1/solution/sim/verilog')/name
                require(digest(actual)==digest(original),'Different original staged DUT');files[str(original)]=digest(original)
        parent=ROOT/'data/derived'/('paired_binary_fsm_physical_20261025_v1/'+job['name'] if job['name'] in ['csr','compact'] else 'search_read_control_staging_physical_20261025_v2/csr')
        for name in ['run_flow.tcl','clock.xdc']:
            require((Path(job['work'])/name).read_bytes()==(parent/name).read_bytes(),'Changed physical flow/constraints')
        sources.append(dict(job=job['name'],files=len(job['source_names'])))
    OUT.mkdir()
    def run(label,command,code,marker):
        start=time.monotonic();p=subprocess.run(command,cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=120)
        log=OUT/(label+'.log');log.write_text(p.stdout)
        require(p.returncode==code and marker in p.stdout,'Unexpected validation result '+label)
        receipt=OUT/(label+'.receipt.json');atomic(receipt,dict(command=command,exit_code=p.returncode,elapsed_seconds=time.monotonic()-start,log_sha256=digest(log)))
        for path in [log,receipt]:files[str(path)]=digest(path)
    run('tests',[sys.executable,'-m','unittest','discover','-s','tests','-p','test_encoded_physical_execution_v2.py','-v'],0,'Ran 8 tests')
    for job in plan['jobs']:
        name=job['name'];work=Path(job['work']);target=OUT/(name+'_must_not_exist.json')
        run(name+'_early_arm',[sys.executable,str(ROOT/'scripts/encoded_physical_entry_v2.py'),'--bundle',str(BUNDLE),'--job',name,'--owner-pid',str(999999999)],1,'compact_nonzero_native_rtl_audit_20261029_v2.json')
        run(name+'_early_audit',[sys.executable,str(new),'--bundle',str(BUNDLE),'--job',name,'--status',str(OUT/'missing_status'),'--history',str(OUT/'missing_history'),'--output',str(target)],1,'FileNotFoundError')
        require(not target.exists() and not (work/'state.json').exists() and not (work/'guard').exists() and not (work/'session.json').exists(),'Early execution produced state/report/session')
    for path in [Path(__file__).resolve(),ROOT/'tests/test_encoded_physical_execution_v2.py']:files[str(path)]=digest(path)
    for path,h in files.items():require(digest(path)==h,'Evidence changed during validation')
    atomic(RESULT,dict(status='current_three_physical_entries_sources_and_early_rejection_verified_not_executed',files=files,source_matrix=sources,tests=8,actual_early_rejections=6,terminal_receipts_ast_unchanged=True,original_flow_and_constraints_byte_identical=True,physical_executed=False,limitations=['Prepared source comparison is not actual RTL acceptance; arm still requires current full accepted reports and same-mode actual DUT SHA.','No new Vivado session or synthesis/place/route operation; no platform/board/timing claim.']))
    print(RESULT)

if __name__=='__main__':main()
