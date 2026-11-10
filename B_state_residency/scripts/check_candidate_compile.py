"""Freeze and elaborate the candidate integration; this is not a functional test."""
from pathlib import Path
import hashlib,json,subprocess,sys,re,shutil
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
 files=[];modules={};sources={}
 def add(p,name):
  text=p.read_text();names=re.findall(r'^\s*module\s+(\w+)',text,re.M)
  if not names:return
  overlap=set(names)&modules.keys()
  if overlap:
   assert all(modules[n]==hashlib.sha256(text.encode()).hexdigest()for n in overlap),(p,overlap)
   return
  q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);digest=hashlib.sha256(q.read_bytes()).hexdigest()
  for n in names:modules[n]=digest
  files.append(str(q));sources[name]={'path':str(p),'sha256':digest}
 for dep in ['expansion_20261024','access_owner_v3_20261024']:
  base=ROOT/'results'/dep;m=json.loads((base/'manifest.json').read_text());assert m['status']=='passed'
  for name in m['rtl']:
   if Path(name).name.startswith('tb_') or Path(name).name in ['axi_file_memory.sv','node_expansion_engine.sv','access_fabric.sv']:continue
   add(base/'sources'/name,dep+'/'+name)
 for p in sorted((ROOT/'hardware/variants/metadata_v1').glob('metadata_controller.sv')):add(p,'metadata/'+p.name)
 for p in sorted((ROOT/'hardware/variants/candidate_pipeline_v1').glob('*.sv')):add(p,'candidate/'+p.name)
 shutil.copyfile(__file__,src/'runner.py')
 m={'status':'running','scope':'compile and elaboration only; no functional simulation','sources':sources,'rtl':files,'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 for stage,argv in [('compile',[str(BIN/'xvlog'),'--sv']+files),('elaborate',[str(BIN/'xelab'),'candidate_engine','-s','candidate','--mt','2'])]:
  with (out/(stage+'.log')).open('w')as log:code=subprocess.call(argv,cwd=out,stdout=log,stderr=subprocess.STDOUT)
  m['commands'].append({'stage':stage,'argv':argv,'exit_code':code});save()
  if code:m['status']='failed';save();raise RuntimeError(stage)
 m['status']='passed';save();print('CANDIDATE_ELABORATION_PASS modules='+str(len(modules)),flush=True)
if __name__=='__main__':main()
