"""Matched OOC area and routed internal timing; never infer board Fmax."""
from pathlib import Path
import json,hashlib,re,csv,sys,io
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def utilization(p):
 s=p.read_text();r={}
 for name,key in [('CLB LUTs*','LUT'),('CLB Registers','FF'),('CARRY8','CARRY8'),('Block RAM Tile','BRAM'),('DSPs','DSP'),('Register as Latch','latches')]:
  mm=re.search(r'^\|\s*'+re.escape(name).replace(r'\*',r'\*?')+r'\s*\|\s*([0-9.]+)\s*\|',s,re.M);assert mm,(p,name);r[key]=float(mm[1])
 assert r['latches']==0
 return r
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='prepared'
 for n,h in m['sources'].items():assert sha(p/n)==h
 assert sha(p/'run.tcl')==m['runner_sha256'] and sha(p/'prepare_parent_physical.py')==m['preparer_sha256']
 for name,path in [('baseline',ROOT/'results/natural_query_rtl_v1'),('cached',ROOT/'results/parent_upstream_query_v2')]:
  assert sha(path/'source_bound_audit.json')==m['dependencies'][name]
  assert sha(p/'sources'/name/'postprev_inputs.sv')==sha(path/'sources/postprev/postprev_inputs.sv')
  for f in (p/'sources/center').iterdir():assert sha(f)==sha(path/'sources/center'/f.name)
 assert 'PARENT_PHYSICAL_PAIR_DONE'in(p/'milestones.txt').read_text()
 cases={}
 for name in ['baseline','cached']:
  d=p/name;done=(d/'completed.txt').read_text();assert f'PARENT_PHYSICAL_VARIANT_DONE {name} version=2022.2 part=xcu280-fsvh2892-2L-e period=10.000'in done or f'PARENT_PHYSICAL_VARIANT_DONE {name} version=2022.2 part=xcu280-fsvh2892-2L-e period=10.0'in done
  assert (d/'research_clock.xdc').read_text()=='create_clock -name research_clock -period 10.000 [get_ports clk]\n'
  for n in ['constraints_synth.xdc','constraints_routed.xdc']:
   c=(d/n).read_text();assert 'create_clock -period 10.000 -name research_clock'in c and 'set_input_delay'not in c and 'set_output_delay'not in c and 'set_false_path'not in c
  route=(d/'route_status.rpt').read_text();nums={}
  for label in ['routable nets','fully routed nets','nets with routing errors']:
   match=re.search(r'# of '+label+r'\.*\s*:\s*(\d+)',route);assert match,label;nums[label]=int(match[1])
  assert nums['routable nets']==nums['fully routed nets'] and nums['nets with routing errors']==0
  assert re.search(r'Violations found:\s*0',(d/'drc_routed.rpt').read_text())
  timing=(d/'timing_routed.rpt').read_text();assert 'Fully Routed'in timing and 'xcu280-fsvh2892-2L-e'in timing
  for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:assert re.search(r'checking '+label+r' \(0\)',timing),label
  paths=list(csv.DictReader(io.StringIO((d/'internal_paths.tsv').read_text().replace('\\t','\t')),delimiter='\t'));assert len(paths)==20
  maxp=[x for x in paths if x['delay_type']=='max'];minp=[x for x in paths if x['delay_type']=='min'];assert len(maxp)==len(minp)==10
  assert all(float(x['requirement_ns'])==10 for x in maxp)and all(float(x['requirement_ns'])==0 for x in minp)
  setup=min(float(x['slack_ns'])for x in maxp);hold=min(float(x['slack_ns'])for x in minp)
  summary=None
  for line in timing[timing.index('| Design Timing Summary'):].splitlines():
   tokens=line.split()
   if len(tokens)==12 and re.fullmatch(r'-?\d+\.\d+',tokens[0]):summary=tokens;break
  assert summary is not None
  wns,tns,whs,ths=map(float,[summary[0],summary[1],summary[4],summary[5]])
  failing={'setup':int(summary[2]),'hold':int(summary[6]),'pulse_width':int(summary[10])}
  methodology={}
  for stage in ['synth','routed']:
   s=(d/f'methodology_{stage}.rpt').read_text();rows=re.findall(r'^\|\s*([A-Z]+-\d+)\s*\|\s*([^|]+)\|[^|]+\|\s*(\d+)\s*\|',s,re.M);assert rows
   methodology[stage]={rule:dict(severity=severity.strip(),count=int(n))for rule,severity,n in rows};assert 'TIMING-18'in methodology[stage]
  cases[name]=dict(synth=utilization(d/'utilization_synth.rpt'),routed=utilization(d/'utilization_routed.rpt'),sampled_internal_setup_slack_ns=setup,sampled_internal_hold_slack_ns=hold,reported_WNS_ns=wns,reported_TNS_ns=tns,reported_WHS_ns=whs,reported_THS_ns=ths,failing_endpoints=failing,constrained_internal_10ns_setup_hold_met=setup>=0 and hold>=0 and wns>=0 and whs>=0 and all(v==0 for v in failing.values()),methodology=methodology,unconstrained_IO_checks={k:int(re.search(r'checking '+k+r' \((\d+)\)',timing)[1])for k in ['no_input_delay','no_output_delay']},route=nums,worst_setup=maxp[0],worst_hold=minp[0],routed_dcp_sha256=sha(d/'routed.dcp'))
 assert (p/'baseline/research_clock.xdc').read_bytes()==(p/'cached/research_clock.xdc').read_bytes()
 m['status']='passed';m['artifacts']={str(q.relative_to(p)):sha(q)for q in p.rglob('*')if q.is_file()and q.suffix in ['.dcp','.rpt','.xdc','.tsv','.txt']};(p/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 a=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),cases=cases,delta={stage:{k:cases['cached'][stage][k]-cases['baseline'][stage][k]for k in cases['baseline'][stage]}for stage in ['synth','routed']},scope=m['scope'],limitations=['Module-only OOC, identical 10ns clock; no board input/output delays or HD.CLK_SRC constraint.','Sampled internal paths and full timing-summary minima reported separately; no whole-accelerator or board Fmax.','Single default placement/routing per netlist, no seed/voltage/frequency sweep; no new post-route functional simulation.'])
 (p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
if __name__=='__main__':main()
