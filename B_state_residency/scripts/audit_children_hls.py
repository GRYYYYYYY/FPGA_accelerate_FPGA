"""Bind first-touch HLS protocol, original oracle, reset registers and real gen3 exhaustion."""
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/children_hls_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 assert m['part']=='xcu280-fsvh2892-2L-e' and m['clock_ns']==10.0 and m['top']=='children_step'
 assert sha(out/'run_children_hls.py')==m['runner_sha256']==sha(ROOT/'scripts/run_children_hls.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest==sha(ROOT/'hardware/hls/children'/name)
 paths={'real':ROOT/'results/children_real_20261024/source_bound_audit.json','unit':ROOT/'results/children_unit_v4_20261024/manifest.json'}
 gates={key:json.loads(p.read_text())for key,p in paths.items()}
 for key,path in paths.items():assert sha(path)==m['gates'][key] and gates[key]['status']=='passed'
 assert gates['real']['manifest_sha256']==sha(paths['real'].parent/'manifest.json')
 assert sha(out/'rearchitect/v1/src/children_machine.hpp')==gates['real']['helper_sha256']==gates['unit']['helper_sha256']
 for name in ['original_exclusion.inc','original_dead.inc','RouteNodeType.hpp']:assert sha(out/'rearchitect/v1/tb'/name)==gates['unit']['artifacts'][name]
 assert set(m['cases'])=={'32','3'};cases={}
 for bits,contexts,calls in [(32,93728,918795),(3,7,406)]:
  row=m['cases'][str(bits)];case=out/f'gen{bits}';assert row['status']=='passed' and row['generation_bits']==bits
  assert [c['stage']for c in row['commands']]==['cpp_build','cpp_test','hls'] and all(c['exit_code']==0 for c in row['commands'])
  assert f'-DCHILDREN_GENERATION_BITS={bits}' in row['commands'][0]['argv'] and sha(case/'cpp_test')==row['cpp_binary_sha256']
  cpp=(case/'cpp_test.log').read_text();counts={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cpp)}
  assert counts['generation_bits']==bits and counts['contexts']==contexts and counts['calls']==calls and row['checks']==calls
  expected=f'CHILDREN_PORT_PASS generation_bits={bits} contexts={contexts} calls={calls}'
  assert row['expected_pass_line']==expected and expected in cpp
  if bits==32:
   assert counts=={'generation_bits':32,'contexts':93728,'calls':918795,'rejected':10657,'next':252794,'exclude':252794,'create':66833,'classify':66833,'emit':46896,'check_dead':32917,'mark_dead':644,'publish':93728}
  else:assert counts['rejected']==337 and counts['publish']==7
  tcl=(case/'run_hls.tcl').read_text();assert sha(case/'run_hls.tcl')==row['tcl_sha256']
  assert f'-DCHILDREN_GENERATION_BITS={bits}' in tcl and 'config_rtl -reset state\n' in tcl
  assert row['argv_preflight']=={'csim':'','cosim':'','both_empty_allowed':True}
  log=(case/'flow.stdout.log').read_text();assert sha(case/'flow.stdout.log')==row['flow_log_sha256']
  assert log.count(expected)>=2 and not re.search(r'^ERROR:',log,re.M)
  assert f'CHILDREN_HLS_BEGIN generation_bits={bits} version=2022.2' in log and f'CHILDREN_HLS_DONE generation_bits={bits}' in log
  for stage in ['csim','csynth','cosim']:assert (case/(stage+'_completed.txt')).read_text()==stage.upper()+'_DONE\n'
  report=case/'children_step/solution1/sim/report/children_step_cosim.rpt';assert sha(report)==row['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',report.read_text(),re.I)
  synth=case/'children_step/solution1/syn/report/children_step_csynth.xml';tree=ET.parse(synth).getroot();fields={}
  for section in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfTimingAnalysis','PerformanceEstimates/SummaryOfOverallLatency']:
   node=tree.find(section)
   if node is not None:fields[section]={n.tag:n.text for n in node}
  rtl=case/'children_step/solution1/syn/verilog';generated=(rtl/'children_step_step.v').read_text()
  for field in ['generation','parent','query','price','active','fault','emitted','machine_count','machine_position','machine_child','machine_prune','machine_any_alive','machine_request']:
   assert re.search(r"if \(ap_rst == 1'b1\) begin\s+controller_"+field+r' <= ',generated),field
  assert re.search(r"if \(ap_rst == 1'b1\) begin\s+controller_machine_request <= 4'd8;",generated)
  cases[str(bits)]={'contexts':contexts,'calls':calls,'counts':counts,'synthesis_estimates':fields,'synthesis_report_sha256':sha(synth),'generated_rtl_artifacts':{p.name:sha(p)for p in rtl.iterdir()if p.is_file()}}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cases,'helper_sha256':gates['real']['helper_sha256'],'reset_config':'state','scope':'Standalone first-touch request protocol RTL with original exclusion/dead predicates and independent service-event oracle; gen32 semantic tests plus actual gen3 exhaustion. External graph/cache/created services are TB models, no device storage integration or whole-router/board proof. Runtime cold-reset proof is separate.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'status':'passed','cases':{k:{'contexts':v['contexts'],'calls':v['calls'],'estimates':v['synthesis_estimates']}for k,v in cases.items()}},indent=2))
if __name__=='__main__':main()
