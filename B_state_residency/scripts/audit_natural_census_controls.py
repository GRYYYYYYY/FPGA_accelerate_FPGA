from pathlib import Path
import hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();base=Path(sys.argv[2]).resolve();m=json.loads((out/'manifest.json').read_text());bm=json.loads((base/'manifest.json').read_text());assert m['status']==bm['status']=='passed'and m['base_manifest_sha256']==sha(base/'manifest.json')
 assert m['control_sha256']==sha(out/'control.cpp')and m['runner_sha256']==sha(out/'runner.py')
 for n,h in m['artifacts'].items():assert sha(out/n)==h,n
 assert all(c['exit_code']==0 for c in m['commands'])and len(m['commands'])==3
 for n,h in m['base_sources'].items():assert sha(base/'sources'/n)==h==bm['sources'][n]
 p=ROOT/'adapters/recursive_census_v1/make_control.py';spec=importlib.util.spec_from_file_location('control_der',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 assert mod.derive((ROOT/'results/recursion_order_20261025/sources/case.cpp').read_text())==(out/'control.cpp').read_text()
 rows={}
 for mode in ['positive','negative']:
  a=(out/(mode+'.txt')).read_text().splitlines();assert len(a)==2;v=dict(zip(a[0].split(),map(int,a[1].split())));assert v==m[mode];rows[mode]=v
 p,n=rows['positive'],rows['negative'];assert [p[k]for k in ['expansions','pushes','lookahead','lookahead_with_siblings','max_depth','first_parent','first_child','first_position','first_remaining','first_degree']]==[2,2,1,1,2,0,1,0,1,2]
 assert [n[k]for k in ['expansions','pushes','lookahead','lookahead_with_siblings','max_depth']]==[1,2,0,0,1]
 ref=(ROOT/'results/recursion_order_20261025/immediate_execute.log').read_text().splitlines();assert [l for l in(out/'positive.log').read_text().splitlines()if not l.startswith('RECURSION_CENSUS_FINISHED')]==[l for l in ref if l.startswith(('L ','Q ','RECURSION_ORDER_CASE_FINISHED'))]
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'control_derive_sha256':sha(ROOT/'adapters/recursive_census_v1/make_control.py'),'base_manifest_sha256':sha(base/'manifest.json'),'positive':p,'negative':n,'scope':'Same instrumented original Router methods and observer header: synthetic Laguna-positive versus non-Laguna-negative control, no natural-design recursion claim.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('NATURAL_CENSUS_CONTROLS_AUDITED')
if __name__=='__main__':main()
