"""Index the actual worst setup path without claiming placed/routed performance."""
from pathlib import Path
from collections import Counter,defaultdict
import json,re
from run_checkpoint_authority import ROOT,sha

base=Path('/tmp/B_state_residency_offer_20261025')
gate=json.loads((base/'checkpoint_edit_synth_followup_v1/manifest.json').read_text())
assert gate['status']=='observed'and gate['stage']=='complete','wait for actual restoration/freeze; do not read a restoring root'
p=base/'checkpoint_edit_synth_v1'
m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
rp=ROOT/'results/checkpoint_edit_synth_v1_restore_20261025.json';r=json.loads(rp.read_text())
assert m['status']=='observed'and a['status']==r['status']=='passed'and r['audit_byte_identical']
assert a['manifest_sha256']==sha(p/'manifest.json')and r['audit_sha256']==sha(p/'source_bound_audit.json')
assert a['check_timing_counts']['loops']==0 and not a['timing_loop_warnings'],'resolve loops before interpreting path timing'
report=p/'timing_synth.rpt';assert sha(report)==a['artifact_sha256'][report.name]
s=report.read_text();starts=list(re.finditer(r'^Slack \(',s,re.M));assert starts
block=s[starts[0].start():starts[1].start()if len(starts)>1 else len(s)]
def field(pattern):
    x=re.search(pattern,block,re.M);assert x,pattern;return x
slack=float(field(r'^Slack \([^)]+\)\s*:\s*(-?[\d.]+)ns')[1])
source=field(r'^\s+Source:\s+(\S+)')[1]
destination=field(r'^\s+Destination:\s+(\S+)')[1]
delay=field(r'Data Path Delay:\s+([\d.]+)ns\s+\(logic\s+([\d.]+)ns.*?route\s+([\d.]+)ns')
levels=field(r'Logic Levels:\s+(\d+)\s+\(([^)]+)\)')
declared={name:int(count)for name,count in re.findall(r'(LUT\d)=(\d+)',levels[2])}
luts=[]
for x in re.finditer(r'^\s+(LUT[1-6])\s+\(Prop_[^)]+\)\s+([\d.]+)\s+([\d.]+)\s+([rf])\s+(\S+)\s*$',block,re.M):
    luts.append(dict(type=x[1],delay_ns=float(x[2]),arrival_ns=float(x[3]),edge=x[4],pin=x[5],cell=x[5].rsplit('/',1)[0]))
assert len(luts)==int(levels[1])and dict(Counter(x['type']for x in luts))==declared
nets=[]
for x in re.finditer(r'^\s+net \(fo=(\d+), ([^)]+)\)\s+([\d.]+)\s+([\d.]+)\s+(\S+)\s*$',block,re.M):
    nets.append(dict(fanout=int(x[1]),placement=x[2],delay_ns=float(x[3]),arrival_ns=float(x[4]),name=x[5]))
unplaced=[n for n in nets if n['placement']=='unplaced']
assert unplaced and abs(sum(n['delay_ns']for n in unplaced)-float(delay[3]))<0.02
groups=defaultdict(lambda:dict(levels=0,logic_delay_ns=0.0))
segments=[]
for lut in luts:
    hierarchy=lut['cell'].rsplit('/',1)[0]
    groups[hierarchy]['levels']+=1;groups[hierarchy]['logic_delay_ns']+=lut['delay_ns']
    if not segments or segments[-1]['hierarchy']!=hierarchy:segments.append(dict(hierarchy=hierarchy,levels=0))
    segments[-1]['levels']+=1
assert slack==a['preplacement_wns_ns']
result=dict(status='source_bound_worst_setup_path_navigation',analyzer_sha256=sha(Path(__file__)),
    audit_sha256=sha(p/'source_bound_audit.json'),restore_receipt_sha256=sha(rp),report_sha256=sha(report),
    source=source,destination=destination,slack_ns=slack,data_delay_ns=float(delay[1]),
    logic_delay_ns=float(delay[2]),estimated_net_delay_ns=float(delay[3]),logic_levels=len(luts),
    primitive_counts=declared,luts=luts,ordered_hierarchy_segments=segments,hierarchy_totals=dict(groups),
    unplaced_data_nets=unplaced,highest_fanout_unplaced_nets=sorted(unplaced,key=lambda n:n['fanout'],reverse=True)[:10],
    scope='Literal first/worst setup path of the restored matched OOC report. Hierarchy groupings are navigation, not an RTL functional proof. Net delays are unplaced estimates; clock nets tagged unset are excluded from data-net ranking. No frequency or board-speed extrapolation.')
baseline_path=ROOT/'results/query_native_timing_path_20261028.json'
baseline=json.loads(baseline_path.read_text())
assert baseline['audit_sha256']==m['reference_audit_sha256']
result['baseline_analysis_sha256']=sha(baseline_path)
result['comparison_to_baseline']=dict(
    baseline_source=baseline['source'],baseline_destination=baseline['destination'],
    baseline_slack_ns=baseline['slack_ns'],baseline_logic_levels=baseline['logic_levels'],
    same_endpoint_names=source==baseline['source']and destination==baseline['destination'],
    slack_delta_ns=slack-baseline['slack_ns'],logic_level_delta=len(luts)-baseline['logic_levels'],
    logic_delay_delta_ns=float(delay[2])-baseline['logic_delay_ns'],
    estimated_net_delay_delta_ns=float(delay[3])-baseline['estimated_net_delay_ns'],
    scope='Comparison of each design worst reported setup path; different endpoints or cones need separate interpretation. Unplaced estimates do not establish physical frequency.')
out=ROOT/'results/checkpoint_edit_timing_path_20261028.json';assert not out.exists()
out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('CHECKPOINT_EDIT_TIMING_PATH_INDEXED',len(luts),'LUT levels',len(unplaced),'data nets','WNS',slack)
print('largest_hierarchies',sorted(groups.items(),key=lambda x:x[1]['levels'],reverse=True)[:6])
