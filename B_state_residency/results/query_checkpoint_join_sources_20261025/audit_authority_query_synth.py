from pathlib import Path
import json,sys,re
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();ref=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());r=json.loads((ref/'manifest.json').read_text());a=json.loads((ref/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and m['mcp_source_exit_code']==0 and m['session_closed']and a['manifest_sha256']==sha(ref/'manifest.json')
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h==r['sources'][n]['sha256']
 assert sha(p/'synth.tcl')==m['tcl_sha256'];log=(p/'vivado.log').read_text();assert 'QUERY_LIFECYCLE_SYNTH_DONE'in log and 'synth_design completed successfully'in log and not re.search(r'^(ERROR|CRITICAL WARNING):',log,re.M)
 report=(p/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in report and m['part']in report
 def n(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',report,re.M)[1])
 util={k:n(v)for k,v in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]};facts={}
 for name in ['facts.txt','port_counts.txt']:
  t=(p/name).read_text().split();facts.update({t[i]:int(t[i+1])for i in range(0,len(t),2)})
 assert facts['latches']==facts['blackboxes']==facts['file_agents']==util['latches']==0
 for name in ['synth.v','synth.dcp']:assert(p/name).stat().st_size>1000
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'reference_audit_sha256':sha(ref/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'utilization':util,'facts':facts,'files':{str(q.relative_to(p)):sha(q)for q in sorted(p.rglob('*'))if q.is_file()and q.name!='source_bound_audit.json'},'scope':m['scope']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','utilization':util,'facts':facts}))
if __name__=='__main__':main()
