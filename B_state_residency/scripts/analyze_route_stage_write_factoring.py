"""Bind the two stage write sites and check their bounded control/address model."""
from itertools import product
from pathlib import Path
import json
import re
from run_checkpoint_authority import ROOT, sha

base = Path('/tmp/B_state_residency_offer_20261025')
gate = json.loads((base/'route_path_synth_followup_v1/manifest.json').read_text())
assert gate['status'] == 'observed' and gate['stage'] == 'complete'
p = base/'route_path_synth_v1'
m = json.loads((p/'manifest.json').read_text())
a = json.loads((p/'source_bound_audit.json').read_text())
rp = ROOT/'results/route_path_synth_v1_restore_20261025.json'
r = json.loads(rp.read_text())
assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
assert a['manifest_sha256'] == sha(p/'manifest.json')
assert r['audit_sha256'] == sha(p/'source_bound_audit.json')
source = p/'sources/route_commit_controller.sv'
assert sha(source) == m['sources'][source.name]
s = source.read_text()
required = [
 'CP_IDLE:if(cp_valid&&cp_ready)begin',
 'if(cp_design!=active_design||cp_nodes==0||cp_nets==0)begin cp_status<=1;cp_state<=CP_DONE;end',
 'else if(cp_restore)cp_state<=CP_IMPORT;',
 'cp_stage[a*CP_STRIDE]<=slot_valid[a]?1:0;',
 'cp_stage[a*CP_STRIDE+1]<=slot_valid[a]?sizes[a]:0;',
 'cp_stage[a*CP_STRIDE+2]<=slot_valid[a]?nets[a]:0;',
 'cp_stage[a*CP_STRIDE+3]<=slot_valid[a]?sources[a]:0;',
 'cp_stage[a*CP_STRIDE+4]<=slot_valid[a]?sinks[a]:0;',
 'cp_stage[a*CP_STRIDE+5]<=slot_valid[a]?designs[a][31:0]:0;',
 'cp_stage[a*CP_STRIDE+6]<=slot_valid[a]?designs[a][63:32]:0;',
 'for(b=0;b<MAX_PATH;b=b+1)cp_stage[a*CP_STRIDE+7+b]<=slot_valid[a]&&b<sizes[a]?path[a][b]:0;',
 'CP_IMPORT:if(cp_failed||abort||fault||cp_drift)begin cp_status<=2;cp_state<=CP_DONE;end',
 'else if(cp_s_valid&&cp_s_ready)begin',
 'if(cp_s_index!=cp_pos||cp_s_last!=(cp_pos+1==CP_WORDS))begin cp_status<=1;cp_state<=CP_DONE;end',
 'else begin cp_stage[cp_pos]<=cp_s_data;cp_running<=crc_word(cp_running,cp_s_data);',
]
for text in required:
    assert text in s, text
assert len(re.findall(r'cp_stage\[[^;\n]*?<=', s)) == 9

count = captures = imports = 0
for state in range(8):
    for reset, offer, ready, bad_design, bad_nodes, bad_nets, restore, failed, abort, fault, drift, valid, stream_ready, bad_index, bad_last in product([False, True], repeat=15):
        old_capture = old_import = False
        if not reset:
            if state == 0 and offer and ready:
                if bad_design or bad_nodes or bad_nets:
                    pass
                elif restore:
                    pass
                else:
                    old_capture = True
            elif state == 2:
                if failed or abort or fault or drift:
                    pass
                elif valid and stream_ready:
                    if bad_index or bad_last:
                        pass
                    else:
                        old_import = True
        new_capture = (not reset and state == 0 and offer and ready
                       and not (bad_design or bad_nodes or bad_nets) and not restore)
        new_import = (not reset and state == 2 and not (failed or abort or fault or drift)
                      and valid and stream_ready and not (bad_index or bad_last))
        assert (old_capture, old_import) == (new_capture, new_import)
        assert not (new_capture and new_import)
        count += 1
        captures += int(new_capture)
        imports += int(new_import)
assert captures and imports

# Independent flattened-word interpretation of the original nested export loop.
word_checks = indexed_checks = 0
for slots in [1, 2, 4]:
    for length in [1, 8, 32]:
        stride = 7 + length
        total = slots * stride
        for mask in range(1 << slots):
            for size in sorted(set([0, 1, max(0, length-1), length, length+1])):
                valid_slots = [bool(mask & (1 << slot)) for slot in range(slots)]
                paths = [[0x12340000 + 256*slot + word for word in range(length)] for slot in range(slots)]
                metadata = [[size, 100+slot, 200+slot, 300+slot, 0x76540000+slot, 0xabcd0000+slot] for slot in range(slots)]
                nested = []
                for slot in range(slots):
                    nested.extend(([1] + metadata[slot]) if valid_slots[slot] else [0]*7)
                    nested.extend(paths[slot][word] if valid_slots[slot] and word < size else 0 for word in range(length))
                flattened = []
                for position in range(total):
                    slot, field = divmod(position, stride)
                    if field == 0:
                        value = int(valid_slots[slot])
                    elif field < 7:
                        value = metadata[slot][field-1] if valid_slots[slot] else 0
                    else:
                        value = paths[slot][field-7] if valid_slots[slot] and field-7 < size else 0
                    flattened.append(value)
                assert nested == flattened
                word_checks += total
        original = [0x87650000+i for i in range(total)]
        for position in list(range(total+2)) + [0xffffffff]:
            old = original.copy()
            if position < total:
                old[position] = 0x12345678
            new = [0x12345678 if i == position else v for i, v in enumerate(original)]
            assert old == new
            indexed_checks += 1

out = ROOT/'results/route_stage_write_factoring_20261029.json'
assert not out.exists()
out.write_text(json.dumps(dict(
    status='source_bound_control_and_bounded_word_model_not_RTL_validation',
    analyzer_sha256=sha(Path(__file__)), source_sha256=sha(source),
    reference_audit_sha256=sha(p/'source_bound_audit.json'),
    restore_receipt_sha256=sha(rp), checked_expressions=required,
    valuations=count, capture_valuations=captures, import_valuations=imports,
    export_word_checks=word_checks, indexed_import_cases=indexed_checks,
    proposal='Static per-word cp_stage writes, retaining original nested if/else control tree, no register or cycle added. Default-off option on the path area candidate; CP remains timing reference.',
    scope='Two-state control predicates and bounded Python word/index model only, not RTL formal or X/Z proof. Actual candidate must compare complete path and stage banks and event cycles, including failed imports, export snapshots, cancellation and reset behavior.'
), indent=2, sort_keys=True)+'\n')
print('ROUTE_STAGE_WRITE_MODEL', count, captures, imports, word_checks, indexed_checks)
