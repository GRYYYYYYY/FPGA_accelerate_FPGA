#!/usr/bin/env python3
"""Run the existing, CPU-verified width64 search source in compact-mode HLS."""
import json,os,resource,shutil,subprocess
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    proof_path=ROOT/'results/search_packet_width64_comparison_20261024_v1.json';proof=json.loads(proof_path.read_text())
    require(proof['input_width_is_64'],'Missing predecessor')
    for p,h in proof['files'].items():require(digest(p)==h,'Changed width64 predecessor '+p)
    old=ROOT/'data/derived/search_packet_width64_20261024_v1';oldplan=json.loads((old/'plan.json').read_text())
    for p,h in oldplan['generated'].items():require(digest(p)==h,'Changed verified source')
    preflight=json.loads((old/'preflight_1.receipt.json').read_text());require(preflight['exit_code']==0 and digest(old/'preflight_1.log')==preflight['log_sha256'],'Missing compact sanitized CPU gate')
    require('SEARCH_KERNEL_TOP_ALL_PASS transactions=2 full_workspace_limits=1' in (old/'preflight_1.log').read_text(),'Missing complete compact CPU preflight')
    out=BASE/'search_packet_width64_compact_hls';project=BASE/'search_packet_width64_compact_hls_project';out.mkdir(exist_ok=False);require(not project.exists(),'Existing project')
    source=out/'source';shutil.copytree(old/'source',source)
    before=(source/'run_width_experiment.tcl').read_text();require(before.count('-DSEARCH_GRAPH_MODE=0')==2,'Different source flow')
    flow=source/'run_width_experiment.tcl';flow.write_text(before.replace('-DSEARCH_GRAPH_MODE=0','-DSEARCH_GRAPH_MODE=1'))
    files={str(p):digest(p) for p in source.iterdir() if p.is_file()}
    for p in [proof_path,old/'plan.json',old/'preflight_1.receipt.json',old/'preflight_1.log',ROOT/'results/search_kernel_compact_route_export_audit_20261025_v1.json',Path(__file__).resolve()]:files[str(p)]=digest(p)
    command=['prlimit','--stack=67108864:67108864','--','taskset','-c','125','/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls','-f',str(flow)]
    (out/'plan.json').write_text(json.dumps(dict(files=files,command=command,project=str(project),graph_mode=1,transactions=2,source_change_from_verified_width64='none; only HLS graph-mode cflags 0 to1',change_from_original_compact='Only packet m_axi max_widen_bitwidth64',max_single_file_bytes=8589934592,part='xcu280-fsvh2892-2L-e',clock_ns=5,uncertainty_ns=1.35),indent=2)+'\n')
    pointer=ROOT/'data/derived/search_packet_width64_compact_hls_20261025_v1';pointer.mkdir(exist_ok=False);(pointer/'location.json').write_text(json.dumps(dict(bundle=str(out),project=str(project),owner_pid=os.getpid(),local_storage_ephemeral=True),indent=2)+'\n')
    state=dict(owner_pid=os.getpid(),status='running',stage='csim_and_synthesis')
    def save():
        p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
    save()
    try:
        env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1','A_SEARCH_KERNEL_SOURCE':str(source),'A_SEARCH_KERNEL_PROJECT':str(project)}
        with (out/'flow.log').open('x') as f:
            child=subprocess.Popen(command,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,preexec_fn=lambda:resource.setrlimit(resource.RLIMIT_FSIZE,(8589934592,8589934592)));state['child_pid']=child.pid;save();code=child.wait()
        (out/'receipt.json').write_text(json.dumps(dict(command=command,exit_code=code,log_sha256=digest(out/'flow.log')),indent=2)+'\n');text=(out/'flow.log').read_text()
        require(code==0 and 'ERROR:' not in text and 'PACKET_WIDTH_SYNTHESIS_COMPLETE' in text,'Compact width HLS failed')
        for p,h in files.items():require(digest(p)==h,'Changed HLS input '+p)
        state.update(status='complete',stage='synthesized_pending_independent_review');save()
    except BaseException as e:state.update(status='failed',error=str(e));save();raise
if __name__=='__main__':main()
