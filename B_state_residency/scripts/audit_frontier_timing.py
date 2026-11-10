"""Audit standalone frontier physical evidence, including negative timing results."""
from pathlib import Path
import csv,difflib,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'hardware/scripts'))
from report_codec_timing import digest,require,summary,constraints,rules
from report_indexed_directory import resource_counts

def main():
 out=ROOT/'results/frontier_hls_timing_20261024';m=json.loads((out/'manifest.json').read_text())
 receipt=json.loads((out/'completion_receipt.json').read_text())
 require(not receipt['is_command_running'] and receipt['last_completed_code']==0,'Not terminal-successful')
 require('frontier_hls_timing_20261024' in receipt['last_completed_output'],'Wrong completion receipt')
 script=ROOT/'hardware/scripts/implement_frontier_hls.tcl'
 require(digest(script)==m['script_sha256']==digest(out/script.name),'Changed script')
 syn=ROOT/'results/frontier_hls_vivado_synthesis_20261024'
 require(digest(syn/'final_audit.json')==m['synthesis_audit_sha256'],'Changed synthesis audit')
 require(digest(syn/'frontier_step.dcp')==m['input_dcp_sha256'],'Changed input DCP')
 require(re.fullmatch(r'FRONTIER_HLS_TIMING_DONE version=2022\.2 part=xcu280-fsvh2892-2L-e period=10\.0+\n',(out/'completed.txt').read_text()) is not None,'Bad marker')
 raw=Path(receipt['log_file']).read_text();starts=list(re.finditer(r'^FRONTIER_HLS_TIMING_BEGIN version=2022\.2',raw,re.M));require(len(starts)==1,'Repeated or missing launch')
 log=raw[starts[0].start():];ending=re.search(r'^FRONTIER_HLS_TIMING_DONE\s*$',log,re.M);require(ending is not None,'Missing terminal log')
 log=log[:ending.end()]+'\n';require(not re.search(r'^ERROR:',log,re.M),'Tool errors');(out/'implementation_session.log').write_text(log)
 before=(out/'constraints_before.xdc').read_text();after=(out/'constraints_after.xdc').read_text()
 require(constraints(out/'constraints_before.xdc')==constraints(out/'constraints_after.xdc'),'Constraints changed')
 require(any('create_clock' in line and '10.000' in line and 'research_clock' in line and 'ap_clk' in line for line in constraints(out/'constraints_before.xdc')),'Missing clock')
 require(not re.search(r'set_(?:false_path|multicycle_path|input_delay|output_delay)',before),'Unexpected timing exceptions/IO budgets')
 timing=summary(out/'timing_routed.rpt');paths=list(csv.DictReader((out/'internal_paths.tsv').open(),delimiter='\t'))
 for kind,key in [('max','wns_ns'),('min','whs_ns')]:
  selected=[p for p in paths if p['delay_type']==kind];require(len(selected)==10,'Missing timing paths')
  require(all(p['startpoint'] and p['endpoint'] for p in selected),'Missing path endpoints')
  require(abs(min(float(p['slack_ns']) for p in selected)-timing[key])<=.0011,'Path/summary mismatch')
 counts={k.rstrip('. '):int(v) for k,v in re.findall(r'^\s*# of ([^\n:]+?)\s*:\s*(\d+)\s*:\s*$',(out/'route_status.rpt').read_text(),re.M)}
 require(counts.get('nets with routing errors')==0 and counts.get('routable nets',0)>0 and counts['routable nets']==counts.get('fully routed nets'),'Incomplete/error route')
 resources=resource_counts(out/'utilization_routed.rpt');require(resources['Register as Latch']==0,'Unexpected latches');require((out/'routed.dcp').stat().st_size>10000,'Missing DCP')
 method={stage:rules(out/('methodology_'+stage+'.rpt')) for stage in ['synth','routed']}
 (out/'constraints_diff.html').write_text(difflib.HtmlDiff().make_file(before.splitlines(),after.splitlines(),'Before','After'))
 report='''# Frontier methodology evidence\n\nVivado 2022.2 text reports substitute for the Ross skill 2026.1+ JSON commands. No constraints were changed or waived. Research clock10ns only; external input/output budgets and platform clock context are absent. Standalone internal timing is not platform timing closure or a board measurement.\n\nObserved checks:\n\n'''+json.dumps({'timing':timing,'methodology':method,'drc':rules(out/'drc_routed.rpt')},indent=2)+'\n'
 (out/'METHODOLOGY_RESOLUTION_REPORT.md').write_text(report)
 result={'status':'evidence_verified','auditor_sha256':digest(Path(__file__)),'launch_manifest_sha256':digest(out/'manifest.json'),'routed_timing':timing,'resources':resources,'internal_paths':paths,'route_counts':counts,'methodology':method,'internal_constraints_met_in_this_model':all(timing[k]>=0 for k in ['wns_ns','whs_ns','wpws_ns']),'platform_timing_closed':False,'board_performance':None,'artifacts':{p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name not in ['final_audit.json','audit.stdout.log']}}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'timing':timing,'resources':resources},indent=2))
if __name__=='__main__':main()
