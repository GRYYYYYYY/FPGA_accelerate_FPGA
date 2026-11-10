from pathlib import Path
from collections import Counter
import json,hashlib,re,sys
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=Path(sys.argv[1]).resolve();unit=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());u=json.loads((unit/'manifest.json').read_text());a=json.loads((unit/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed' and m['mcp_source_exit_code']==0 and m['session_closed']
 assert a['manifest_sha256']==sha(unit/'manifest.json')
 assert sha(p/'sources/route_commit_controller.sv')==m['rtl_sha256']==u['sources']['route_commit_controller.sv']
 assert sha(p/'synth.tcl')==m['tcl_sha256']
 log=(p/'vivado.log').read_text();assert 'ROUTE_CHECKPOINT_SYNTH_DONE'in log and 'synth_design completed successfully'in log and 'Synthesis finished with 0 errors, 0 critical warnings'in log and not re.search(r'^(ERROR|CRITICAL WARNING):',log,re.M)
 r=(p/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in r and 'xcu280-fsvh2892-2L-e'in r and 'Synthesized'in r
 def n(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',r,re.M)[1])
 util={k:n(label)for k,label in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]}
 words=(p/'netlist_facts.txt').read_text().split();facts={words[i]:int(words[i+1])for i in range(0,len(words),2)};assert facts['blackboxes']==facts['latches']==util['latches']==0
 for f in ['synth.dcp','synth.v']:assert (p/f).stat().st_size>1000
 result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),unit_audit_sha256=sha(unit/'source_bound_audit.json'),utilization=util,facts=facts,warnings=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),files={str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f.name!='source_bound_audit.json'},scope='Route saved-path checkpoint component, default32-node/two-slot OOC only. Full system/fence/AXI integration and timing/board measurements absent.')
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','utilization':util,'facts':facts}))
if __name__=='__main__':main()
