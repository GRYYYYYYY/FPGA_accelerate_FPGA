from pathlib import Path
import json,re,sys
from run_checkpoint_authority import sha

def main():
 p=Path(sys.argv[1]).resolve();unit=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());a=json.loads((unit/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and m['mcp_source_exit_code']==0 and m['session_closed']and a['manifest_sha256']==sha(unit/'manifest.json')
 assert sha(p/'sources/query_lifecycle.sv')==m['rtl_sha256']==sha(Path(m['reference']))
 if not m['baseline']:assert m['rtl_sha256']==sha(unit/'sources/query_lifecycle.sv')
 assert sha(p/'synth.tcl')==m['tcl_sha256'];log=(p/'vivado.log').read_text();assert 'QUERY_CP_SYNTH_DONE'in log and 'synth_design completed successfully'in log and not re.search(r'^(ERROR|CRITICAL WARNING):',log,re.M)
 r=(p/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in r
 def value(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',r,re.M)[1])
 util={k:value(v)for k,v in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]};t=(p/'facts.txt').read_text().split();facts={t[i]:int(t[i+1])for i in range(0,len(t),2)};assert facts['latches']==facts['blackboxes']==util['latches']==0
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'unit_audit_sha256':sha(unit/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'utilization':util,'facts':facts,'files':{str(q.relative_to(p)):sha(q)for q in sorted(p.rglob('*'))if q.is_file()and q.name!='source_bound_audit.json'},'scope':m['scope']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','baseline':m['baseline'],'utilization':util}))
if __name__=='__main__':main()
