"""Gated label-only route specialization and actual full-system port monitor."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent/'route_label_exclusion_v2'
NAMES = ['route_commit_controller.sv', 'route_commit_host_adapter.sv', 'residency_system.sv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restored(path):
    m = json.loads((path/'manifest.json').read_text())
    a = json.loads((path/'source_bound_audit.json').read_text())
    rp = ROOT/'results'/f'{path.name}_restore_20261025.json'
    r = json.loads(rp.read_text())
    assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
    assert a['manifest_sha256'] == sha(path/'manifest.json')
    assert r['audit_byte_identical'] and r['audit_sha256'] == sha(path/'source_bound_audit.json')
    return m, a, rp


def sources(reference):
    assert reference.name == 'checkpoint_edit_system_crc_pressure_v1'
    rm, ra, rr = restored(reference)
    unit = reference.parent/'route_label_units_v2'
    um, ua, ur = restored(unit)
    assert len(ua['cases']) == 12 and ua['exact_trace_comparisons'] == 7
    assert ua['generic_overlap_specialization_counterexample']
    f = ROOT/'results/route_label_units_sources_20261028'
    fm = json.loads((f/'manifest.json').read_text())
    assert fm['status'] == 'frozen'
    for name, entry in fm['files'].items():
        assert sha(f/name) == entry['sha256'], name
    vm = json.loads((PARENT/'manifest.json').read_text())
    proof = ROOT/'results/route_label_exclusion_20261028.json'
    pr = json.loads(proof.read_text())
    assert pr['status'] == 'native_route_label_two_state_exclusion_not_rtl_validation'
    assert pr['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_label_exclusion.py')
    fixed = {}
    for name in NAMES:
        assert sha(reference/'sources'/name) == vm['sources'][name]['baseline']
        assert sha(PARENT/'fixed'/name) == vm['sources'][name]['fixed']
        fixed[name] = (PARENT/'fixed'/name).read_text()
    evidence = dict(reference_audit_sha256=sha(reference/'source_bound_audit.json'),
                    reference_restore_sha256=sha(rr), unit_audit_sha256=sha(unit/'source_bound_audit.json'),
                    unit_restore_sha256=sha(ur), unit_freeze_sha256=sha(f/'manifest.json'),
                    proof_sha256=sha(proof), builder_sha256=sha(HERE/'build.py'),
                    parent_manifest_sha256=sha(PARENT/'manifest.json'))
    return fixed, evidence


def monitored_tb(original):
    decl = 'module tb_candidate_offer;'
    marker = ' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
    assert original.count(decl) == original.count(marker) == 1
    assert original.count('\nendmodule') == 1 and 'rl_cycles' not in original
    counters = '\n integer rl_cycles=0,rl_requests=0,rl_replies=0;\n'
    monitor = '''
 always @(posedge clk)if(!k_cold_rst)begin
  if((^{R.l_ready,R.l_rsp_valid})===1'bx)$fatal(1,"route label READY/reply unknown");
  if(R.l_ready&&R.l_rsp_valid)$fatal(1,"route native label overlap");
  rl_cycles=rl_cycles+1;
  if(R.l_valid&&R.l_ready)rl_requests=rl_requests+1;
  if(R.l_rsp_valid&&R.l_rsp_ready)rl_replies=rl_replies+1;
 end
'''.replace('R.', 'system.inner.backend.route_join.controller.')
    check = ''' if(rl_cycles==0||rl_requests==0||rl_requests!=rl_replies)$fatal(1,"route label coverage missing or unbalanced");
 $display("ROUTE_LABEL_EXCLUSION_PASS cycles=%0d requests=%0d replies=%0d",rl_cycles,rl_requests,rl_replies);
'''
    return original.replace(decl, decl+counters).replace('\nendmodule', monitor+'\nendmodule').replace(marker, check+marker)
