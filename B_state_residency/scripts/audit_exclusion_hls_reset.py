"""Audit original-function oracle, real-route helper lineage and both RTL protocol cases."""
from pathlib import Path
import json,re,sys,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/exclusion_hls_reset_20261024';m=json.loads((out/'manifest.json').read_text())
 if m['status']!='passed':print(json.dumps({'status':'not_ready','flow_status':m['status']}));return
 assert m['part']=='xcu280-fsvh2892-2L-e' and m['clock_ns']==10.0 and m['top']=='exclusion_step'
 assert sha(out/'run_exclusion_hls_reset.py')==m['runner_sha256']==sha(ROOT/'scripts/run_exclusion_hls_reset.py')
 for name,digest in m['sources'].items():assert sha(out/name)==digest==sha(ROOT/'hardware/hls/exclusion_reset_state'/name)
 paths={'real':ROOT/'results/exclusion_real_20261024/source_bound_audit.json','unit':ROOT/'results/exclusion_unit_20261024/manifest.json'}
 gates={key:json.loads(p.read_text()) for key,p in paths.items()}
 for key,path in paths.items():assert sha(path)==m['gates'][key] and gates[key]['status']=='passed'
 assert sha(out/'rearchitect/v1/src/exclusion_machine.hpp')==gates['real']['helper_sha256']==gates['unit']['helper_sha256']
 original=ROOT/'results/frontier_real_20261024/original_trace.cpp';assert sha(original)==gates['unit']['original_source_sha256']
 source=original.read_text();start=source.index('    bool isPartOfExistingRoute(int parent, int child) const {');end=source.index('    // ----------------------------------------------------------------- getChildren',start)
 assert (out/'rearchitect/v1/tb/original_functions.inc').read_text()==source[start:end]
 assert set(m['cases'])=={'32','3'};cases={}
 for bits,expected_contexts,expected_checks in [(32,27648,354530),(3,7,12)]:
  row=m['cases'][str(bits)];case=out/f'gen{bits}';assert row['status']=='passed' and row['generation_bits']==bits
  assert [c['stage'] for c in row['commands']]==['cpp_build','cpp_test','hls'] and all(c['exit_code']==0 for c in row['commands'])
  assert f'-DEXCLUSION_GENERATION_BITS={bits}' in row['commands'][0]['argv']
  assert sha(case/'cpp_test')==row['cpp_binary_sha256']
  expected=f'EXCLUSION_PORT_PASS generation_bits={bits} contexts={expected_contexts} checks={expected_checks}'
  assert row['expected_pass_line']==expected and expected in (case/'cpp_test.log').read_text()
  assert sha(case/'run_hls.tcl')==row['tcl_sha256'] and f'-DEXCLUSION_GENERATION_BITS={bits}' in (case/'run_hls.tcl').read_text()
  assert row['argv_preflight']=={'csim':'','cosim':'','both_empty_allowed':True}
  log=(case/'flow.stdout.log').read_text();assert sha(case/'flow.stdout.log')==row['flow_log_sha256']
  assert log.count(expected)>=2 and not re.search(r'^ERROR:',log,re.M)
  assert f'EXCLUSION_HLS_BEGIN generation_bits={bits} version=2022.2' in log and f'EXCLUSION_HLS_DONE generation_bits={bits}' in log
  for stage in ['csim','csynth','cosim']:assert (case/(stage+'_completed.txt')).read_text()==stage.upper()+'_DONE\n'
  report=case/'exclusion_step/solution1/sim/report/exclusion_step_cosim.rpt';assert sha(report)==row['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',report.read_text(),re.I)
  synth=case/'exclusion_step/solution1/syn/report/exclusion_step_csynth.xml';tree=ET.parse(synth).getroot();fields={}
  for section in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfTimingAnalysis','PerformanceEstimates/SummaryOfOverallLatency']:
   node=tree.find(section)
   if node is not None:fields[section]={n.tag:n.text for n in node}
  assert 'config_rtl -reset state\n' in (case/'run_hls.tcl').read_text()
  rtl=case/'exclusion_step/solution1/syn/verilog'
  generated=(rtl/'exclusion_step_step.v').read_text()
  for field in ['generation','machine_request','machine_previous','machine_child_sequence','machine_excluded']:
   assert re.search(r"if \(ap_rst == 1'b1\) begin\s+controller_"+field+r' <= ',generated),field
  cases[str(bits)]={'contexts':expected_contexts,'calls':expected_checks,'synthesis_estimates':fields,'synthesis_report_sha256':sha(synth),'generated_rtl_artifacts':{p.name:sha(p) for p in rtl.iterdir() if p.is_file()}}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cases,'helper_sha256':gates['real']['helper_sha256'],'reset_config':'state','scope':'Explicit static reset generated RTL; subsequent runtime reset proof belongs to integrated engine tests. Standalone protocol RTL: full32 semantic combinations and reduced3 actual exhaustion. No 2^32-context exhaustion run, cross-reset stale-response protection, label-endpoint integration, full FPGA routing or board claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','cases':{k:{'contexts':v['contexts'],'calls':v['calls'],'estimates':v['synthesis_estimates']} for k,v in cases.items()}},indent=2))
if __name__=='__main__':main()
