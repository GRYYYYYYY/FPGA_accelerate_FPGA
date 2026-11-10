from pathlib import Path
import hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();kind=sys.argv[2];assert kind in ['static','sparse'];variant='search_static_v2'if kind=='static'else'search_sparse_v3';checks=69632 if kind=='static'else 17420
 m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'and len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
 for n,h in m['sources'].items():
  assert sha(out/'sources'/n)==h
  if n=='reference.sv':assert (out/'sources'/n).read_text()==(ROOT/'hardware/variants/search_scheduler_v1/search_host_fence.sv').read_text().replace('module search_host_fence(', 'module search_host_fence_reference(')
  else:assert sha(ROOT/('scripts'if n.startswith('run_')else'hardware/variants/'+variant)/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 for builder,target in [('build.py','search_host_fence.sv'),('build_miter.py','tb_search_mux_equivalence.sv')]:
  p=ROOT/'hardware/variants'/variant/builder;sp=importlib.util.spec_from_file_location('builder',p);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);assert b.make().encode()==(out/'sources'/target).read_bytes()
 log=(out/'simulate.log').read_text();label='SEARCH_MUX_EQUIVALENCE_PASS'if kind=='static'else'SEARCH_SPARSE_EQUIVALENCE_PASS';assert label+' checks='+str(checks)in log and 'Fatal:'not in log and '$finish called'in log
 result=dict(status='passed',manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),kind=kind,checks=checks,scope=m['scope'],reference_source_sha256=sha(ROOT/'hardware/variants/search_scheduler_v1/search_host_fence.sv'))
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','kind':kind,'checks':checks}))
if __name__=='__main__':main()
