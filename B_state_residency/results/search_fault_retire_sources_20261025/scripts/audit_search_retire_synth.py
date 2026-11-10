from pathlib import Path
from collections import Counter
import json,hashlib,re,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and m['mcp_source_exit_code']==0
 reference=Path(sys.argv[2]).resolve();a=json.loads((reference/'source_bound_audit.json').read_text());assert a['status']=='passed'
 rm=json.loads((reference/'manifest.json').read_text())
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h==rm['sources'][n]['sha256']
 assert sha(out/'synth.tcl')==m['tcl_sha256']
 p=reference/'sources/build_variant.py';sp=importlib.util.spec_from_file_location('system_builder',p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);b.ROOT=ROOT;b.BASE=ROOT/'results/query_lifecycle_join_v2/sources'
 for n,text in b.make().items():assert text.encode()==(out/'sources'/n).read_bytes(),n
 log=(out/'vivado.log').read_text();assert 'QUERY_LIFECYCLE_SYNTH_DONE' in log and 'synth_design completed successfully' in log and not re.search(r'^(?:ERROR|CRITICAL WARNING):',log,re.M)
 assert 'Synthesis finished with 0 errors, 0 critical warnings' in log
 r=(out/'utilization.rpt').read_text();assert 'Vivado v.2022.2' in r and 'Synthesized' in r and 'query_residency_system' in r and 'xcu280-fsvh2892-2L-e' in r
 def num(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',r,re.M)[1])
 utilization={n:num(label)for n,label in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs'),('URAM','URAM')]}
 assert utilization['latches']==0 and utilization['LUT']>0 and utilization['FF']>0
 words=(out/'netlist_facts.txt').read_text().split();facts={words[i]:int(words[i+1])for i in range(0,len(words),2)};assert facts['blackboxes']==facts['latches']==facts['file_agents']==0
 for n in ['synth.dcp','synth.v']:assert (out/n).stat().st_size>1000
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),reference_audit_sha256=sha(reference/'source_bound_audit.json'),utilization=utilization,netlist_facts=facts,warnings=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),files={str(p.relative_to(out)):sha(p)for p in sorted(out.rglob('*'))if p.is_file()and p.name!='source_bound_audit.json'},scope='Full search fault retirement variant query lifecycle OOC,32 slots/16384 frames, test injection default0. No black boxes/file agents/latches. No timing constraints, placement/routing/Fmax or board measurement; initial import/ripup commands and snapshot production remain external. Uninstantiated file-agent definition was read from inherited simulation file list and produces declaration warnings but has no synthesized cell.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','utilization':utilization,'facts':facts,'warnings':result['warnings']}))
if __name__=='__main__':main()
