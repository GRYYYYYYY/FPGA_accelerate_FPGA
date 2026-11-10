from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/owner_axi_synthesis_20261024';sim=ROOT/'results/owner_axi_v2_20261024';boundary=ROOT/'results/owner_axi_boundaries_20261024'
 for dep,target in [(sim,'simulation_audit.json'),(boundary,'boundary_audit.json')]:
  g=read(dep/'source_bound_audit.json');assert g['status']=='passed' and g['manifest_sha256']==sha(dep/'manifest.json') and sha(out/target)==sha(dep/'source_bound_audit.json')
 assert sha(out/'owner_state_store.sv')==sha(sim/'sources/owner_state_store.sv')==sha(boundary/'sources/owner_state_store.sv')
 script=ROOT/'hardware/scripts/synthesize_owner_axi.tcl';assert sha(script)==sha(out/script.name)
 assert 'synth_design -top owner_state_store -part xcu280-fsvh2892-2L-e -mode out_of_context' in script.read_text()
 assert 'ALLOW_COMBINATORIAL_LOOPS'not in script.read_text()+(out/'research_clock.xdc').read_text()
 receipt=read(out/'completion_receipt.json');assert receipt['exit_code']==0
 log=receipt['output']
 if 'Output truncated.'in log:
  log=(out/'full_synthesis.log').read_text();capture=read(out/'log_capture.json');assert sha(out/'full_synthesis.log')==capture['sha256']
  excerpt=receipt['output'].split('OWNER_AXI_SYNTH_BEGIN version=2022.2\n',1)[1].split('\n\n... [Output truncated.',1)[0]
  assert not(Counter(excerpt.splitlines()[:-1])-Counter(log.splitlines()))
  assert any(line.startswith(excerpt.splitlines()[-1])for line in log.splitlines())
 assert 'OWNER_AXI_SYNTH_DONE'in log and '0 Critical Warnings and 0 Errors encountered.'in log
 assert not re.search(r'^(ERROR:|CRITICAL WARNING:)',log,re.M)
 checksum=re.search(r'Synth Design complete, checksum: (\w+)',log)[1]
 assert re.search(r'Violations found:\s*0\b',(out/'combinational_loops.rpt').read_text())
 timing=(out/'check_timing.rpt').read_text()
 for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:assert f'checking {label} (0)'in timing
 io={label:int(re.search(r'checking no_'+label+r'_delay \((\d+)\)',timing)[1])for label in ('input','output')}
 rpt=(out/'utilization.rpt').read_text()
 def number(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',rpt,re.M)[1])
 resources={k:number(k)for k in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs','CARRY8']}
 assert all(resources[k]==0 for k in ['Register as Latch','Block RAM Tile','URAM','DSPs'])
 assert (out/'owner_state_store.dcp').stat().st_size>0
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','resources':resources,'checksum':checksum,'elapsed_s':receipt['elapsed_seconds'],'combinational_loop_violations':0,'io_without_delay':io,'warnings':dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),'artifacts':{str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='final_audit.json'},'auditor_sha256':sha(Path(__file__)),'scope':'Actual default AXI owner store synthesis; external backing, owner identity bridge, integrated fabric, routed timing and board remain outside this gate.'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='artifacts'},indent=2))
if __name__=='__main__':main()
