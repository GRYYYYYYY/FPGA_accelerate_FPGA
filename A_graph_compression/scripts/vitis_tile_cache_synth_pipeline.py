#!/usr/bin/env python3
"""Synthesize the verified single tile-cache variant; retain all provenance."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest,require,validate_case_log

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'data/derived/vitis_tile_cache_synthesis_20261023_v1'
SOURCE=ROOT/'data/derived/vitis_tile_cache_kernel_20261023_v1'
PROJECT=ROOT/'build/vitis_graph_compact_tile_cache_20261023_v1'
HLS=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path,value):
    temp=path.with_suffix('.tmp');temp.write_text(json.dumps(value,indent=2)+'\n');temp.replace(path)


def main():
    require(121 in os.sched_getaffinity(0),'CPU121 unavailable')
    proof_path=ROOT/'data/derived/vitis_tile_cache_profile_20261023_v1/report.json'
    proof=json.loads(proof_path.read_text())
    require(proof['status']=='plain_and_instrumented_full_golden_and_helper_sanitizers_passed', 'CPU preflight missing')
    files={**proof['files'],**proof['generated']}
    for path in [proof_path,Path(__file__).resolve(),ROOT/'hardware/vitis/run_tile_cache_synth.tcl']:
        files[str(path)]=digest(path)
    for path,sha in files.items():require(digest(path)==sha,'Frozen input changed: '+path)
    require(not PROJECT.exists(),'Refusing existing synthesis project')
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/'plan.json',{'files':files,'source':str(SOURCE),'project':str(PROJECT), 'cpu':121,
         'created_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'Classic2022.2 Csim and synthesis; no automatic implementation or default promotion.'})
    state_path=OUT/'state.json';state={'owner_pid':os.getpid(),'status':'running','stage':'csim_csynth','cpu':121}
    save(state_path,state)
    try:
        env=os.environ.copy();env.update(A_TILE_CACHE_SOURCE=str(SOURCE),A_TILE_CACHE_PROJECT=str(PROJECT),
                                        LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command=['taskset','-c','121',str(HLS),'-f',str(ROOT/'hardware/vitis/run_tile_cache_synth.tcl')]
        log_path=OUT/'synth.log'
        with log_path.open('x') as stream:
            child=subprocess.Popen(command,cwd=OUT,env=env,stdout=stream,stderr=subprocess.STDOUT)
            state.update(child_pid=child.pid,command=command);save(state_path,state)
            code=child.wait()
        save(OUT/'receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(log_path)})
        state.pop('child_pid',None)
        content=log_path.read_text()
        require(code==0 and 'VITIS_TILE_CACHE_SYNTH_COMPLETE' in content and 'ERROR:' not in content,'HLS failed')
        cases=validate_case_log(content,SOURCE/'validation.txt',1)
        require(cases==proof['plain_cases'],'HLS Csim differs from full CPU coverage')
        synth=PROJECT/'solution/syn/report/graph_accel_csynth.xml';xml=ET.parse(synth).getroot()
        require(xml.findtext('UserAssignments/Part')=='xcu280-fsvh2892-2L-e'
                and float(xml.findtext('UserAssignments/TargetClockPeriod'))==5,'Part/clock differs')
        for path,sha in files.items():require(digest(path)==sha,'Input changed during synthesis')
        generated={str(p):digest(p) for p in [synth,log_path,OUT/'receipt.json']}
        save(OUT/'report.json',{'status':'cpu_and_hls_csim_pass_synthesis_pending_schedule_review',
            'files':files,'generated':generated,'hls_cases':cases,
            'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
            'limitations':['Synthesis estimates are not RTL cycles or routed results.',
                           'Lookup cache may change control scheduling; inspect before matched RTL.']})
        state.update(status='complete',stage='await_schedule_review');save(state_path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


if __name__=='__main__':main()
