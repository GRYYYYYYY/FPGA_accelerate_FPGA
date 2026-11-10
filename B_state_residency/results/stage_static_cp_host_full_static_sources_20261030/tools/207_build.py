"""Gated stage-bank specialization with the old control tree as a reference."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PARENT = HERE.parent/'route_stage_write_v1'
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
    assert reference.name == 'route_path_system_crc_pressure_v1'
    rm, ra, rr = restored(reference)
    unit = reference.parent/'route_stage_units_v1'
    um, ua, ur = restored(unit)
    assert len(ua['cases']) == 12 and ua['exact_trace_comparisons'] == 8
    assert ua['generic_overlap_preserved']
    for mode in ['baseline','default','factored']:
        for suite in ['checkpoint','checkpoint32']:
            entry=ua['cases'][f'{mode}_{suite}']
            assert entry['stage_captures']>0 and entry['stage_imports']>0 and entry['stage_checked_cycles']>0
    f = ROOT/'results/route_stage_units_sources_20261029'
    fm = json.loads((f/'manifest.json').read_text())
    assert fm['status'] == 'frozen'
    for name, entry in fm['files'].items():
        assert sha(f/name) == entry['sha256'], name
    vm = json.loads((PARENT/'manifest.json').read_text())
    proof = ROOT/'results/route_stage_write_factoring_20261029.json'
    pr = json.loads(proof.read_text())
    assert pr['status'] == 'source_bound_control_and_bounded_word_model_not_RTL_validation'
    assert pr['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_stage_write_factoring_v2.py')
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
    assert 'pb_cycles' in original and 'ROUTE_PATH_BANK_PASS' in original
    assert 'sb_cycles' not in original
    declarations = '''
 reg[31:0]sb_expected[0:155];reg sb_dirty=1;
 integer sb_cycles=0,sb_captures=0,sb_imports=0,sb_checks=0;
'''
    monitor = '''
 // Old stage-write branches. Never use the candidate's sw_* event wires.
 genvar sb_w;
 generate for(sb_w=0;sb_w<156;sb_w=sb_w+1)begin:sb_words
  always @(R.cp_stage[sb_w])sb_dirty=1;
 end endgenerate
 always @(posedge clk)begin
  if(R.rst)begin end
  else begin
   case(R.cp_state)
    0:if(R.cp_valid&&R.cp_ready)begin
     if(R.cp_design!=R.active_design||R.cp_nodes==0||R.cp_nets==0)begin end
     else if(R.cp_restore)begin end
     else begin
      sb_captures=sb_captures+1;sb_dirty=1;
      for(integer ss=0;ss<4;ss=ss+1)begin
       sb_expected[ss*39]<=R.slot_valid[ss]?1:0;
       sb_expected[ss*39+1]<=R.slot_valid[ss]?R.sizes[ss]:0;
       sb_expected[ss*39+2]<=R.slot_valid[ss]?R.nets[ss]:0;
       sb_expected[ss*39+3]<=R.slot_valid[ss]?R.sources[ss]:0;
       sb_expected[ss*39+4]<=R.slot_valid[ss]?R.sinks[ss]:0;
       sb_expected[ss*39+5]<=R.slot_valid[ss]?R.designs[ss][31:0]:0;
       sb_expected[ss*39+6]<=R.slot_valid[ss]?R.designs[ss][63:32]:0;
       for(integer ww=0;ww<32;ww=ww+1)
        sb_expected[ss*39+7+ww]<=R.slot_valid[ss]&&ww<R.sizes[ss]?R.path[ss][ww]:0;
      end
     end
    end
    2:if(R.cp_failed||R.abort||R.fault||R.cp_drift)begin end
     else if(R.cp_s_valid&&R.cp_s_ready)begin
      if(R.cp_s_index!=R.cp_pos||R.cp_s_last!=(R.cp_pos+1==156))begin end
      else begin
       sb_expected[R.cp_pos]<=R.cp_s_data;
       sb_imports=sb_imports+1;sb_dirty=1;
      end
     end
    default:begin end
   endcase
  end
  if(!k_cold_rst)sb_cycles=sb_cycles+1;
  #1;
  if(sb_dirty)begin
   for(integer ww=0;ww<156;ww=ww+1)
    if(R.cp_stage[ww]!==sb_expected[ww])$fatal(1,"stage bank old-tree mismatch word=%0d got=%08h expected=%08h",ww,R.cp_stage[ww],sb_expected[ww]);
   sb_checks=sb_checks+1;sb_dirty=0;
  end
 end
'''.replace('R.', 'system.inner.backend.route_join.controller.')
    check = ''' if(sb_cycles==0||sb_captures==0||sb_imports==0||sb_checks==0)$fatal(1,"stage bank reference coverage missing");
 $display("ROUTE_STAGE_BANK_PASS cycles=%0d captures=%0d imports=%0d checked_cycles=%0d",sb_cycles,sb_captures,sb_imports,sb_checks);
'''
    return original.replace(decl, decl+declarations).replace('\nendmodule', monitor+'\nendmodule').replace(marker, check+marker)

