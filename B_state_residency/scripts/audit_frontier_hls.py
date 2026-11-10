"""Independent frozen-source and stage-receipt audit for frontier HLS recovery."""
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/frontier_hls_relative_project_20261024'
 m=json.loads((out/'manifest.json').read_text())
 if m['status']!='passed':
  print(json.dumps({'status':'not_ready','flow_status':m['status']}));return
 assert m['part']=='xcu280-fsvh2892-2L-e' and m['clock_ns']==10.0 and m['capacity']==65536
 assert sha(out/'run_frontier_hls_relative_project.py')==m['runner_sha256']
 assert sha(out/'run_hls.tcl')==m['tcl_sha256']
 cpp=ROOT/'results/frontier_cpp_verified_20261024'
 for name,digest in m['sources'].items():
  assert sha(out/name)==digest==sha(cpp/name)
 for label,directory in [('cpp','frontier_cpp_verified_20261024'),('real_route','bounded_frontier_real_20261024')]:
  gate=ROOT/'results'/directory/'source_bound_audit.json'
  assert sha(gate)==m['gates'][label] and json.loads(gate.read_text())['status']=='passed'
 assert len(m['commands'])==1 and m['commands'][0]['exit_code']==0
 log=(out/'flow.stdout.log').read_text()
 assert 'version=2022.2' in log and not re.search(r'^ERROR:',log,re.M)
 assert 'FRONTIER_HLS_DONE' in log
 assert 'FRONTIER_TEST_PASS capacity=65536 checks=135228 comparisons=1000169' in log
 for stage in ['csim','csynth','cosim']:
  assert (out/(stage+'_completed.txt')).read_text()=='FRONTIER_'+stage.upper()+'_DONE\n'
 report=out/'frontier_step/solution1/sim/report/frontier_step_cosim.rpt'
 assert sha(report)==m['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',report.read_text(),re.I)
 assert sha(out/'flow.stdout.log')==m['flow_log_sha256']
 synth=out/'frontier_step/solution1/syn/report/frontier_step_csynth.xml'
 tree=ET.parse(synth).getroot()
 fields={}
 for section in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfTimingAnalysis','PerformanceEstimates/SummaryOfOverallLatency']:
  node=tree.find(section)
  if node is not None:fields[section]={v.tag:v.text for v in node}
 memory_receipts={}
 for field in ['id','key_bits']:
  paths=list((out/'frontier_step/solution1/syn/verilog').glob('*heap_'+field+'_RAM_AUTO_1R1W.v'))
  assert len(paths)==1
  memory=paths[0];rtl=memory.read_text()
  for param,value in [('DataWidth',32),('AddressWidth',16),('AddressRange',65536)]:
   assert re.search(r'parameter\s+'+param+r'\s*=\s*'+str(value)+r'\s*;',rtl)
  assert 'ram[0:AddressRange-1]' in rtl
  memory_receipts[field]={'sha256':sha(memory),'depth':65536,'width':32}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'synthesis_report_sha256':sha(synth),'synthesis_estimates':fields,'rtl_memory_capacity':memory_receipts,'generated_rtl_artifacts':{p.name:sha(p) for p in (out/'frontier_step/solution1/syn/verilog').iterdir() if p.is_file()},'memory_estimate_caution':'AUTO RAM reports 32 BRAM_18K for 4194304 payload bits; not a validated physical mapping. Validate actual BRAM/URAM usage in downstream Vivado synthesis.','scope':'Full-capacity standalone component Csim/Csynth/RTL cosim; estimates are not post-route timing, integrated routing, or board performance.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
if __name__=='__main__':main()
