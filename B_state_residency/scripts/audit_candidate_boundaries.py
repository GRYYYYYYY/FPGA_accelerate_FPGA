from pathlib import Path
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,spec in m['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 for p,digest in m['gates'].items():assert sha(Path(p))==digest
 control=ROOT/'results/candidate_control_boundaries_v2_20261024';assert sha(out/'sources/candidate/candidate_controller.sv')==sha(control/'sources/candidate_controller.sv')
 counts={}
 for case,cm in m['cases'].items():
  assert cm['status']=='passed'and all(c['exit_code']==0 for c in cm['commands']);d=out/case
  for name,digest in cm['artifacts'].items():assert sha(d/name)==digest
  log=(d/'simulate.log').read_text();assert 'Fatal:'not in log and '$finish called'in log and cm['result']in log
  count={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',cm['result'])};assert count['mode']==(case=='graph_r')and count['owner_writes']==0
  responses=[line.split()for line in(d/'graph_axi.txt').read_text().splitlines()if line.startswith('R ')]
  errs=sum(r[3]!='0'for r in responses);assert errs==(case=='graph_r')
  original=ROOT/'results/candidate_initial_owner_20261024/owners.bin';assert sha(d/'owners.bin')==sha(original)
  count['graph_R_errors']=errs;counts[case]=count
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'counts':counts,'scope':'Actual shared candidate stack: metadata graph AR held across abort, retained AR payload and drain before manual error retirement; actual graph R error. Owner backing unchanged. No recovery/reload or other AXI fault types covered here.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
