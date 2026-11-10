"""Bind hierarchy deltas and routed path composition to audited reports."""
from pathlib import Path
import hashlib,json,re,csv
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def hierarchy(p):
 result={};stack=[]
 for line in p.read_text().splitlines():
  fields=line.split('|')[1:-1]
  if len(fields)<11:continue
  try:counts={k:int(fields[i].strip()) for k,i in [('LUT',2),('logic_LUT',3),('LUTRAM',4),('FF',6),('RAMB36',7),('RAMB18',8),('DSP',10)]}
  except ValueError:continue
  raw=fields[0];name=raw.strip()
  if name.startswith('('):continue
  level=(len(raw)-len(raw.lstrip())-1)//2
  assert 0<=level<=len(stack)
  stack=stack[:level]+[name];key='/'.join(stack[1:]) or '(top)';assert key not in result
  result[key]=counts
 return result

def paths(p,expected):
 text=p.read_text().split('Max Delay Paths',1)[1].split('Min Delay Paths',1)[0];rows=[]
 for block in re.split(r'(?=Slack \((?:MET|VIOLATED)\))',text)[1:]:
  m=re.search(r'Data Path Delay:\s+([\d.]+)ns\s+\(logic ([\d.]+)ns.*?route ([\d.]+)ns',block)
  if not m:continue
  row={'source':re.search(r'Source:\s+(\S+)',block)[1],'destination':re.search(r'Destination:\s+(\S+)',block)[1],'delay_ns':float(m[1]),'logic_ns':float(m[2]),'route_ns':float(m[3]),'logic_levels':int(re.search(r'Logic Levels:\s+(\d+)',block)[1])};row['route_fraction']=row['route_ns']/row['delay_ns'];rows.append(row)
 expected=[x for x in expected if x['delay_type']=='max'];assert len(rows)==len(expected)==10
 for row,e in zip(rows,expected):assert row['source']==e['startpoint'] and row['destination']==e['endpoint'] and abs(row['delay_ns']-float(e['datapath_delay_ns']))<.0011
 return rows

def main():
 out=ROOT/'results/record_response_cost_analysis_20261024';out.mkdir()
 cs=ROOT/'results/record_response_synthesis_20261024';bs=ROOT/'results/rtl_small_endpoint_synthesis_20261023'
 cr=ROOT/'results/record_response_timing_20261024';br=ROOT/'results/rtl_small_codec_endpoint_timing_20261023'
 ca=json.loads((cs/'final_audit.json').read_text());ba=json.loads((bs/'final_audit.json').read_text());ra=json.loads((cr/'final_audit.json').read_text());rb=json.loads((br/'final_manifest.json').read_text())
 assert ca['status']==ba['status']=='synthesis_evidence_verified' and ra['status']=='evidence_verified' and rb['audit_status']=='evidence_verified'
 binding={str(p):sha(p) for p in [cs/'final_audit.json',bs/'final_audit.json',cr/'final_audit.json',br/'final_manifest.json']}
 result={'status':'verified_report_extraction','inputs':binding,'stages':{},'paths':{},'source_sha256':sha(Path(__file__)),'scope':'hierarchy counts can share packed LUTs and are not additive; mapping changes are not isolated RTL operator costs. One routed run per configuration; no causal attribution, Fmax or benefit prediction.'}
 rows=[]
 for stage,old,new,old_hash,new_hash in [('synth',bs/'utilization_hierarchical.rpt',cs/'utilization_hierarchical.rpt',ba['artifacts']['utilization_hierarchical.rpt'],ca['artifacts']['utilization_hierarchical.rpt']),('routed',br/'dynamic/utilization_hierarchical.rpt',cr/'utilization_hierarchical.rpt',rb['artifacts']['dynamic/utilization_hierarchical.rpt'],ra['artifacts']['utilization_hierarchical.rpt'])]:
  assert sha(old)==old_hash and sha(new)==new_hash;binding[str(old)]=old_hash;binding[str(new)]=new_hash
  o,n=hierarchy(old),hierarchy(new);assert o.keys()==n.keys()
  result['stages'][stage]={}
  for key in n:
   delta={k:n[key][k]-o[key][k] for k in n[key]};result['stages'][stage][key]={'baseline':o[key],'candidate':n[key],'delta':delta}
   rows.append({'stage':stage,'hierarchy':key,**{'baseline_'+k:v for k,v in o[key].items()},**{'candidate_'+k:v for k,v in n[key].items()},**{'delta_'+k:v for k,v in delta.items()}})
 for name,p,expected,digest in [('baseline',br/'dynamic/timing_routed.rpt',rb['variants']['dynamic']['internal_paths'],rb['artifacts']['dynamic/timing_routed.rpt']),('candidate',cr/'timing_routed.rpt',ra['internal_paths'],ra['artifacts']['timing_routed.rpt'])]:
  assert sha(p)==digest;binding[str(p)]=digest;result['paths'][name]=paths(p,expected)
 assert result['stages']['synth']['(top)']['delta']['LUT']==258
 assert result['stages']['routed']['(top)']['delta']['LUT']==248
 with (out/'hierarchy.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 for stage in result['stages']:
  for key in ['(top)','pages','pages/responses','pages/endpoint','pages/work']:print(stage,key,result['stages'][stage][key]['delta'])
 for name,p in result['paths'].items():print(name,p[0])
if __name__=='__main__':main()
