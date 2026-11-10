"""Drop the native capture result check only inside zero-depth retirement."""
from pathlib import Path
import hashlib,json

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/route_block_system_crc_pressure_v1')
NAME='priced/candidate_recursive_query_core.sv'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources(fixed):
    proof=json.loads((ROOT/'results/capture_retirement_identity_20261027.json').read_text())
    assert proof['status']=='zero_depth_retirement_identity_not_rtl_validation'and proof['valuations']==8192
    assert proof['analyzer_sha256']==sha(ROOT/'scripts/analyze_capture_retirement_identity.py')
    m=json.loads((BASE/'manifest.json').read_text());a=json.loads((BASE/'source_bound_audit.json').read_text())
    assert a['status']=='passed'and a['manifest_sha256']==sha(BASE/'manifest.json')
    assert proof['reference_audit_sha256']==sha(BASE/'source_bound_audit.json')
    for n,h in proof['source_sha256'].items():assert sha(BASE/'sources'/n)==h==m['sources'][n]['sha256']
    s=(BASE/'sources'/NAME).read_text()
    if fixed:
        old=' !g_rsp_valid&&!d_rsp_valid&&!b_result_valid&&!ce_result_valid&&!e_result_valid&&'
        assert s.count(old)==1
        s=s.replace(old,' !g_rsp_valid&&!d_rsp_valid&&!b_result_valid&&!ce_result_valid&&',1)
        marker=' // Label command replies retire via host_label_pending / p_result_valid;'
        assert s.count(marker)==1
        s=s.replace(marker,' // Native capture result_valid implies capture_depth!=0; the zero-depth\n // retirement condition below already excludes that reply.\n'+marker,1)
    return {NAME:s}
if __name__=='__main__':
    for mode in ['baseline','fixed']:
        d=HERE/mode;d.mkdir()
        for n,s in sources(mode=='fixed').items():
            q=d/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
    print('CAPTURE_RETIREMENT_SOURCE_PREPARED_NOT_VALIDATED')
