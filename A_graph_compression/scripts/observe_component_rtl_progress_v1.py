#!/usr/bin/env python3
"""Snapshot live RTL progress with explicit simulator time units and scope."""
import datetime
import json
import os
import re
import xml.etree.ElementTree as ET
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT=Path(__file__).resolve().parents[1]
def main():
    out=ROOT/'data/derived/component_rtl_progress_observation_20261025_v1';out.mkdir(exist_ok=False)
    files={};observations=[]
    for stem,pid in [('site_occupancy',1787486),('route_tree',3001920),('retained_nodes',459268),('retained_edges',2216832)]:
        proc=Path('/proc')/str(pid);stat=(proc/'stat').read_text().rsplit(')',1)[1].split()
        command=(proc/'cmdline').read_bytes().replace(b'\0',b' ').decode()
        require('xsimk' in command and 'search_'+stem+'_top' in command,'Wrong live simulation process')
        work=ROOT/'data/derived'/(stem+'_rtl_20261024_v1')
        log=(work/'rtl.log').read_bytes();snapshot=out/(stem+'_rtl.log');snapshot.write_bytes(log)
        text=log.decode(errors='replace');require('Time resolution is 1 ps' in text,'Unknown simulation precision')
        top='search_'+stem+'_top'
        bench=ROOT/'build'/(stem+'_rtl_20261024_v1')/'solution/sim/verilog'/(top+'.autotb.v')
        source=bench.read_text()
        require(re.search(r'`timescale\s+1ns/1ps',source) and '$timeformat' not in source,'Unverified display time unit')
        require('"%0t' not in source or '$time' in source,'Unknown timestamp origin')
        half=float(re.search(r'`define AUTOTB_CLOCK_PERIOD_DIV2\s+([\d.]+)',source)[1]);period_ps=half*2000
        rows=[(int(a),int(b),int(c)) for a,b,c in re.findall(r'RTL Simulation :\s*(\d+) / (\d+) \[[^\]]+\] @ "(\d+)"',text)]
        require(rows and all(a[2]<=b[2] for a,b in zip(rows,rows[1:])),'No monotonic progress timestamps')
        xml=ROOT/'build'/(stem+'_hls_20261024_v1')/'solution/syn/report'/(top+'_csynth.xml')
        latency=ET.parse(xml).getroot().find('PerformanceEstimates/SummaryOfOverallLatency/Worst-caseLatency').text
        same=[x for x in rows if x[0]==rows[-1][0]]
        observations.append(dict(component=stem,pid=pid,start_ticks=stat[19],process_state=stat[0],command=command,
            completed_transactions=rows[-1][0],total_transactions=rows[-1][1],last_display_timestamp_ps=rows[-1][2],
            simulated_seconds=rows[-1][2]/1e12,clock_period_ns=period_ps/1000,
            approximate_elapsed_clock_cycles=rows[-1][2]/period_ps,
            same_transaction_display_span_seconds=(same[-1][2]-same[0][2])/1e12,
            hls_worst_case_latency_cycles=latency))
        for p in [snapshot,bench,xml]:files[str(p)]=digest(p)
    files[str(Path(__file__).resolve())]=digest(Path(__file__).resolve())
    result=dict(status='live_component_rtl_progress_snapshots_with_picosecond_timestamp_interpretation',
                observed_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),observations=observations,files=files,
                limits=['Live process and advancing simulation clock do not prove DUT transaction progress or absence of deadlock',
                        'Undefined HLS latency is not a proven simulation timeout bound',
                        'No process was interrupted or restarted; completion/original C postcheck still required'])
    target=ROOT/'results/component_rtl_progress_observation_20261025_v1.json';require(not target.exists(),'Refuse overwrite')
    temporary=target.with_suffix('.json.tmp')
    with temporary.open('x') as f:
        json.dump(result,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,target)
    print(json.dumps([{k:r[k] for k in ['component','completed_transactions','total_transactions','simulated_seconds','hls_worst_case_latency_cycles']} for r in observations]))
if __name__=='__main__':main()
