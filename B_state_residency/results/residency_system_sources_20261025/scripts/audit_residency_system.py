"""Bind extracted hardware to independently audited, byte-identical complete executions."""
from pathlib import Path
import json,hashlib,sys,importlib.util,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def digest(v):return v['sha256']if isinstance(v,dict)else v
def main():
 out=Path(sys.argv[1]).resolve();kind=sys.argv[2];names={'normal':'transaction_fence_normal_rtl_v1','dependent':'transaction_fence_normal_dependent_rtl_v1','fault':'transaction_fence_static_join_rtl_v1'};base=ROOT/'results'/names[kind]
 m=json.loads((out/'manifest.json').read_text());bm=json.loads((base/'manifest.json').read_text());a=json.loads((base/'source_bound_audit.json').read_text())
 assert m['status']==bm['status']==a['status']=='passed'
 assert a['manifest_sha256']==sha(base/'manifest.json')
 same=0
 for n,v in m['sources'].items():
  p=out/'sources'/n;assert sha(p)==digest(v)
  if n.startswith('tb_') or n in ['runner.py','residency_system.sv']:continue
  assert n in bm['sources'] and digest(v)==digest(bm['sources'][n]);assert sha(base/'sources'/n)==digest(bm['sources'][n]);same+=1
 builder=ROOT/'hardware/variants/residency_system_v1/build.py';sp=importlib.util.spec_from_file_location('system_builder',builder);b=importlib.util.module_from_spec(sp);sp.loader.exec_module(b);expected,interface,meta=b.make()
 assert expected.encode()==(out/'sources/residency_system.sv').read_bytes()
 assert b.bench(kind).encode()==(out/'sources'/('tb_system_'+kind+'.sv')).read_bytes()
 if kind=='normal':assert '.ENABLE_TEST_INJECTION(0)' in b.bench(kind)
 if kind=='fault':assert b.bench(kind).count('snapshot capture ')==6 and 'snapshot_test_design=~snapshot_test_design;' in b.bench(kind)
 assert len(meta['instances'])==13 and len(interface)==313
 assert not re.search(r'\$(?:fopen|fread|fscanf|fdisplay|finish|fatal)|\b(?:initial|force|release)\b',expected)
 assert 'ENABLE_TEST_INJECTION=0' in expected
 assert not re.search(r"\b(?:65185|150697|9089009|2717|328)\b",expected)
 assert all(n in interface for n in ['recover_checkpoint','recover_version','snapshot_count','snapshot_nodes','snapshot_probe','snapshot_design','snapshot_checkpoint','snapshot_cookie','lr_s_cookie'])
 assert sha(out/'sources/runner.py')==sha(ROOT/'scripts'/('run_residency_system_'+kind+'.py'))
 for n,v in m.get('scoreboards',{}).items():assert sha(out/n)==v==bm['scoreboards'][n]
 assert set(m['cases'])==set(bm['cases'])
 if kind=='fault':assert all(c['exit_code']==0 for c in m['commands']) and len(m['commands'])==4
 cases={}
 compared=['natural_trace.txt']+[n+'_axi.txt'for n in ['graph','design','label','owner','cost','qstate','table']]+['design.bin','owners.bin','labels.bin','cost.bin']
 for case,c in m['cases'].items():
  assert c['status']=='passed'and all(x['exit_code']==0 for x in c['commands'])
  assert c['result']==bm['cases'][case]['result']
  for n,h in c['artifacts'].items():assert sha(out/case/n)==h
  hashes={}
  for n in compared:
   oldhash=sha(base/case/n);assert oldhash==bm['cases'][case]['artifacts'][n]
   newhash=sha(out/case/n);assert newhash==oldhash,(case,n)
   hashes[n]=newhash
  log=(out/case/'simulate.log').read_text();assert c['result']in log and '$finish called'in log and 'Fatal:'not in log
  cases[case]={'result':c['result'],'byte_identical':hashes}
 result=dict(status='passed',kind=kind,manifest_sha256=sha(out/'manifest.json'),auditor_sha256=sha(Path(__file__)),builder_sha256=sha(builder),reference_audit_sha256=sha(base/'source_bound_audit.json'),reference_manifest_sha256=sha(base/'manifest.json'),unchanged_source_files=same,structural_instances=meta['instances'],top_ports=interface,cases=cases,scope='Full trace cycle/payload and all seven AXI logs/four complete images byte-identical to independent CPU/memory/protocol audited reference; structural extraction plus latched external recovery snapshot metadata. TB search/authority/snapshot producer remain; no arbitrary-write recovery or board claim.')
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','kind':kind,'cases':list(cases),'unchanged_sources':same}))
if __name__=='__main__':main()
