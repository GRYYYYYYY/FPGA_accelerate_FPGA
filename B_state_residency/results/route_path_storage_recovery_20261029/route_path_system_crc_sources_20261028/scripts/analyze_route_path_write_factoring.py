"""Check two-state write-event predicates before any path-bank RTL refactor."""
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
source = p/'sources/route_commit_controller.sv'
assert sha(source) == m['sources'][source.name]
s = source.read_text()
required = [
 'if(!cp_busy)case(state)',
 'wire cp_drift=!active||!lease||!cp_safe||active_design!=cp_context;',
 'if(cp_check_slot==PATH_SLOTS-1&&cp_check_field+1==CP_STRIDE)begin',
 "if(cp_importing&&~cp_running!=cp_wanted)begin cp_status<=1;cp_state<=CP_DONE;end",
 'else if(!cp_importing)begin cp_pos<=0;cp_state<=CP_EXPORT;end',
 'for(b=0;b<MAX_PATH;b=b+1)path[a][b]<=cp_stage[a*CP_STRIDE+7+b];',
 'if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end',
 'else if(cp_bad)begin cp_status<=1;cp_state<=CP_DONE;end',
 'else if(cp_stage[cp_check_slot*CP_STRIDE]==1&&cp_check_field>7&&cp_check_field-7<cp_stage[cp_check_slot*CP_STRIDE+1])begin cp_dup_pos<=0;cp_state<=CP_DUP;end',
 'else if(cp_stage[cp_check_slot*CP_STRIDE+cp_check_field]==cp_stage[cp_check_slot*CP_STRIDE+7+cp_dup_pos])begin cp_status<=1;cp_state<=CP_DONE;end',
 'else if(cp_dup_pos+1==cp_check_field-7)cp_advance;',
 'if(stopped||fail_now)finish(stopped?error_code:(bad_l?4:6));',
 'else if((current==sink&&(l_payload[128]!=1||l_payload[127:96]!=sequence_id))||duplicate)fatal_finish(2);',
 "else if(l_payload[95:64]==32'hffffffff||l_payload[95:64]==sink||current==32'hffffffff)fatal_finish(2);",
 'else if(current!=sink&&length==MAX_PATH)fatal_finish(3);',
 "if(current!=sink)begin path[slot][length]<=current;length<=length+1'b1;end"
]
for expression in required:
 assert expression in s, expression

cp_count = cp_writes = 0
for state in range(8):
 for reset,failed,abort,fault,drift,bad,needs_dup,equal,dup_done,last_slot,last_field,importing,crc_match in product([False,True],repeat=13):
  cancel = failed or abort or fault or drift
  advance = False
  if not reset:
   if state == 3:
    if cancel: pass
    elif bad: pass
    elif needs_dup: pass
    else: advance = True
   elif state == 5:
    if cancel: pass
    elif equal: pass
    elif dup_done: advance = True
  old = False
  if advance and last_slot and last_field:
   if importing and not crc_match: pass
   elif not importing: pass
   else: old = True
  new = (not reset and not cancel and importing and crc_match and last_slot and last_field
         and ((state == 3 and not bad and not needs_dup) or
              (state == 5 and not equal and dup_done)))
  assert old == new
  # Non-reset CP activity excludes the original normal-path case statement.
  assert not (new and state == 0)
  cp_count += 1
  cp_writes += int(new)

normal_count = normal_writes = 0
for state in range(8):
 for reset,cp_busy,reply,stopped,fail,sink,source_node,bad_sequence,duplicate,prev_invalid,prev_sink,current_invalid,full in product([False,True],repeat=13):
  old = False
  if not reset and not cp_busy and state == 2 and reply:
   if stopped or fail: pass
   elif (sink and bad_sequence) or duplicate: pass
   elif source_node: pass
   elif prev_invalid or prev_sink or current_invalid: pass
   elif not sink and full: pass
   elif not sink: old = True
  new = (not reset and not cp_busy and state == 2 and reply and not stopped and not fail
         and not sink and not source_node and not duplicate and not prev_invalid
         and not prev_sink and not current_invalid and not full)
  assert old == new
  normal_count += 1
  normal_writes += int(new)
assert cp_writes > 0 and normal_writes > 0
out = ROOT/'results/route_path_write_factoring_20261028.json'
assert not out.exists()
out.write_text(json.dumps(dict(
 status='source_bound_two_state_write_predicates_not_RTL_validation',
 analyzer_sha256=sha(Path(__file__)), reference_audit_sha256=sha(p/'source_bound_audit.json'),
 restore_receipt_sha256=sha(rp), source_sha256=sha(source), checked_expressions=required,
 valuations=dict(checkpoint=cp_count, checkpoint_writes=cp_writes,
                 normal=normal_count, normal_writes=normal_writes),
 proposal='Factor path bank into explicit static per-word write processes with the same-cycle '
          'checkpoint publication and ordinary indexed-write predicates. No added register or cycle. '
          'Keep original generic/default implementation available for direct comparison.',
 scope='Boolean control model, not RTL formal, X/Z equivalence, data/index proof or synthesis benefit. '
       'CRC, cancellation, drift and final verification qualifiers must all remain. '
       'Candidate must branch from the preferred CP baseline, not rejected label-exclusion mapping.'
), indent=2, sort_keys=True)+'\n')
print('ROUTE_PATH_WRITE_PREDICATES', cp_count, normal_count, cp_writes, normal_writes)
