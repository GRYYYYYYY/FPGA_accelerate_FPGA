"""Distinguish successful cosim execution from actual native floating arithmetic equality."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def compare(vector,observed):
 v=vector.read_text().splitlines();o=observed.read_text().splitlines();assert len(v)==len(o)
 groups={};badwords=0;examples=[]
 for idx,(vl,ol)in enumerate(zip(v,o)):
  a=vl.split();b=ol.split();group=int(a[0]);assert len(a)==29 and len(b)==7 and int(b[0])==idx and int(b[1])==group
  want=list(map(lambda x:int(x,16),a[24:]));got=list(map(lambda x:int(x,16),b[2:]));n=sum(x!=y for x,y in zip(want,got));badwords+=n
  g=groups.setdefault(group,{'cases':0,'mismatched_cases':0,'mismatched_words':0});g['cases']+=1;g['mismatched_cases']+=bool(n);g['mismatched_words']+=n
  if n and len(examples)<16:examples.append({'case':idx,'group':group,'expected':a[24:],'actual':b[2:]})
 return groups,badwords,examples

def main():
 out=ROOT/'results/search_cost_native_hls_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='characterized'
 assert sha(Path(__file__).parent/'run_search_cost_hls.py')==m['runner_sha256']==sha(out/'runner.py')
 for n,d in m['sources'].items():assert sha(out/'sources'/n)==d==sha(ROOT/'hardware/hls/search_cost/native_v1'/n)
 for n,d in m['generated_rtl_artifacts'].items():assert sha(out/n)==d
 for n,d in m['observations'].items():assert sha(out/n)==d
 assert sha(out/'vectors.txt')==m['vectors_sha256'] and sha(out/'run_hls.tcl')==m['tcl_sha256']
 assert all(c['exit_code']==0 for c in m['commands']) and sha(out/'hls.log')==m['flow_log_sha256']
 assert 'COST_HLS_DONE' in (out/'hls.log').read_text()
 c,cb,_=compare(out/'vectors.txt',out/'csim_observed.txt');assert cb==0
 groups,words,examples=compare(out/'vectors.txt',out/'cost_step/solution1/sim/wrapc_pc/observed.txt')
 assert sum(g['mismatched_cases']for g in groups.values())==158 and words==331 and groups[0]['mismatched_cases']==0
 r={'status':'characterized','rtl_bit_exact':False,'integration_gate':'failed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'csim_mismatched_words':cb,'rtl_groups':groups,'rtl_mismatched_words':words,'examples':examples,'scope':'Cosim PASS means the characterization test completed. Actual scalar outputs differ from frozen host IEEE oracle; cannot substitute this native float block as bit-identical.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'numerical_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items()if k!='examples'},indent=2))
if __name__=='__main__':main()
