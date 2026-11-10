from pathlib import Path
import sys,json,re
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();unit=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());u=json.loads((unit/'manifest.json').read_text());a=json.loads((unit/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and m['mcp_source_exit_code']==0 and m['session_closed']and a['manifest_sha256']==sha(unit/'manifest.json')
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h==u['sources'][n]['sha256']
 assert sha(p/'synth.tcl')==m['tcl_sha256'];log=(p/'vivado.log').read_text();assert 'AUTHORITY_SYNTH_DONE'in log and 'synth_design completed successfully'in log and not re.search(r'^(ERROR|CRITICAL WARNING):',log,re.M)
 report=(p/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in report and m['part']in report
 def number(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',report,re.M)[1])
 util={k:number(v)for k,v in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]}
 facts={}
 for n in ['counts.txt','port_counts.txt']:
  words=(p/n).read_text().split();facts.update({words[i]:int(words[i+1])for i in range(0,len(words),2)})
 assert facts['latches']==facts['blackboxes']==util['latches']==0
 for n in ['synth.dcp','synth.v']:assert (p/n).stat().st_size>1000
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'unit_audit_sha256':sha(unit/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'utilization':util,'facts':facts,'files':{str(q.relative_to(p)):sha(q)for q in sorted(p.rglob('*'))if q.is_file()and q.name!='source_bound_audit.json'},'scope':m['scope']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','utilization':util,'facts':facts}))
if __name__=='__main__':main()
