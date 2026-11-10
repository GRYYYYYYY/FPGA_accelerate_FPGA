"""Verify actual OOC mapping and structural checks for the tested integrated access fabric."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/access_fabric_v3_synthesis_20261024';sim=ROOT/'results/access_fabric_v3_20261024'
 gate=read(sim/'source_bound_audit.json');assert gate['status']=='passed' and gate['manifest_sha256']==sha(sim/'manifest.json')
 assert sha(out/'simulation_audit.json')==sha(sim/'source_bound_audit.json')
 boundary=ROOT/'results/access_fabric_v3_boundaries_20261024';bg=read(boundary/'source_bound_audit.json');assert bg['status']=='passed'and bg['manifest_sha256']==sha(boundary/'manifest.json')and sha(out/'boundary_audit.json')==sha(boundary/'source_bound_audit.json')
 for name,spec in read(sim/'manifest.json')['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 cold=ROOT/'results/access_fabric_v3_cold_20261024';cg=read(cold/'source_bound_audit.json');assert cg['status']=='passed'and cg['manifest_sha256']==sha(cold/'manifest.json')and sha(out/'cold_audit.json')==sha(cold/'source_bound_audit.json')
 assert sha(out/'ownership_change_audit.json')==sha(sim/'ownership_change_audit.json')
 script=ROOT/'hardware/scripts/synthesize_access_fabric_v3.tcl';assert sha(script)==sha(out/script.name)
 assert 'synth_design -top access_fabric -part xcu280-fsvh2892-2L-e -mode out_of_context' in script.read_text()
 assert 'ALLOW_COMBINATORIAL_LOOPS' not in script.read_text()+(out/'research_clock.xdc').read_text()
 receipt=read(out/'completion_receipt.json');assert receipt['exit_code']==0
 log=receipt['output']
 if 'Output truncated.' in log:
  log=(out/'full_synthesis.log').read_text();capture=read(out/'log_capture.json');assert sha(out/'full_synthesis.log')==capture['sha256']
  excerpt=receipt['output'].split('ACCESS_FABRIC_V3_SYNTH_BEGIN version=2022.2\n',1)[1].split('\n\n... [Output truncated.',1)[0]
  assert not (Counter(excerpt.splitlines()[:-1])-Counter(log.splitlines()))
  assert any(line.startswith(excerpt.splitlines()[-1])for line in log.splitlines())
 assert 'ACCESS_FABRIC_V3_SYNTH_DONE' in log and '0 Critical Warnings and 0 Errors encountered.' in log
 assert not re.search(r'^(ERROR:|CRITICAL WARNING:)',log,re.M)
 checksum=re.search(r'Synth Design complete, checksum: (\w+)',log)[1]
 assert re.search(r'Violations found:\s*0\b',(out/'combinational_loops.rpt').read_text())
 timing=(out/'check_timing.rpt').read_text()
 for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:assert f'checking {label} (0)' in timing
 io={label:int(re.search(r'checking no_'+label+r'_delay \((\d+)\)',timing)[1])for label in ('input','output')}
 rpt=(out/'utilization.rpt').read_text()
 def number(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',rpt,re.M)[1])
 resources={k:number(k)for k in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs','CARRY8']}
 assert resources['Register as Latch']==0 and resources['URAM']==0
 assert (out/'access_fabric.dcp').stat().st_size>0
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 artifacts={str(p.relative_to(out)):sha(p)for p in sorted(out.rglob('*'))if p.is_file() and p.name not in ['final_audit.json','audit.stdout.log']}
 result={'status':'passed','resources':resources,'checksum':checksum,'elapsed_s':receipt['elapsed_seconds'],'combinational_loop_violations':0,'io_without_delay':io,'warnings':dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),'artifacts':artifacts,'auditor_sha256':sha(Path(__file__)),'scope':'Actual default FRAMES163840 access HLS, dispatcher, graph/table coordinate service and paged labels. Excludes owner backend, metadata producer, complete search, routed timing and board.'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='artifacts'},indent=2))
if __name__=='__main__':main()
