#!/usr/bin/env python3
"""Validate the single-sort variant, synthesize, then stop for schedule investigation."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import subprocess
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require, validate_case_log

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'data/derived/vitis_merge_synthesis_20261023_v1'
SOURCE = ROOT/'data/derived/vitis_merge_kernel_20261023_v1'
PROJECT = ROOT/'build/vitis_graph_compact_merge_20261023_v1'
HLS = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/bin/vitis_hls')


def save(path, value):
    temp = path.with_suffix('.tmp'); temp.write_text(json.dumps(value,indent=2)+'\n'); temp.replace(path)


def main():
    require(121 in os.sched_getaffinity(0), 'CPU121 unavailable')
    source_plan = SOURCE/'plan.json'; plan = json.loads(source_plan.read_text())
    stress_path = ROOT/'results/vitis_merge_sort_stress_20261023_v1.json'
    stress = json.loads(stress_path.read_text())
    require(stress['status'] == 'all_degrees_and_five_patterns_pass_asan_ubsan'
            and stress['execution_exit_code'] == 0 and stress['compile_exit_code'] == 0, 'Sort stress test failed')
    files = {**plan['files'], **plan['generated'], **stress['files']}
    for path, sha in files.items(): require(digest(path) == sha, 'Frozen experiment input changed: '+path)
    files.update({str(p):digest(p) for p in [source_plan,stress_path,Path(__file__).resolve(),
                  ROOT/'hardware/vitis/run_merge_synth.tcl',ROOT/'scripts/check_vitis_kernel.py']})
    OUT.mkdir(parents=True,exist_ok=False)
    save(OUT/'plan.json', {'files':files,'source':str(SOURCE),'project':str(PROJECT),'cpu':121,
         'created_utc':datetime.now(timezone.utc).isoformat(),
         'scope':'CPU golden check plus classic2022.2 C simulation and synthesis; stop for inspection before any RTL/implementation escalation.'})
    state_path = OUT/'state.json'
    state = {'owner_pid':os.getpid(),'status':'running','stage':'cpu_golden','cpu':121}
    save(state_path,state)
    try:
        binary = OUT/'cpu_test'
        compile_command = ['taskset','-c','121','g++','-std=c++14','-O2','-Wno-unknown-pragmas',
                           *[str(SOURCE/name) for name in ['graph_body.cpp','graph_accel.cpp','test_graph_expand.cpp']],
                           '-o',str(binary)]
        with (OUT/'compile.log').open('x') as log:
            subprocess.run(compile_command,stdout=log,stderr=subprocess.STDOUT,check=True)
        manifest = SOURCE/'validation.txt'
        with (OUT/'cpu.log').open('x') as log:
            subprocess.run(['taskset','-c','121',str(binary),str(manifest)],stdout=log,stderr=subprocess.STDOUT,check=True)
        cpu_cases = validate_case_log((OUT/'cpu.log').read_text(),manifest,1)
        require(len(cpu_cases)==23,'Expected complete graph, original negatives, and stratified stimuli')
        env = os.environ.copy(); env.update(A_MERGE_SOURCE=str(SOURCE),A_MERGE_PROJECT=str(PROJECT),
                                            LD_PRELOAD='/lib/x86_64-linux-gnu/libudev.so.1')
        command = ['taskset','-c','121',str(HLS),'-f',str(ROOT/'hardware/vitis/run_merge_synth.tcl')]
        log_path = OUT/'synth.log'
        with log_path.open('x') as log:
            child = subprocess.Popen(command,cwd=OUT,env=env,stdout=log,stderr=subprocess.STDOUT)
            state.update(stage='csim_csynth',child_pid=child.pid,command=command); save(state_path,state)
            code = child.wait()
        save(OUT/'receipt.json',{'exit_code':code,'command':command,'log_sha256':digest(log_path)})
        state.pop('child_pid',None)
        content = log_path.read_text()
        require(code==0 and 'VITIS_MERGE_SYNTH_COMPLETE' in content and 'ERROR:' not in content,'HLS stage failed')
        hls_cases = validate_case_log(content,manifest,1)
        require(hls_cases==cpu_cases,'HLS Csim coverage differs')
        synth = PROJECT/'solution/syn/report/graph_accel_csynth.xml'
        xml = ET.parse(synth).getroot()
        require(xml.findtext('UserAssignments/Part')=='xcu280-fsvh2892-2L-e'
                and float(xml.findtext('UserAssignments/TargetClockPeriod'))==5,'Part/clock differs')
        for path, sha in files.items():require(digest(path)==sha,'Input changed during synthesis')
        generated = {str(p):digest(p) for p in [synth,log_path,OUT/'receipt.json',OUT/'compile.log',OUT/'cpu.log',binary]}
        save(OUT/'report.json',{'status':'cpu_and_hls_csim_pass_synthesis_pending_schedule_review',
             'files':files,'generated':generated,'cpu_cases':cpu_cases,'hls_cases':hls_cases,
             'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
             'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
             'limitations':['Synthesis estimates are not RTL cycles or routed results.','Only sorting changed; low-degree regressions and added memory remain possible.']})
        state.update(status='complete',stage='await_schedule_review');save(state_path,state)
    except BaseException as exc:
        state.update(status='failed',error=str(exc));save(state_path,state);raise


if __name__=='__main__': main()
