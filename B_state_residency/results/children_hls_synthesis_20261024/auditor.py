"""Verify actual OOC mapping and structural checks for the tested first-touch HLS RTL."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/children_hls_synthesis_20261024';hls=ROOT/'results/children_hls_20261024';reset=ROOT/'results/children_reset_20261024'
 h=read(hls/'source_bound_audit.json');r=read(reset/'source_bound_audit.json')
 assert h['status']==r['status']=='passed' and h['manifest_sha256']==sha(hls/'manifest.json') and r['manifest_sha256']==sha(reset/'manifest.json')
 assert sha(out/'hls_audit.json')==sha(hls/'source_bound_audit.json') and sha(out/'reset_audit.json')==sha(reset/'source_bound_audit.json')
 for name,digest in h['cases']['32']['generated_rtl_artifacts'].items():assert sha(out/'rtl'/name)==digest
 script=ROOT/'hardware/scripts/synthesize_children_hls.tcl';assert sha(script)==sha(out/script.name)
 assert 'synth_design -top children_step -part xcu280-fsvh2892-2L-e -mode out_of_context' in script.read_text()
 assert 'ALLOW_COMBINATORIAL_LOOPS' not in script.read_text()+(out/'research_clock.xdc').read_text()
 receipt=read(out/'completion_receipt.json');assert receipt['exit_code']==0;log=receipt['output']
 assert 'CHILDREN_SYNTH_DONE' in log and '0 Critical Warnings and 0 Errors encountered.' in log
 assert not re.search(r'^(ERROR:|CRITICAL WARNING:)',log,re.M)
 checksum=re.search(r'Synth Design complete, checksum: (\w+)',log)[1]
 assert re.search(r'Violations found:\s*0\b',(out/'combinational_loops.rpt').read_text())
 timing=(out/'check_timing.rpt').read_text()
 for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:assert f'checking {label} (0)' in timing
 io={label:int(re.search(r'checking no_'+label+r'_delay \((\d+)\)',timing)[1])for label in ('input','output')}
 rpt=(out/'utilization.rpt').read_text()
 def number(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',rpt,re.M)[1])
 resources={k:number(k)for k in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs','CARRY8']}
 assert resources['Register as Latch']==0 and resources['Block RAM Tile']==0 and resources['URAM']==0 and resources['DSPs']==0
 assert (out/'children_step.dcp').stat().st_size>0
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 artifacts={str(p.relative_to(out)):sha(p)for p in sorted(out.rglob('*'))if p.is_file() and p.name not in ['final_audit.json','audit.stdout.log']}
 result={'status':'passed','resources':resources,'checksum':checksum,'elapsed_s':receipt['elapsed_seconds'],'combinational_loop_violations':0,'io_without_delay':io,'warnings':dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),'artifacts':artifacts,'auditor_sha256':sha(Path(__file__)),'scope':'Actual standalone first-touch HLS controller OOC synthesis, tested gen32 state-reset RTL. Excludes call collector, graph/design/cache storage, exclusion engine integration, routed timing, platform and board.'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='artifacts'},indent=2))
if __name__=='__main__':main()
