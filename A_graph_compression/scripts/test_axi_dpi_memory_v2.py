#!/usr/bin/env python3
"""Execute small native-SV vs DPI four-state/NBA storage equivalence cases."""
import json,os,subprocess
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
 out=Path('/tmp/A_graph_compression_recovery_20261025_v1/axi_dpi_memory_test_v2');out.mkdir(exist_ok=False)
 cpp=ROOT/'hardware/sim/axi_dpi_memory_v1.cpp';sv=ROOT/'hardware/sim/test_axi_dpi_memory_v2.sv'
 tcl=out/'run.tcl';tcl.write_text('run 100us\nquit\n');env={**os.environ,'LD_PRELOAD':'/lib/x86_64-linux-gnu/libudev.so.1'};rows=[]
 jobs=[('xsc',[str(BIN/'xsc'),'--cppversion','14',str(cpp)]),('xvlog',[str(BIN/'xvlog'),'--sv','--work','xil_defaultlib',str(sv)]),('xelab',[str(BIN/'xelab'),'xil_defaultlib.test_axi_dpi_memory_v2','-s','dpi_memory_test','-mt','off','--sv_lib','dpi','--sv_root','xsim.dir/work/xsc']),('xsim',[str(BIN/'xsim'),'dpi_memory_test','-tclbatch',str(tcl)])]
 for name,cmd in jobs:
  with (out/(name+'.log')).open('x') as f:code=subprocess.run(cmd,cwd=out,env=env,stdout=f,stderr=subprocess.STDOUT,timeout=180).returncode
  text=(out/(name+'.log')).read_text(errors='replace');rows.append(dict(phase=name,command=cmd,exit_code=code,log_sha256=digest(out/(name+'.log'))))
  (out/(name+'.receipt.json')).write_text(json.dumps(rows[-1],indent=2)+'\n');require(code==0 and 'ERROR:' not in text and 'Fatal:' not in text,name+' failed; inspect retained log')
  if name=='xsim':require('DPI_MEMORY_ALL_PASS cases=5' in text and text.count('DPI_MEMORY_CASE_PASS')==5,'Missing exact parity cases')
 report=dict(status='small_five_width_native_sv_vs_dpi_four_state_and_nba_storage_parity_verified',cases=5,updates_per_case=128,rows=rows,files={str(p):digest(p) for p in [cpp,sv,tcl,Path(__file__).resolve()]},limits=['Small storage-semantic tests only; no transformed HLS AXI model or full RTL acceptance yet','Full DUT, declared depths, transaction count and protocol must remain unchanged in subsequent model validation'])
 p=ROOT/'results/axi_dpi_memory_unit_20261025_v2.json';require(not p.exists(),'Refuse overwrite');p.write_text(json.dumps(report,indent=2)+'\n');print(report['status'])
if __name__=='__main__':main()
