#!/usr/bin/env python3
"""One owner for candidate cosim, output audit, and comparison with the completed baseline."""
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_tile_cache_cosim_20261023_v1'
SOURCE=ROOT/'data/derived/vitis_tile_cache_kernel_20261023_v1'
ORIGINAL=ROOT/'build/vitis_graph_compact_tile_cache_20261023_v1'
PROJECT=ROOT/'build/vitis_graph_compact_tile_cache_cosim_20261023_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def main():
    review_path=ROOT/'results/vitis_tile_cache_synthesis_review_20261023_v1.json'
    review=json.loads(review_path.read_text())
    require(review['status']=='synthesis_reviewed_escalate_to_matched_rtl_experiment','Schedule review missing')
    synthesis_path=ROOT/'data/derived/vitis_tile_cache_synthesis_20261023_v1/report.json'
    synthesis=json.loads(synthesis_path.read_text())
    files={**review['files'],**synthesis['files'],**synthesis['generated']}
    dependencies=[review_path,synthesis_path,Path(__file__).resolve(),ROOT/'scripts/check_vitis_tile_cache_cosim.py',
                  ROOT/'scripts/check_vitis_kernel.py',ROOT/'hardware/vitis/run_stratified_cosim.tcl']
    files.update({str(p):digest(p) for p in dependencies})
    for p in (ORIGINAL/'solution/syn/verilog').glob('*.v'):files[str(p)]=digest(p)
    for path,sha in files.items():require(digest(path)==sha,'Frozen dependency changed: '+path)
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/'plan.json',{'files':files,'source':str(SOURCE),'project':str(PROJECT),
         'synthesized_project':str(ORIGINAL),'cpu':121,'scope':'Only the reviewed tile-cache experiment; no source edits or automatic implementation.'})
    state_path=OUT/'state.json';state={'owner_pid':os.getpid(),'status':'running','stage':'copy_project','cpu':121}
    save(state_path,state)
    try:
        shutil.copytree(ORIGINAL,PROJECT,ignore=shutil.ignore_patterns('csim','sim','impl'))
        save(OUT/'copied_project.json',{'original':str(ORIGINAL),'copy':str(PROJECT),
             'initial_files':{str(p.relative_to(PROJECT)):digest(p) for p in PROJECT.rglob('*') if p.is_file()}})
        env=os.environ.copy();env.update(A_STRATIFIED_PROJECT=str(PROJECT),A_STRATIFIED_MANIFEST=str(SOURCE/'rtl.txt'),
                                        LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c','121',str(HLS),'-f',str(ROOT/'hardware/vitis/run_stratified_cosim.tcl')]
        log_path=OUT/'cosim.log'
        with log_path.open('x') as stream:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            state.update(stage='cosimulation',child_pid=child.pid,command=command);save(state_path,state)
            code=child.wait()
        save(OUT/'receipt.json',{'exit_code':code,'log_sha256':digest(log_path),'command':command})
        state.pop('child_pid',None);require(code==0,'Cosim failed')
        auditor=ROOT/'scripts/check_vitis_tile_cache_cosim.py'
        candidate=ROOT/'results/vitis_tile_cache_cosim_audit_20261023_v1.json'
        def run_audit(output,baseline=None):
            command=[sys.executable,str(auditor),'--bundle',str(OUT),'--output',str(output)]
            if baseline:command.extend(['--baseline',str(baseline)])
            with (OUT/(output.stem+'.log')).open('x') as stream:
                subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,check=True)
        state.update(stage='candidate_audit');save(state_path,state);run_audit(candidate)
        state.update(stage='wait_baseline_comparison',candidate_audit=str(candidate),candidate_sha256=digest(candidate));save(state_path,state)
        # The original baseline already completed; require its bound audit receipt.
        baseline_dir=ROOT/'data/derived/vitis_stratified_cosim_20261023_v1'
        require((baseline_dir/'audit_receipt.json').exists(),'Completed baseline receipt missing')
        br=json.loads((baseline_dir/'audit_receipt.json').read_text());baseline=Path(br['output'])
        require(br['exit_code']==0 and digest(baseline)==br['report_sha256'],'Baseline receipt differs')
        comparison=ROOT/'results/vitis_tile_cache_comparison_20261023_v1.json'
        run_audit(comparison,baseline)
        state.update(status='complete',stage='matched_comparison_audited',comparison=str(comparison),comparison_sha256=digest(comparison))
        save(state_path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


if __name__=='__main__':main()
