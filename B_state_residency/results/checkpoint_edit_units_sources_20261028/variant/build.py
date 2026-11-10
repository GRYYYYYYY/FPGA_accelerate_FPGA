"""Prepare a default-off native checkpoint edit exclusion specialization."""
from pathlib import Path
import hashlib
import json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/query_native_synth_v1')
NAMES=['query_lifecycle.sv','query_residency_system.sv']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources(fixed):
    proof=json.loads((ROOT/'results/checkpoint_edit_exclusion_20261028.json').read_text())
    assert proof['status']=='native_cp_safe_excludes_edit_two_state_not_rtl_validation'
    assert proof['analyzer_sha256']==sha(ROOT/'scripts/analyze_checkpoint_edit_exclusion.py')
    result={}
    for n in NAMES:
        origin=BASE/'sources'/n;assert sha(origin)==proof['source_sha256'][n]
        original=origin.read_text();s=original
        if fixed and n=='query_lifecycle.sv':
            old='EXCLUSIVE_BACKEND_RESPONSES=0)('
            assert s.count(old)==1
            s=s.replace(old,'EXCLUSIVE_BACKEND_RESPONSES=0,CP_SAFE_EXCLUDES_HOST_EDIT=0)(')
            old='||host_label_edit||'
            assert s.count(old)==1
            s=s.replace(old,'||((CP_SAFE_EXCLUDES_HOST_EDIT==0)&&host_label_edit)||')
            # The existing host edit/label dirty updates and all CP state updates
            # are byte-identical; only the CP drift combinational term changes.
            assert s.split(' always @(posedge clk)begin',1)[1]==original.split(' always @(posedge clk)begin',1)[1]
        elif fixed:
            old='query_lifecycle #(.EXCLUSIVE_BACKEND_RESPONSES(1),'
            assert s.count(old)==1
            s=s.replace(old,'query_lifecycle #(.EXCLUSIVE_BACKEND_RESPONSES(1),.CP_SAFE_EXCLUDES_HOST_EDIT(1),')
        result[n]=s
    return result
if __name__=='__main__':
    manifest={}
    for mode in ['baseline','fixed']:
        for n,s in sources(mode=='fixed').items():
            p=HERE/mode/n;assert not p.exists();p.parent.mkdir(parents=True,exist_ok=True);p.write_text(s)
            manifest.setdefault(n,{})[mode]=sha(p)
    (HERE/'manifest.json').write_text(json.dumps(dict(status='prepared_not_compiled_or_simulated',sources=manifest,
        builder_sha256=sha(HERE/'build.py'),proof_sha256=sha(ROOT/'results/checkpoint_edit_exclusion_20261028.json')),
        indent=2,sort_keys=True)+'\n')
    print('CHECKPOINT_EDIT_CANDIDATE_PREPARED_NOT_VALIDATED')
