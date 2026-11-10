from pathlib import Path
import hashlib,json,shutil,subprocess,time,os
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 graph=ROOT/'results/graph_image_20261024';out=ROOT/'results/expansion_inputs_20261024';out.mkdir();src=out/'sources';src.mkdir()
 gate=json.loads((graph/'source_bound_audit.json').read_text());assert gate['status']=='passed'and gate['manifest_sha256']==sha(graph/'manifest.json')
 shutil.copytree(graph/'reference',src/'reference');s=(src/'reference/trace.cpp').read_text()
 edits=[('void getOrCreate(int id) { created[id] = 1; }','void getOrCreate(int id) { created[id] = 1; note_create(id); }',1),('int child = childIds[n.childStart + k];','int child = childIds[n.childStart + k]; note_position(k);',1),('out->push_back(child);','out->push_back(child); note_emit(child);',2)]
 for old,new,count in edits:assert s.count(old)==count;s=s.replace(old,new)
 (src/'reference/oracle_trace.cpp').write_text(s)
 shutil.copyfile(ROOT/'hardware/variants/expansion_v1/make_inputs.cpp',src/'make_inputs.cpp');shutil.copyfile(__file__,src/'runner.py')
 m={'status':'running','pid':os.getpid(),'graph_manifest_sha256':sha(graph/'manifest.json'),'graph_audit_sha256':sha(graph/'source_bound_audit.json'),'sources':{str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for stage,args in [('compile',['g++','-std=c++17','-O2','-fno-fast-math','-pthread','-I'+str(src/'reference'),'-I'+str(src/'reference/include'),str(src/'make_inputs.cpp'),'-o',str(out/'make_inputs')]),('execute',[str(out/'make_inputs'),str(ROOT/'data/derived/logicnets_jscl.rrt'),str(out)])]:
   t=time.monotonic();row={'stage':stage,'argv':args};m['commands'].append(row);save()
   with (out/(stage+'.log')).open('w')as f:
    p=subprocess.Popen(args,stdout=f,stderr=subprocess.STDOUT,cwd=out);row['pid']=p.pid;save();row['exit_code']=p.wait();row['elapsed_s']=time.monotonic()-t;save();assert row['exit_code']==0
  assert 'EXPANSION_INPUTS_PASS 'in(out/'execute.log').read_text()
  m['artifacts']={p.name:sha(p)for p in out.iterdir()if p.is_file()and p.name!='manifest.json'};m['status']='passed';save();print((out/'coverage.json').read_text())
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
