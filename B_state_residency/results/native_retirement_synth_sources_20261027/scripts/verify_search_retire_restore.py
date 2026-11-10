"""Actually restore a verified archive and rerun its independent audit."""
from pathlib import Path
import json,subprocess,sys,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 name=sys.argv[1];script=sys.argv[2];extra=sys.argv[3:]
 index=ROOT/'results/offer_archives_20261025'/(name+'.json');record=json.loads(index.read_text());p=Path(record['source_root']);before=(p/'source_bound_audit.json').read_bytes()
 held=p.parent/'.preserved'/p.name;held.parent.mkdir(exist_ok=True);assert not held.exists();p.rename(held)
 subprocess.run([sys.executable,str(ROOT/'scripts/restore_offer_result.py'),str(index)],check=True)
 r=subprocess.run([sys.executable,str(ROOT/'scripts'/script),str(p),*extra],capture_output=True,text=True);assert r.returncode==0,r.stderr
 assert before==(p/'source_bound_audit.json').read_bytes()
 receipt=dict(status='passed',archive_index=str(index),archive_sha256=record['archive_sha256'],restored_root=str(p),preserved_original=str(held),files=len(record['members']),audit_byte_identical=True,audit_sha256=sha(p/'source_bound_audit.json'),auditor=script)
 dest=ROOT/'results'/(name+'_restore_20261025.json');dest.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt))
if __name__=='__main__':main()
