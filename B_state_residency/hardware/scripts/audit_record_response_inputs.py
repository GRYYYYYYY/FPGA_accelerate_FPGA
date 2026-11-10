"""Audit invocation/vector binding independently of an active replay's verdict."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/record_response_full_20261024';m=json.loads((out/'manifest.json').read_text());r=m['cases']['pilot']
 bp=ROOT/'results/rtl_small_checkpoint_stream_full_20261023';b=json.loads((bp/'manifest.json').read_text())
 assert sha(bp/'manifest.json')==r['baseline_sha256']==json.loads((bp/'completion_audit.json').read_text())['manifest_sha256']
 a=next(x['argv'] for x in r['commands'] if x['stage']=='simulate');ba=next(x['argv'] for x in b['commands'] if x['stage']=='simulate')
 assert a[0]==ba[0] and a[1]=='ablation' and a[2:]==ba[2:]
 assert (out/'pilot/run.tcl').read_text()=='run all\nquit\n'
 vdir=ROOT/'results/small_checkpoint_vectors_full_20261023';vp=vdir/'manifest.json';v=json.loads(vp.read_text());assert v['status']=='passed' and sha(vp)==b['vector_manifest_sha256']
 hashes={}
 for name in ['actual.txt','pages.hex']:
  p=vdir/name;hashes[name]=sha(p);assert hashes[name]==v['artifacts'][name]
  assert str(p) in '\n'.join(a)
 result={'status':'passed','scope':'input binding only; replay completion not established','baseline_sha256':sha(bp/'manifest.json'),'vector_manifest_sha256':sha(vp),'vector_hashes':hashes,'simulate_argv':a,'run_tcl_sha256':sha(out/'pilot/run.tcl'),'auditor_sha256':sha(Path(__file__))}
 (out/'input_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('RECORD_RESPONSE_INPUT_BINDING_PASS')
if __name__=='__main__':main()
