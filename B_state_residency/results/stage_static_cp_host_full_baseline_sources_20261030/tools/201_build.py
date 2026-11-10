"""Gated label-only route specialization and actual full-system port monitor."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent/'route_path_write_v1'
NAMES = ['route_commit_controller.sv', 'route_commit_host_adapter.sv']


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
    unit = reference.parent/'route_path_units_v1'
    um, ua, ur = restored(unit)
    assert len(ua['cases']) == 12 and ua['exact_trace_comparisons'] == 8
    assert ua['generic_overlap_preserved']
    f = ROOT/'results/route_path_units_sources_20261028'
    fm = json.loads((f/'manifest.json').read_text())
    assert fm['status'] == 'frozen'
    for name, entry in fm['files'].items():
        assert sha(f/name) == entry['sha256'], name
    vm = json.loads((PARENT/'manifest.json').read_text())
    proof = ROOT/'results/route_path_write_factoring_20261028.json'
    pr = json.loads(proof.read_text())
    assert pr['status'] == 'source_bound_two_state_write_predicates_not_RTL_validation'
    assert pr['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_path_write_factoring.py')
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
    assert original.count('\nendmodule') == 1 and '.PATH_SLOTS(4)' in original
    assert 'pb_cycles' not in original
    declarations = '''
 reg[31:0]pb_expected[0:3][0:31];reg pb_dirty=1;
 integer pb_cycles=0,pb_nodes=0,pb_publications=0,pb_checks=0;
'''
    monitor = '''
 // The reference follows the old control tree, never the new pw_* wires.
 task pb_old_advance;begin
  if(R.cp_check_slot==3&&R.cp_check_field+1==39)begin
   if(R.cp_importing&&~R.cp_running!=R.cp_wanted)begin end
   else if(!R.cp_importing)begin end
   else begin
    for(integer ps=0;ps<4;ps=ps+1)
     for(integer pn=0;pn<32;pn=pn+1)pb_expected[ps][pn]<=R.cp_stage[ps*39+7+pn];
    pb_publications=pb_publications+1;pb_dirty=1;
   end
  end
 end endtask
 genvar pb_s,pb_n;
 generate for(pb_s=0;pb_s<4;pb_s=pb_s+1)begin:pb_slots
  for(pb_n=0;pb_n<32;pb_n=pb_n+1)begin:pb_words
   always @(R.path[pb_s][pb_n])pb_dirty=1;
  end
 end endgenerate
 always @(posedge clk)begin
  if(!R.rst)begin
   case(R.cp_state)
    3:begin
     if(R.cp_failed||R.abort||R.fault||R.cp_drift)begin end
     else if(R.cp_bad)begin end
     else if(R.cp_stage[R.cp_check_slot*39]==1&&R.cp_check_field>7&&R.cp_check_field-7<R.cp_stage[R.cp_check_slot*39+1])begin end
     else pb_old_advance;
    end
    5:begin
     if(R.cp_failed||R.abort||R.fault||R.cp_drift)begin end
     else if(R.cp_stage[R.cp_check_slot*39+R.cp_check_field]==R.cp_stage[R.cp_check_slot*39+7+R.cp_dup_pos])begin end
     else if(R.cp_dup_pos+1==R.cp_check_field-7)pb_old_advance;
    end
   endcase
   if(!R.cp_busy&&R.state==2&&R.l_rsp_valid)begin
    if(R.stopped||R.fail_now)begin end
    else if((R.current==R.sink&&(R.l_payload[128]!=1||R.l_payload[127:96]!=R.sequence_id))||R.duplicate)begin end
    else if(R.current==R.source)begin end
    else if(R.l_payload[95:64]==32'hffffffff||R.l_payload[95:64]==R.sink||R.current==32'hffffffff)begin end
    else if(R.current!=R.sink&&R.length==32)begin end
    else if(R.current!=R.sink)begin
     pb_expected[R.slot][R.length]<=R.current;
     pb_nodes=pb_nodes+1;pb_dirty=1;
    end
   end
  end
  if(!k_cold_rst)pb_cycles=pb_cycles+1;
  #1;
  if(pb_dirty)begin
   for(integer ps=0;ps<4;ps=ps+1)
    for(integer pn=0;pn<32;pn=pn+1)
     if(R.path[ps][pn]!==pb_expected[ps][pn])$fatal(1,"path bank old-tree mismatch slot=%0d word=%0d",ps,pn);
   pb_checks=pb_checks+1;pb_dirty=0;
  end
 end
'''.replace('R.', 'system.inner.backend.route_join.controller.')
    check = ''' if(pb_cycles==0||pb_nodes==0||pb_publications==0||pb_checks==0)$fatal(1,"path bank reference coverage missing");
 $display("ROUTE_PATH_BANK_PASS cycles=%0d node_writes=%0d publications=%0d checked_cycles=%0d",pb_cycles,pb_nodes,pb_publications,pb_checks);
'''
    return original.replace(decl, decl+declarations).replace('\nendmodule', monitor+'\nendmodule').replace(marker, check+marker)


