"""Audit the tested default candidate netlist and preserve explicit timing limits."""
from pathlib import Path
from collections import Counter
import hashlib,json,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='prepared'and m['top']=='candidate_engine'and len(m['rtl'])==52
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']
 revision=read(out/'revision.json');assert sha(out/'revision.json')==m['revision_sha256']and revision['status']=='passed'
 for name,spec in m['gates'].items():
  dep=ROOT/'results'/name;gate=read(dep/'source_bound_audit.json');assert gate['status']=='passed'and gate['manifest_sha256']==sha(dep/'manifest.json')==spec['manifest_sha256']
  assert sha(dep/'source_bound_audit.json')==spec['audit_sha256']==sha(out/(name+'_audit.json'))
 script=ROOT/'hardware/scripts/synthesize_candidate.tcl';assert sha(script)==sha(out/'synthesize_candidate.tcl')
 assert 'synth_design -top candidate_engine -part xcu280-fsvh2892-2L-e -mode out_of_context'in script.read_text()
 assert 'ALLOW_COMBINATORIAL_LOOPS'not in script.read_text()+(out/'research_clock.xdc').read_text()
 receipt=read(out/'completion_receipt.json');assert receipt['exit_code']==0 and receipt['command'].endswith('/hardware/scripts/synthesize_candidate.tcl')
 log=(out/'full_synthesis.log').read_text();capture=read(out/'log_capture.json');assert sha(out/'full_synthesis.log')==capture['sha256']
 assert log.startswith('CANDIDATE_SYNTH_BEGIN version=2022.2\n')and log.rstrip().endswith('CANDIDATE_SYNTH_DONE')
 history_output=receipt['output'];excerpt=history_output.split('CANDIDATE_SYNTH_BEGIN version=2022.2\n',1)[1].split('\n\n... [Output truncated.',1)[0]
 if 'Output truncated.'in history_output:
  assert not(Counter(excerpt.splitlines()[:-1])-Counter(log.splitlines()))
  assert any(line.startswith(excerpt.splitlines()[-1])for line in log.splitlines())
 else:
  assert 'CANDIDATE_SYNTH_DONE'in history_output
  assert not(Counter(excerpt.splitlines())-Counter(log.splitlines()))
 assert not re.search(r'^(ERROR:|CRITICAL WARNING:)',log,re.M)
 assert '0 Critical Warnings and 0 Errors encountered.'in log
 checksum=re.search(r'Synth Design complete, checksum: (\w+)',log)[1]
 assert re.search(r'Violations found:\s*0\b',(out/'combinational_loops.rpt').read_text())
 timing=(out/'check_timing.rpt').read_text()
 for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:assert f'checking {label} (0)'in timing
 io={k:int(re.search(r'checking no_'+k+r'_delay \((\d+)\)',timing)[1])for k in ['input','output']}
 rpt=(out/'utilization.rpt').read_text()
 def num(k):return float(re.search(r'^\|\s*'+re.escape(k)+r'\s*\|\s*([\d.]+)\s*\|',rpt,re.M)[1])
 resources={k:num(k)for k in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs','CARRY8']};assert resources['Register as Latch']==0
 assert (out/'candidate_engine.dcp').stat().st_size>0 and (out/'timing_summary.rpt').stat().st_size>0
 summary=(out/'timing_summary.rpt').read_text()
 wns=re.search(r'^\s*WNS\(ns\).*?\n\s*[- ]+\n\s*([-+]?\d+(?:\.\d+)?)\s+',summary,re.M)
 assert wns,'Missing estimated setup summary'
 setup_slack=float(wns[1])
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','resources':resources,'checksum':checksum,'elapsed_s':receipt['elapsed_seconds'],'estimated_setup_slack_ns':setup_slack,'estimated_setup_target_met':setup_slack>=0,'hold_timing_assessed':False,'combinational_loop_violations':0,'io_without_delay':io,'warnings':dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),'auditor_sha256':sha(Path(__file__)),'scope':'Actual default candidate children/metadata/access/coordinates/pager/owner integrated OOC netlist; internal max/setup constraints inspected; hold not assessed, IO platform delay/clock location and routed/board timing absent; no cost/frontier/full search or acceleration proof.'}
 result['artifacts']={str(p.relative_to(out)):sha(p)for p in sorted(out.rglob('*'))if p.is_file()and p.name not in ['final_audit.json','audit.stdout.log']}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='artifacts'},indent=2))
if __name__=='__main__':main()
