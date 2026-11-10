"""Verify clean candidate rebuild and packaged standalone regressions."""
from pathlib import Path
import json,re,hashlib
from audit_small_synthesis import resources
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 bundle=ROOT/'hardware/candidates/native_epoch6_record';bp=bundle/'manifest.json';b=json.loads(bp.read_text())
 for name,digest in b['artifacts'].items():assert sha(bundle/name)==digest,name
 full=ROOT/'results/record_epoch6_full_20261024';f=json.loads((full/'manifest.json').read_text());assert f['status']=='passed' and f['cycle_comparison']['equal'] and sha(full/'manifest.json')==b['full_manifest_sha256']
 gate=ROOT/'results/record_epoch6_full_workflow_20261024/manifest.json';assert sha(gate)==b['workflow_manifest_sha256'] and json.loads(gate.read_text())['status']=='composite_replay_audited'
 launch=ROOT/'results/candidate_package_rebuild_launch_20261024';lm=json.loads((launch/'manifest.json').read_text());assert lm['package_manifest_sha256']==sha(bp)
 assert sha(ROOT/'hardware/scripts/rebuild_candidate_package.tcl')==lm['launcher_sha256']==sha(launch/'rebuild_candidate_package.tcl')
 receipt=json.loads((launch/'completion_receipt.json').read_text());assert not receipt['is_command_running'] and receipt['last_completed_code']==0 and 'candidate_package_rebuild_20261024' in receipt['last_completed_output']
 out=ROOT/'results/candidate_package_rebuild_20261024';assert (out/'completed.txt').read_text()=='RESIDENCY_CANDIDATE_REBUILD_DONE version=2022.2\n'
 raw=Path(receipt['log_file']).read_text();matches=list(re.finditer(r'^RESIDENCY_CANDIDATE_REBUILD_BEGIN version=2022\.2',raw,re.M));assert len(matches)==1
 log=raw[matches[0].start():];end=re.search(r'^RESIDENCY_CANDIDATE_REBUILD_DONE\s*$',log,re.M);assert end;log=log[:end.end()]+'\n';assert not re.search(r'^ERROR:',log,re.M)
 old=ROOT/'results/record_epoch6_synthesis_20261024';old_a=json.loads((old/'final_audit.json').read_text());assert sha(old/'final_audit.json')==b['artifacts']['Evidence/synthesis_audit.json']
 new_resources=resources(out/'utilization.rpt');assert new_resources==old_a['resources']
 assert (out/'candidate.dcp').stat().st_size>10000
 checksum=re.search(r'Synth Design complete, checksum: (\w+)',log)[1];assert checksum==re.search(r'Synth Design complete, checksum: (\w+)',(old/'synthesis_session.log').read_text())[1]
 for key,value in [('FRAMES',163840),('INDEX_BITS',18),('HASH_BITS',18),('EPOCH_BITS',6)]:assert f'Parameter {key} bound to: {value} - type: integer' in log
 (out/'synthesis_session.log').write_text(log)
 simulations={}
 for case in ['checkpoint','wrap']:
  d=ROOT/'results'/f'candidate_package_{case}_20261024';mp=d/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed' and m['package_sha256']==sha(bp) and all(s['exit_code']==0 for s in m['commands'])
  assert sha(d/'simulate.log')==m['log_sha256'];simulations[case]=sha(mp)
 result={'status':'clean_rebuild_and_regressions_verified','package_manifest_sha256':sha(bp),'full_manifest_sha256':sha(full/'manifest.json'),'resources':new_resources,'synthesis_checksum':checksum,'simulations':simulations,'rebuild_receipt_sha256':sha(launch/'completion_receipt.json'),'rebuild_artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='final_audit.json'},'auditor_sha256':sha(Path(__file__)),'platform_closed':False,'scope':'self-contained native OOC source package; no XPR/data fixture/prior DCP dependency; not full router or board proof'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');(bundle/'validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(new_resources));print('CANDIDATE_CLEAN_REBUILD_PASS checksum='+checksum)
if __name__=='__main__':main()
