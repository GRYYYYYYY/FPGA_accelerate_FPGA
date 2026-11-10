"""Prepare stage-bank write factoring on the restored path area candidate."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/route_path_synth_v1')
NAMES = ['route_commit_controller.sv', 'route_commit_host_adapter.sv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(fixed):
    proof = json.loads((ROOT/'results/route_stage_write_factoring_20261029.json').read_text())
    assert proof['status'] == 'source_bound_control_and_bounded_word_model_not_RTL_validation'
    assert proof['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_stage_write_factoring_v2.py')
    m = json.loads((BASE/'manifest.json').read_text())
    a = json.loads((BASE/'source_bound_audit.json').read_text())
    rp = ROOT/'results/route_path_synth_v1_restore_20261025.json'
    r = json.loads(rp.read_text())
    assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed'
    assert r['audit_byte_identical'] and r['audit_sha256'] == sha(BASE/'source_bound_audit.json')
    assert a['manifest_sha256'] == sha(BASE/'manifest.json')
    assert proof['reference_audit_sha256'] == sha(BASE/'source_bound_audit.json')
    result = {}
    for name in NAMES:
        p = BASE/'sources'/name
        assert sha(p) == m['sources'][name]
        text = p.read_text()
        if fixed and name == 'route_commit_controller.sv':
            assert sha(p) == proof['source_sha256']
            old = 'parameter integer FACTORED_PATH_WRITES=0,'
            assert text.count(old) == 1
            text = text.replace(old, 'parameter integer FACTORED_STAGE_WRITES=0,FACTORED_PATH_WRITES=0,')
            start = text.index('      for(a=0;a<PATH_SLOTS;a=a+1)begin\n       cp_stage')
            end = text.index('      cp_state<=CP_VERIFY;', start)
            old = text[start:end]
            assert old.count('cp_stage[') == 8
            text = text[:start] + '      if(FACTORED_STAGE_WRITES==0)begin\n' + old + '      end\n' + text[end:]
            old = 'cp_stage[cp_pos]<=cp_s_data;'
            assert text.count(old) == 1
            text = text.replace(old, 'if(FACTORED_STAGE_WRITES==0)'+old)
            extra = '''
 // Preserve the original nested control tree, including invalid-frame guards.
 // The stage bank has no reset initialization in either implementation.
 reg sw_capture,sw_import;
 always @*begin
  sw_capture=0;sw_import=0;
  if(rst)begin end
  else begin
   case(cp_state)
    CP_IDLE:if(cp_valid&&cp_ready)begin
     if(cp_design!=active_design||cp_nodes==0||cp_nets==0)begin end
     else if(cp_restore)begin end
     else sw_capture=1;
    end
    CP_IMPORT:if(cp_failed||abort||fault||cp_drift)begin end
     else if(cp_s_valid&&cp_s_ready)begin
      if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos+1==CP_WORDS))begin end
      else sw_import=1;
     end
    default:begin end
   endcase
  end
 end
 genvar sw_slot,sw_field;
 generate if(FACTORED_STAGE_WRITES!=0)begin:factored_stage_bank
  for(sw_slot=0;sw_slot<PATH_SLOTS;sw_slot=sw_slot+1)begin:slots
   for(sw_field=0;sw_field<CP_STRIDE;sw_field=sw_field+1)begin:words
    wire[31:0]export_word;
    if(sw_field==0)assign export_word=slot_valid[sw_slot]?1:0;
    else if(sw_field==1)assign export_word=slot_valid[sw_slot]?sizes[sw_slot]:0;
    else if(sw_field==2)assign export_word=slot_valid[sw_slot]?nets[sw_slot]:0;
    else if(sw_field==3)assign export_word=slot_valid[sw_slot]?sources[sw_slot]:0;
    else if(sw_field==4)assign export_word=slot_valid[sw_slot]?sinks[sw_slot]:0;
    else if(sw_field==5)assign export_word=slot_valid[sw_slot]?designs[sw_slot][31:0]:0;
    else if(sw_field==6)assign export_word=slot_valid[sw_slot]?designs[sw_slot][63:32]:0;
    else assign export_word=slot_valid[sw_slot]&&sw_field-7<sizes[sw_slot]?path[sw_slot][sw_field-7]:0;
    always @(posedge clk)begin
     if(sw_capture)cp_stage[sw_slot*CP_STRIDE+sw_field]<=export_word;
     else if(sw_import&&cp_pos==sw_slot*CP_STRIDE+sw_field)cp_stage[sw_slot*CP_STRIDE+sw_field]<=cp_s_data;
    end
   end
  end
 end endgenerate
'''
            assert text.count('\nendmodule') == 1
            text = text.replace('\nendmodule', extra+'\nendmodule')
        elif fixed:
            old = 'route_commit_controller #(.FACTORED_PATH_WRITES(1),'
            assert text.count(old) == 1
            text = text.replace(old, 'route_commit_controller #(.FACTORED_STAGE_WRITES(1),.FACTORED_PATH_WRITES(1),')
        result[name] = text
    return result


if __name__ == '__main__':
    entries = {}
    for mode in ['baseline', 'fixed']:
        for name, text in sources(mode == 'fixed').items():
            path = HERE/mode/name
            assert not path.exists()
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text)
            entries.setdefault(name, {})[mode] = sha(path)
    (HERE/'manifest.json').write_text(json.dumps(dict(
        status='prepared_not_compiled_or_simulated', sources=entries,
        builder_sha256=sha(HERE/'build.py'),
        proof_sha256=sha(ROOT/'results/route_stage_write_factoring_20261029.json'),
        scope='Default-off stage writes on the path area candidate, both explicitly enabled by adapter. Original control tree and same-cycle data preserved; no new state, cycle, reset initialization or relaxed guards. Requires bank/cycle tests, complete system and matched OOC versus both path and CP.'
    ), indent=2, sort_keys=True)+'\n')
    print('ROUTE_STAGE_WRITE_CANDIDATE_PREPARED_NOT_VALIDATED')
