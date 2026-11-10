from pathlib import Path
import hashlib,json,sys,importlib.util
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,v in m['sources'].items():assert sha(out/'sources'/n)==v['sha256']==sha(Path(v['path']))
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert sha(out/'runner.py')==m['runner_sha256'] and all(c['exit_code']==0 for c in m['commands']) and len(m['commands'])==3
 p=ROOT/'hardware/variants/recursive_controller_v1/derive_controller.py';spec=importlib.util.spec_from_file_location('derive_rec',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 assert mod.derive((ROOT/'hardware/variants/candidate_pipeline_v1/candidate_controller.sv').read_text())==(out/'sources/recursive_candidate_controller.sv').read_text()
 for n in ['children_frames.sv','expansion_capture.sv']:assert sha(out/'sources'/n)==sha(ROOT/'results/expansion_capture_20261025/sources/capture'/n)
 expected=[];summaries=[]
 for scenario in range(5):
  seen=set();counter=100;early=False;calls=decisions=depth=0
  def kids(node):
   if scenario==4:return []
   if scenario==3:return [node+1]if node<8 else[]
   if node==0:return[1,2]
   if node==1:return[3]if scenario==1 else[2]
   if scenario==1 and node==3:return[2]
   return[]
  def expand(parent,level,cookie):
   nonlocal counter,early,calls,decisions,depth
   calls+=1;depth=max(depth,level);expected.append(f'E {scenario} {cookie} {parent}')
   for node in kids(parent):
    if early:break
    expected.append(f'M {scenario} {cookie} {parent} {node}')
    old=int(node in seen);expected.append(f'R {scenario} {parent} {node} {old}')
    if old:action=0
    elif scenario==2 and node==2:action=1;early=True
    else:action=2 if scenario==3 or parent==0 or(scenario==1 and node==3)else 1
    expected.append(f'O {scenario} {cookie} {parent} {node} {action}');decisions+=1
    if action:seen.add(node)
    if action==2:counter+=1;expand(node,level+1,counter)
  expand(0,1,100);summaries.append(f'CASE {scenario} PASS decisions={decisions} expansions={calls} depth={depth} early={int(early)}')
 log=(out/'simulate.log').read_text();events=[l for l in log.splitlines()if l.startswith(('E ','M ','R ','O '))];assert events==expected
 assert [l for l in log.splitlines()if l.startswith('CASE ')]==summaries
 assert 'RECURSIVE_CONTROLLER_PASS cases=5'in log and 'Fatal:'not in log
 cpu=ROOT/'results/recursion_order_20261025';ca=json.loads((cpu/'source_bound_audit.json').read_text());assert ca['status']=='passed' and ca['manifest_sha256']==sha(cpu/'manifest.json')
 assert 'R 0 0 2 1'in events and 'O 0 100 0 2 0'in events
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'derive_sha256':sha(p),'original_controller_sha256':sha(ROOT/'hardware/variants/candidate_pipeline_v1/candidate_controller.sv'),'cpu_counterexample_audit_sha256':sha(cpu/'source_bound_audit.json'),'summaries':summaries,'events':len(events),'scope':'Actual frame/capture/recursive controller RTL, mock graph/metadata/access/label-commit callback. Fresh mock visited decision after subtree; not actual native label, geometry/cost, queue or joined recovery.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
