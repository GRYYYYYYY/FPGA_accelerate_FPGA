"""Audit the completed frozen OOC pair; preserve all negative timing results."""
from pathlib import Path
import csv,json,re
from report_codec_timing import digest,require,summary,constraints,rules
from report_indexed_directory import resource_counts
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/rtl_epoch6_endpoint_timing_v2_20261023'
def main():
 inputs=json.loads((OUT/'manifest.json').read_text())
 receipt=json.loads((OUT/'completion_receipt.json').read_text())
 require(not receipt['is_command_running'] and receipt['last_completed_code']==0,'Implementation not terminal-successful')
 require('rtl_epoch6_endpoint_timing_v2_20261023' in receipt['last_completed_output'],'Wrong command receipt')
 for path,digest_value in inputs['inputs'].items():require(digest(Path(path))==digest_value,'Changed input '+path)
 script=ROOT/'hardware/scripts/implement_epoch6_endpoint_v2.tcl'
 require(digest(script)==inputs['script_sha256']==digest(OUT/script.name),'Changed implementation flow')
 raw=Path(receipt['log_file']).read_text();starts=list(re.finditer(r'^B_EPOCH6_TIMING_BEGIN version=2022\.2',raw,re.M))
 require(len(starts)==1,'Missing or repeated pair run')
 tail=raw[starts[0].start():];ending=re.search(r'^B_EPOCH6_TIMING_PAIR_DONE\s*$',tail,re.M);require(ending is not None,'No pair completion')
 log=tail[:ending.end()]+'\n';require(not re.search(r'^ERROR:',log,re.M),'Implementation errors')
 (OUT/'implementation_session.log').write_text(log)
 result={'status':'completed','audit_status':'evidence_verified','platform_timing_closed':False,'physical_clock_model_complete':False,'board_performance':None,'variants':{},'inputs':inputs,'completion_receipt_sha256':digest(OUT/'completion_receipt.json'),'warnings':re.findall(r'^(?:CRITICAL )?WARNING:.*$',log,re.M)}
 expected=['create_clock -period 10.000 -name core_clk [get_ports clk]','current_instance -quiet']
 for name in ['epoch6']:
  folder=OUT/name
  require((folder/'routed.dcp').stat().st_size>10000,'Missing routed DCP '+name)
  require(f'B_EPOCH6_TIMING_VARIANT_DONE {name} version=2022.2' in (folder/'completed.txt').read_text(),'Incomplete variant '+name)
  for stage in ['before','after']:require(constraints(folder/f'constraints_{stage}.xdc')==expected,'Changed constraints '+name)
  timing=summary(folder/'timing_routed.rpt');paths=list(csv.DictReader((folder/'internal_paths.tsv').open(),delimiter='\t'))
  for kind,key in [('max','wns_ns'),('min','whs_ns')]:
   selected=[p for p in paths if p['delay_type']==kind];require(len(selected)==10,'Missing paths '+name)
   require(all(p['startpoint'] and p['endpoint'] for p in selected),'Incomplete path endpoints')
   require(abs(min(float(p['slack_ns']) for p in selected)-timing[key])<=0.0011,'Summary/path mismatch '+name)
  route=(folder/'route_status.rpt').read_text();counts={key.rstrip('. '):int(value) for key,value in re.findall(r'^\s*# of ([^\n:]+?)\s*:\s*(\d+)\s*:\s*$',route,re.M)}
  require(counts.get('nets with routing errors')==0,'Routing errors '+name)
  require(counts.get('routable nets',0)>0 and counts['routable nets']==counts.get('fully routed nets'),'Incomplete route '+name)
  resources=resource_counts(folder/'utilization_routed.rpt');require(resources['Register as Latch']==0,'Unexpected latch')
  result['variants'][name]={'routed_timing':timing,'synthesized_timing':summary(folder/'timing_synth.rpt'),'internal_paths':paths,'route_counts':counts,'resources':resources,'methodology_synth':rules(folder/'methodology_synth.rpt'),'methodology_routed':rules(folder/'methodology_routed.rpt'),'drc':rules(folder/'drc_routed.rpt'),'internal_constraints_met_in_this_model':all(timing[key]>=0 for key in ['wns_ns','whs_ns','wpws_ns'])}
 result['scope']='One OOC implementation per frozen default-capacity design, identical 10ns constraints and Default directives. No external IO delays or upstream physical clock context. Negative slack is retained; audit success means evidence integrity, not timing closure.'
 result['sources']={str(p):digest(p) for p in [Path(__file__).resolve(),ROOT/'hardware/scripts/report_codec_timing.py',ROOT/'hardware/scripts/report_indexed_directory.py']}
 result['artifacts']={str(p.relative_to(OUT)):digest(p) for p in OUT.rglob('*') if p.is_file() and '.Xil' not in p.parts and p.name not in ['final_manifest.json','completion_audit.json']}
 (OUT/'final_manifest.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 (OUT/'completion_audit.json').write_text(json.dumps({'status':'evidence_verified','final_manifest_sha256':digest(OUT/'final_manifest.json')},indent=2)+'\n')
 print(json.dumps({name:row['routed_timing'] for name,row in result['variants'].items()},indent=2))
if __name__=='__main__':main()
