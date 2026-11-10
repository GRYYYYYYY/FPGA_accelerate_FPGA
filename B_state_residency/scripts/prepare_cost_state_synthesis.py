from pathlib import Path
import hashlib,json,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();assert not out.exists();gates={};digest=None
 for name in ['cost_state_20261025','cost_state_boundaries_20261025']:
  dep=ROOT/'results'/name;m=json.loads((dep/'manifest.json').read_text());a=json.loads((dep/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and a['manifest_sha256']==sha(dep/'manifest.json')
  spec=m['sources']['cost_state_store.sv'];current=sha(dep/'sources/cost_state_store.sv');assert current==spec['sha256']==sha(Path(spec['path']))
  if digest is not None:assert digest==current
  digest=current;gates[name]={'manifest_sha256':sha(dep/'manifest.json'),'audit_sha256':sha(dep/'source_bound_audit.json')}
 out.mkdir();src=out/'sources';src.mkdir();module=ROOT/'hardware/variants/cost_state_v1/cost_state_store.sv';shutil.copyfile(module,src/module.name)
 for name in gates:shutil.copyfile(ROOT/'results'/name/'source_bound_audit.json',out/(name+'_audit.json'))
 revision={'status':'passed','rtl_sha256':digest,'gates':gates};(out/'revision.json').write_text(json.dumps(revision,indent=2)+'\n')
 manifest={'status':'prepared','top':'cost_state_store','part':'xcu280-fsvh2892-2L-e','clock_period_ns':10,'parameters':'all RTL defaults; MAX_CYCLES1048576','sources':{module.name:{'path':str(module),'sha256':digest}},'rtl':[module.name],'gates':gates,'revision_sha256':sha(out/'revision.json'),'prepare_script_sha256':sha(Path(__file__))}
 (out/'manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');shutil.copyfile(__file__,out/'prepare_script.py');print('COST_STATE_SYNTH_PREPARED')
if __name__=='__main__':main()
