"""Reexecute original audit assertions against recovered bytes, never solvers or output writers."""
from pathlib import Path as RealPath
import ast,json,sys,subprocess,hashlib,datetime
R=RealPath(__file__).resolve().parents[2];V=RealPath('/tmp/B_state_residency_recovery_20261102/ka_dependency_review_view_v1');OLD='/tmp/B_state_residency_offer_20261025'
class MappedPath(type(RealPath())):
 def __new__(cls,*args,**kwargs):
  p=RealPath(*args,**kwargs);s=str(p)
  if s==OLD or s.startswith(OLD+'/'):p=V/s[len(OLD):].lstrip('/')
  return super().__new__(cls,p)
def sha(p):return hashlib.sha256(RealPath(p).read_bytes()).hexdigest()
def one(source):
 s=source.read_text();tree=ast.parse(s);kept=[]
 for node in tree.body:
  if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cap' for t in node.targets):break
  kept.append(node)
 else:raise AssertionError('No explicit evidence-writing boundary')
 for node in kept:
  if isinstance(node,ast.ImportFrom) and node.module=='pathlib':node.module='pathlib'
 # Preserve the exact assertion AST; only replace the imported Path name.
 tree.body=kept
 code=ast.unparse(tree).replace('from pathlib import Path','from __main__ import MappedPath as Path')
 def readonly(event,args):
  if event=='open':
   mode=args[1];flags=args[2]
   assert not (isinstance(mode,str) and any(x in mode for x in 'wax+')),('write forbidden',args[:2])
   assert not (isinstance(flags,int) and flags & (1|2|64|512|1024)),('write flags forbidden',args[:2])
  assert event not in ['os.mkdir','os.remove','os.rename','os.rmdir','os.symlink','subprocess.Popen','os.system'],('mutation forbidden',event)
 sys.addaudithook(readonly)
 ns={'__file__':str(source),'__name__':'restored_readonly_audit'}
 exec(compile(code,str(source),'exec'),ns)
 print(json.dumps(dict(status='original_assertions_passed_readonly',source_sha256=sha(source),assertion_nodes=sum(isinstance(x,ast.Assert) for x in ast.walk(tree)),executed_prefix_ast_sha256=hashlib.sha256(ast.dump(tree).encode()).hexdigest())))
def main():
 if len(sys.argv)>1 and sys.argv[1]=='--one':one(RealPath(sys.argv[2]));return
 rec=json.loads((R/'results/shadow_ka_dependency_actual_restore_20261102.json').read_text())
 scripts={sha(p):p for p in (R/'scripts/research_checks').glob('*.py')}
 selected={}
 for n,a in rec['archives'].items():
  r=json.loads((R/'results'/n).read_text());digest=r.get('reviewer_sha256') or r.get('file_sha256',{}).get('reviewer.py')
  if digest and digest in scripts:selected[n]=scripts[digest]
 out=R/'results/shadow_ka_readonly_reaudit_v1_20261102.json';assert not out.exists();logs=R/'results/shadow_ka_readonly_reaudit_v1_logs';logs.mkdir()
 rows={}
 for name,source in selected.items():
  proc=subprocess.run([sys.executable,'-B',str(RealPath(__file__)), '--one',str(source)],capture_output=True,text=True)
  log=logs/(source.stem+'.log');log.write_text(proc.stdout+proc.stderr)
  rows[name]=dict(source=str(source),source_sha256=sha(source),exit_code=proc.returncode,log=str(log),log_sha256=sha(log))
  if proc.returncode==0:rows[name]['receipt']=json.loads(proc.stdout)
  print(name,proc.returncode,flush=True)
 out.write_text(json.dumps(dict(status='read_only_audit_attempts_recorded',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),rows=rows,passed=sum(x['exit_code']==0 for x in rows.values()),total=len(rows),tool_sha256=sha(RealPath(__file__)),scope='Exact original audit-prefix assertions; only Path reads remapped. Artifact-writing tails excluded explicitly. No solver runs or original verdict rewrites.'),indent=2)+'\n')
if __name__=='__main__':main()
