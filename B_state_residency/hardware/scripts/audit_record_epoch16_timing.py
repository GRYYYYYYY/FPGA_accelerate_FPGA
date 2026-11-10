"""Verify candidate OOC route evidence; a verified negative result stays negative."""
from pathlib import Path
import csv,json,re
from report_codec_timing import digest,require,summary,constraints,rules
from report_indexed_directory import resource_counts
ROOT=Path(__file__).resolve().parents[2]
def main():
 out=ROOT/'results/record_epoch16_timing_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text())
 receipt=json.loads((out/'completion_receipt.json').read_text())
 require(not receipt['is_command_running'] and receipt['last_completed_code']==0,'Not terminal-successful')
 require('record_epoch16_timing_20261024' in receipt['last_completed_output'],'Wrong completion receipt')
 script=ROOT/'hardware/scripts/implement_record_epoch16.tcl';require(digest(script)==m['script_sha256']==digest(out/script.name),'Changed script')
 syn=ROOT/'results/record_epoch16_synthesis_20261024';require(digest(syn/'final_audit.json')==m['synthesis_audit_sha256'],'Changed synthesis audit');require(digest(syn/'memory_scratch_endpoint_small_staticcodec.dcp')==m['input_dcp_sha256'],'Changed DCP')
 baseline=ROOT/'results/record_epoch6_timing_20261024';bp=baseline/'final_audit.json';require(digest(bp)==m['baseline_manifest_sha256'],'Changed baseline')
 b=json.loads(bp.read_text());require(b['status']=='evidence_verified','Unverified baseline')
 for name in ['timing_routed.rpt','utilization_routed.rpt','constraints_before.xdc','constraints_after.xdc']:require(digest(baseline/name)==b['artifacts'][name],'Changed baseline report '+name)
 require((out/'completed.txt').read_text()=='RECORD_EPOCH16_TIMING_DONE version=2022.2 part=xcu280-fsvh2892-2L-e period=10.000\n' or (out/'completed.txt').read_text()=='RECORD_EPOCH16_TIMING_DONE version=2022.2 part=xcu280-fsvh2892-2L-e period=10.0\n','Wrong completion marker')
 raw=Path(receipt['log_file']).read_text();starts=list(re.finditer(r'^RECORD_EPOCH16_TIMING_BEGIN version=2022\.2',raw,re.M));require(len(starts)==1,'Missing/repeated implementation')
 log=raw[starts[0].start():];ending=re.search(r'^RECORD_EPOCH16_TIMING_DONE\s*$',log,re.M);require(ending is not None,'Missing terminal log');log=log[:ending.end()]+'\n';require(not re.search(r'^ERROR:',log,re.M),'Tool errors');(out/'implementation_session.log').write_text(log)
 for stage in ['before','after']:require(constraints(out/f'constraints_{stage}.xdc')==constraints(baseline/f'constraints_{stage}.xdc'),'Changed constraints')
 timing=summary(out/'timing_routed.rpt');paths=list(csv.DictReader((out/'internal_paths.tsv').open(),delimiter='\t'))
 for kind,key in [('max','wns_ns'),('min','whs_ns')]:
  selected=[p for p in paths if p['delay_type']==kind];require(len(selected)==10,'Missing paths');require(all(p['startpoint'] and p['endpoint'] for p in selected),'Missing endpoints');require(abs(min(float(p['slack_ns']) for p in selected)-timing[key])<=.0011,'Path/summary mismatch')
 counts={k.rstrip('. '):int(v) for k,v in re.findall(r'^\s*# of ([^\n:]+?)\s*:\s*(\d+)\s*:\s*$',(out/'route_status.rpt').read_text(),re.M)}
 require(counts.get('nets with routing errors')==0 and counts.get('routable nets',0)>0 and counts['routable nets']==counts.get('fully routed nets'),'Incomplete/error route')
 resources=resource_counts(out/'utilization_routed.rpt');require(resources['Register as Latch']==0,'Unexpected latch');require((out/'routed.dcp').stat().st_size>10000,'Missing routed DCP')
 result={'status':'evidence_verified','launch_manifest_sha256':digest(mp),'baseline_manifest_sha256':digest(bp),'routed_timing':timing,'baseline_routed_timing':b['routed_timing'],'resources':resources,'baseline_resources':b['resources'],'internal_paths':paths,'route_counts':counts,'methodology_synth':rules(out/'methodology_synth.rpt'),'methodology_routed':rules(out/'methodology_routed.rpt'),'drc':rules(out/'drc_routed.rpt'),'internal_constraints_met_in_this_model':all(timing[k]>=0 for k in ['wns_ns','whs_ns','wpws_ns']),'platform_timing_closed':False,'physical_clock_model_complete':False,'board_performance':None,'scope':'paired epoch16 vs epoch6 native static-codec OOC implementations; identical 10ns constraint and Default directives, missing external IO/clock model','artifacts':{p.name:digest(p) for p in out.iterdir() if p.is_file() and p.name!='final_audit.json'}}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(timing,indent=2))
if __name__=='__main__':main()
