"""Recompute an existing filter oracle into a temporary directory and compare bytes."""
from pathlib import Path
import json, subprocess, sys, tempfile
from run_checkpoint_authority import ROOT, sha

p=Path(sys.argv[1]).resolve()
m=json.loads((p/'manifest.json').read_text())
assert m['status']=='passed' and m['runner_sha256']==sha(ROOT/'scripts/verify_followup_filters.py')
assert m['input_audit_sha256']==sha(Path(m['input_root'])/'source_bound_audit.json')
for n,h in m['artifacts'].items():assert sha(p/n)==h,n
with tempfile.TemporaryDirectory(prefix='q3_filter_reaudit_')as tmp:
    target=Path(tmp)/'oracle'
    r=subprocess.run([sys.executable,str(ROOT/'scripts/verify_followup_filters.py'),m['input_root'],str(target)],capture_output=True,text=True)
    assert r.returncode==0,r.stderr
    for name in list(m['artifacts'])+['manifest.json','source_bound_audit.json']:
        assert (p/name).read_bytes()==(target/name).read_bytes(),name
print('FOLLOWUP_FILTER_REPLAY_BYTE_IDENTICAL')
