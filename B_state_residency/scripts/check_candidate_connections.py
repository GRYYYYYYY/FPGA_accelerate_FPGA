"""Structural source-presence check for generated flat wiring; not functional proof."""
from pathlib import Path
import importlib.util,re,json,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
def check():
 p=ROOT/'hardware/variants/candidate_pipeline_v1/generate_top.py';spec=importlib.util.spec_from_file_location('candidate_gen',p);g=importlib.util.module_from_spec(spec);spec.loader.exec_module(g)
 rtl=p.parent/'candidate_engine.sv';text=rtl.read_text();driven=set();used=set()
 def ids(s):return set(re.findall(r'\b[a-zA-Z_]\w*\b',s))
 for direction,width,name in re.findall(r'(input|output) wire\s*(\[[^]]+\])?\s*(\w+)',text[:text.index(');')]):
  (driven if direction=='input'else used).add(name)
 for names in re.findall(r'\breg\s*(?:\[[^]]+\])?\s*([^;]+);',text):driven.update(ids(names))
 for lhs,rhs in re.findall(r'\bassign\s+(.+?)=(.+?);',text):
  driven.update(ids(re.sub(r'\[[^]]*\]','',lhs)));used.update(ids(rhs))
 for pre,path in g.paths.items():
  name={'e':'expansion','m':'metadata','a':'access','s':'dispatch','c':'coordinates','u':'owner_store','o':'owners','k':'controller'}.get(pre,pre)
  match=re.search(r'\b'+name+r'\(\n(.*?)\n\);',text,re.S);assert match,name
  for port,signal in re.findall(r'\.(\w+)\(([^()]*)\)',match.group(1)):
   (driven if g.ports(path)[port][0]=='output'else used).update(ids(signal))
 for name in ['g','d','io']:
  match=re.search(r'\b'+name+r'_arb\(\n(.*?)\n\);',text,re.S)
  for port,signal in re.findall(r'\.(\w+)\(([^()]*)\)',match.group(1)):
   (driven if port in ['c_req_ready','c_rsp_valid','c_rsp_data','b_req_valid','b_req_data','b_rsp_ready','fault','busy']else used).update(ids(signal))
 missing=sorted(used-driven);assert not missing,missing
 return {'status':'passed','scope':'flat generated source presence; not width, single-driver, sequential or functional proof','used_signals':len(used),'driven_signals':len(driven),'rtl_sha256':hashlib.sha256(rtl.read_bytes()).hexdigest()}
if __name__=='__main__':
 result=check();print(json.dumps(result,indent=2))
 if len(sys.argv)>1:Path(sys.argv[1]).write_text(json.dumps(result,indent=2)+'\n')
