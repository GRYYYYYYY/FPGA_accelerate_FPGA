"""Freeze the tested candidate revision and validate its functional/fault gates."""
from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();assert not out.exists();revision=ROOT/'results/candidate_revision_20261025.json';r=json.loads(revision.read_text());assert r['status']=='passed';gates={}
 for name,spec in r['gates'].items():
  dep=ROOT/'results'/name;m=json.loads((dep/'manifest.json').read_text());a=json.loads((dep/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'
  assert sha(dep/'manifest.json')==spec['manifest_sha256']==a['manifest_sha256']and sha(dep/'source_bound_audit.json')==spec['audit_sha256']
  gates[name]=spec
 sim=ROOT/'results/candidate_pipeline_v2_20261024';m=json.loads((sim/'manifest.json').read_text())
 for name,spec in m['sources'].items():assert sha(sim/'sources'/name)==spec['sha256']==sha(Path(spec['path']))
 ctrl=sim/'sources/candidate/candidate_controller.sv';assert sha(ctrl)==r['controller_sha256']
 out.mkdir();shutil.copytree(sim/'sources',out/'sources');shutil.copyfile(revision,out/'revision.json')
 for name in gates:shutil.copyfile(ROOT/'results'/name/'source_bound_audit.json',out/(name+'_audit.json'))
 rtl=[n for n in m['rtl']if not Path(n).name.startswith('tb_')and Path(n).name!='axi_file_memory.sv']
 assert len(rtl)==52
 manifest={'status':'prepared','top':'candidate_engine','part':'xcu280-fsvh2892-2L-e','clock_period_ns':10,'parameters':'all RTL defaults: SLOTS32 FRAMES163840 INDEX18 HASH18','sources':m['sources'],'rtl':rtl,'gates':gates,'revision_sha256':sha(revision),'prepare_script_sha256':sha(Path(__file__))}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');shutil.copyfile(__file__,out/'prepare_script.py');print('CANDIDATE_SYNTH_PREPARED rtl='+str(len(rtl)))
if __name__=='__main__':main()
