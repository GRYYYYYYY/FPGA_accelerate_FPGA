"""Prepare same-cycle path-bank write factoring from the preferred CP baseline."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/checkpoint_edit_synth_v1')
NAMES = ['route_commit_controller.sv', 'route_commit_host_adapter.sv']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sources(fixed):
    proof = json.loads((ROOT/'results/route_path_write_factoring_20261028.json').read_text())
    assert proof['status'] == 'source_bound_two_state_write_predicates_not_RTL_validation'
    assert proof['analyzer_sha256'] == sha(ROOT/'scripts/analyze_route_path_write_factoring.py')
    m = json.loads((BASE/'manifest.json').read_text())
    result = {}
    for name in NAMES:
        p = BASE/'sources'/name
        assert sha(p) == m['sources'][name]
        original = p.read_text()
        text = original
        if fixed and name == 'route_commit_controller.sv':
            assert sha(p) == proof['source_sha256']
            old = 'parameter integer PATH_SLOTS=2,'
            assert text.count(old) == 1
            text = text.replace(old, 'parameter integer FACTORED_PATH_WRITES=0,PATH_SLOTS=2,')
            old = 'for(b=0;b<MAX_PATH;b=b+1)path[a][b]<=cp_stage[a*CP_STRIDE+7+b];'
            assert text.count(old) == 1
            text = text.replace(old, 'if(FACTORED_PATH_WRITES==0)'+old)
            old = 'path[slot][length]<=current;'
            assert text.count(old) == 1
            text = text.replace(old, 'if(FACTORED_PATH_WRITES==0)'+old)
            extra = '''
 // Same-cycle publication qualifiers, including all original validation gates.
 wire pw_cancel=cp_failed||abort||fault||cp_drift;
 wire pw_verify_advance=cp_state==CP_VERIFY&&!cp_bad&&!(cp_stage[cp_check_slot*CP_STRIDE]==1&&cp_check_field>7&&cp_check_field-7<cp_stage[cp_check_slot*CP_STRIDE+1]);
 wire pw_dup_advance=cp_state==CP_DUP&&cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]!=cp_stage[cp_check_slot*CP_STRIDE+7+cp_dup_pos]&&cp_dup_pos+1==cp_check_field-7;
 wire pw_cp_write=!rst&&!pw_cancel&&(pw_verify_advance||pw_dup_advance)&&cp_check_slot==PATH_SLOTS-1&&cp_check_field+1==CP_STRIDE&&cp_importing&&~cp_running==cp_wanted;
 wire pw_node_write=!rst&&!cp_busy&&state==LW&&l_rsp_valid&&!stopped&&!fail_now&&!duplicate&&current!=sink&&current!=source&&current!=32'hffffffff&&l_payload[95:64]!=32'hffffffff&&l_payload[95:64]!=sink&&length!=MAX_PATH;
 genvar pw_slot,pw_word;
 generate if(FACTORED_PATH_WRITES!=0)begin:factored_path_bank
  for(pw_slot=0;pw_slot<PATH_SLOTS;pw_slot=pw_slot+1)begin:slots
   for(pw_word=0;pw_word<MAX_PATH;pw_word=pw_word+1)begin:words
    always @(posedge clk)begin
     if(pw_cp_write)path[pw_slot][pw_word]<=cp_stage[pw_slot*CP_STRIDE+7+pw_word];
     else if(pw_node_write&&slot==pw_slot&&length==pw_word)path[pw_slot][pw_word]<=current;
    end
   end
  end
 end endgenerate
'''
            assert text.count('\nendmodule') == 1
            text = text.replace('\nendmodule', extra+'\nendmodule')
        elif fixed:
            old = 'route_commit_controller #(.PATH_SLOTS(PATH_SLOTS),'
            assert text.count(old) == 1
            text = text.replace(old, 'route_commit_controller #(.FACTORED_PATH_WRITES(1),.PATH_SLOTS(PATH_SLOTS),')
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
        proof_sha256=sha(ROOT/'results/route_path_write_factoring_20261028.json'),
        scope='Default-off controller write factoring, enabled by integrated adapter. '
              'Same-cycle path writes, no new state or pipeline, full publication guards retained. '
              'No label-exclusion change. Requires exact default/enabled tests, real system and OOC.'
    ), indent=2, sort_keys=True)+'\n')
    print('ROUTE_PATH_WRITE_CANDIDATE_PREPARED_NOT_VALIDATED')
