"""Source-bound native label exclusion; two-state model, not RTL formal proof."""
from itertools import product
from pathlib import Path
import json
from run_checkpoint_authority import ROOT, sha

p = Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_synth_v1')
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results/checkpoint_edit_synth_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert a['manifest_sha256'] == sha(p/'manifest.json') and r['audit_sha256'] == sha(p/'source_bound_audit.json')
required = {
 'candidate/service_arbiter.sv': [
  'localparam IDLE=0,SEND=1,WAIT_REPLY=2;',
  'selected=-1;c_req_ready=0;',
  'if(!rst&&!fault&&state==IDLE&&selected>=0)c_req_ready[selected]=1;',
  'assign c_rsp_valid[g]=!rst&&state==WAIT_REPLY&&owner==g&&b_rsp_valid;'],
 'priced/candidate_recursive_query_core.sv': [
  'service_arbiter #(.CLIENTS(5),.REQUEST_BITS(68),.RESPONSE_BITS(165))io_arb(',
  'assign h_io_ready=arb_io_c_req_ready[2];',
  'assign h_io_rsp_valid=arb_io_c_rsp_valid[2];',
  'assign host_io_ready=h_io_ready&&permit_label&&!host_ctrl_valid;',
  'assign host_io_rsp_valid=h_io_rsp_valid;',
  '.c_req_ready(arb_io_c_req_ready)', '.c_rsp_valid(arb_io_c_rsp_valid)'],
 'priced/candidate_recursive_engine.sv': [
  'assign host_io_ready=core_host_io_ready&&!state_lease&&!fault;',
  '.host_io_ready(core_host_io_ready)', '.host_io_rsp_valid(host_io_rsp_valid)'],
 'residency_system.sv': [
  '.host_io_ready(b_l_ready)', '.host_io_rsp_valid(b_l_rsp_valid)',
  '.b_l_ready(b_l_ready)', '.b_l_rsp_valid(b_l_rsp_valid)'],
 'route_commit_host_adapter.sv': [
  'assign l_ready=held&&b_l_ready;assign l_rsp_valid=held&&b_l_rsp_valid;',
  '.l_ready(l_ready)', '.l_rsp_valid(l_rsp_valid)'],
 'route_commit_controller.sv': [
  'localparam IDLE=0,LS=1,LW=2,OS=3,OW=4;',
  'wire unexpected=(l_rsp_valid&&state!=LW&&!(state==LS&&l_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));']
}
for name, expressions in required.items():
 assert sha(p/'sources'/name) == m['sources'][name], name
 text = (p/'sources'/name).read_text()
 for expression in expressions:
  assert expression in text, (name, expression)

pairs = set()
count = 0
for state in range(4):
 for rst,fault,selected_here,owner_here,bvalid,permit,ctrl,lease,engine_fault,held in product([False,True], repeat=10):
  ready = not rst and not fault and state == 0 and selected_here
  valid = not rst and state == 2 and owner_here and bvalid
  ready = ready and permit and not ctrl and not lease and not engine_fault and held
  valid = valid and held
  assert not (ready and valid)
  pairs.add((ready, valid)); count += 1
assert pairs == {(False,False),(False,True),(True,False)}
predicates = 0
for state,(ready,valid),ov,oready in product(range(8),sorted(pairs),[False,True],[False,True]):
 owner = ov and state != 4 and not (state == 3 and oready)
 old = (valid and state != 2 and not (state == 1 and ready)) or owner
 new = (valid and state != 2) or owner
 assert old == new
 predicates += 1
# Generic overlap remains a legal input to the unspecialized controller.
counterexample = dict(state='LS', l_ready=True, l_rsp_valid=True,
                     o_rsp_valid=False, original_unexpected=False, specialized_unexpected=True)
out = ROOT/'results/route_label_exclusion_20261028.json'
assert not out.exists()
out.write_text(json.dumps(dict(
 status='native_route_label_two_state_exclusion_not_rtl_validation',
 analyzer_sha256=sha(Path(__file__)), reference_audit_sha256=sha(p/'source_bound_audit.json'),
 restore_receipt_sha256=sha(rp), source_sha256={n:sha(p/'sources'/n) for n in required},
 checked_expressions=required, valuations=dict(label_chain=count, route_predicate=predicates),
 generic_overlap_counterexample=counterexample,
 scope='Only label READY/reply exclusion through the real five-client arbiter chain. '
       'Owner predicate is unchanged and arbitrarily valued. Not X/Z, RTL formal, simulation or timing proof. '
       'Any specialization must default off and be enabled only for the verified native chain.'
), indent=2, sort_keys=True)+'\n')
print('ROUTE_LABEL_EXCLUSION', count, predicates)
