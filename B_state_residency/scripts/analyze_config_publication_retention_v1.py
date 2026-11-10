"""Source-bound binary guard study and four-value counterexample, not RTL proof."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
TARGET = BASE / 'checkpoint_edit_route_recovery_v1'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def four_ne(a, b):
    if a in '01' and b in '01':
        return '1' if a != b else '0'
    return 'x'


def main():
    manifest_file = TARGET / 'manifest.json'
    manifest = json.loads(manifest_file.read_text())
    assert manifest['status'] == 'observed' and manifest['stage'] == 'complete'
    source = TARGET / 'sources/config_restore_controller.sv'
    assert sha(source) == manifest['inputs']['sources/config_restore_controller.sv']
    baseline = BASE / 'checkpoint_edit_synth_v1'
    baseline_manifest = json.loads((baseline / 'manifest.json').read_text())
    assert sha(source) == baseline_manifest['sources']['config_restore_controller.sv']
    assert sha(source) == sha(baseline / 'sources/config_restore_controller.sv')
    nav_file = ROOT / 'results/checkpoint_edit_route_recovery_timing_20261030.json'
    nav = json.loads(nav_file.read_text())
    assert nav['audit_sha256'] == sha(TARGET / 'source_bound_audit.json')
    diag_file = ROOT / 'results/checkpoint_edit_route_diagnostics_20261030.json'
    diag = json.loads(diag_file.read_text())
    assert diag['status'] == 'restored_reports_classified_no_fix'
    assert diag['bound'][str(nav_file)] == sha(nav_file)
    worst = nav['observations']['routed']['worst']['Setup']
    assert worst['destination'] == 'inner/backend/config_restore/descriptor_reg[1177]/CE'
    text = source.read_text()
    required = [
        "assign active_payload=configured?{descriptor[2303:2272],current_version,descriptor[2239:0]}:2304'd0;",
        'assign staged_valid=!rst&&!abort&&prepared&&!load_rsp_valid&&state==IDLE&&!fault;',
        'assign publish_ready=staged_valid&&publish_permit&&!load_valid&&!start_valid&&!attempt_reset&&!discard_valid&&backend_drained&&normal_retired;',
        'assign load_ready=!rst&&!abort&&!attempt_reset&&!stopped&&state==IDLE&&!load_rsp_valid&&backend_drained&&normal_retired;',
        'assign start_ready=!rst&&!prepared&&!attempt_reset&&!stopped&&configured&&state==IDLE&&!load_rsp_valid&&!load_valid&&backend_drained&&normal_retired;',
        'wire fail_now=busy&&!rsp_valid&&(abort||elapsed>=MAX_CYCLES);',
        'assign busy=!rst&&state!=IDLE;assign fault=!rst&&(stopped||fail_now);',
        'else if(attempt_reset&&state==IDLE&&!load_rsp_valid&&backend_drained&&normal_retired)begin',
        'if(load_valid&&load_ready)begin',
        'if(prepared||(!load_stage&&configured))load_status<=1;',
        'if(!publish_permit||!configured||!load_authoritative||load_design!=saved_design||load_checkpoint<=saved_checkpoint||!descriptor_ok(load_payload,load_design)||load_payload!=active_payload)load_status<=1;',
        'else begin prepared<=1;shadow_payload<=load_payload;shadow_design<=load_design;shadow_checkpoint<=load_checkpoint;end',
        'else begin descriptor<=load_payload;saved_design<=load_design;saved_checkpoint<=load_checkpoint;current_version<=load_payload[2240+:32];configured<=1;end',
        'if(publish_valid&&publish_ready)begin descriptor<=shadow_payload;saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_payload[2240+:32];prepared<=0;end',
        'if((discard_valid&&discard_ready)||abort||fail_now)prepared<=0;',
    ]
    for expression in required:
        assert expression in text, expression
    assert re.findall(r'\bdescriptor\s*<=\s*([^;]+);', text) == ['0', 'load_payload', 'shadow_payload']
    assert re.findall(r'\bprepared\s*<=\s*([^;]+);', text) == ['0', '0', '1', '0', '0']
    assert re.findall(r'\bshadow_payload\s*<=\s*([^;]+);', text) == ['0', 'load_payload']
    # retired abstracts backend_drained && normal_retired; idle abstracts the
    # original state comparison. Payload/design/descriptor predicates are binary
    # projections. No claim is made that this is executable RTL or formal proof.
    counts = Counter()
    count = 0
    for (rst, abort, attempt, retired, stopped, idle, load_rsp, configured, prepared,
         load_valid, stage, permit, pub_valid, start_valid, discard, authoritative,
         descriptor_valid, design_equal, checkpoint_newer, payload_equal) in product((0, 1), repeat=20):
        count += 1
        reset_attempt = attempt and idle and not load_rsp and retired
        body = not rst and not reset_attempt
        load_ready = not (rst or abort or attempt or stopped or load_rsp) and idle and retired
        load = body and idle and load_valid and load_ready
        capture = load and not prepared and stage and permit and configured and authoritative and design_equal and checkpoint_newer and descriptor_valid and payload_equal
        initial = load and not prepared and not stage and not configured and authoritative and descriptor_valid
        staged = not (rst or abort or load_rsp or stopped) and prepared and idle
        pub_ready = staged and permit and not (load_valid or start_valid or attempt or discard) and retired
        publish = body and pub_valid and pub_ready
        start_ready = not (rst or prepared or attempt or stopped or load_rsp or load_valid) and configured and idle and retired
        start = body and idle and start_valid and start_ready
        assert not (capture and publish) and not (initial and publish)
        assert not (prepared and (initial or capture or start))
        assert not capture or (configured and idle and payload_equal and design_equal)
        assert not publish or (prepared and idle)
        counts['stage_capture'] += bool(capture)
        counts['initial_descriptor_write'] += bool(initial)
        counts['publication'] += bool(publish)
        counts['prepared_start_blocked'] += bool(prepared and start_valid and not start)
    assert count == 1048576 and all(counts.values())
    # Bit projection of the active_payload concatenation: the 2272 non-version
    # bits are descriptor bits; only bits 2240..2271 select current_version.
    known_bits = 0
    for position in range(2304):
        for stored, current in product((0, 1), repeat=2):
            captured = current if 2240 <= position < 2272 else stored
            full_publication = captured
            retained_publication = captured if 2240 <= position < 2272 else stored
            assert full_publication == retained_publication
            known_bits += 1
    assert known_bits == 9216
    # Dropping all descriptor writes would not preserve the raw version slice.
    version_counterexample = dict(descriptor_version=0, current_version=1,
        captured_version=1, original_descriptor_after_publish=1, all_writes_removed=0)
    # Bit 0 is outside descriptor_ok's inspected fields and outside the patched
    # version slice. With all other policy rejection terms false, != yields X;
    # an if(X) does not take its true arm, so the original else accepts the X.
    unknown_counterexamples = []
    for value in ('x', 'z'):
        comparison = four_ne(value, '0')
        rejected = comparison == '1'
        assert comparison == 'x' and not rejected
        original_after_publish = value
        proposed_after_publish = '0'
        assert original_after_publish != proposed_after_publish
        unknown_counterexamples.append(dict(bit=0, descriptor_before='0', load_payload_bit=value,
            all_other_reject_terms='0', payload_not_equal=comparison, original_rejects=rejected,
            original_stage_captures=value, publication_ready='1',
            original_descriptor_after_publish=original_after_publish,
            retained_descriptor_after_publish=proposed_after_publish,
            externally_visible_difference='active_payload[0] and cfg_payload[0]'))
    # Locate all descriptor_ok slice accesses so bit-0's exclusion is explicit.
    fn = text.split('function descriptor_ok', 1)[1].split('end endfunction', 1)[0]
    inspected = [(int(a), int(b)) for a, b in re.findall(r'p\[(\d+)\+:(\d+)\]', fn)]
    assert inspected and all(not (a <= 0 < a + width) for a, width in inspected)
    out = ROOT / 'results/config_publication_retention_20261030.json'
    freeze = ROOT / 'results/config_publication_retention_sources_20261030'
    assert not out.exists() and not freeze.exists()
    bound = [Path(__file__).resolve(), source, manifest_file, baseline / 'manifest.json',
             nav_file, diag_file, TARGET / 'source_bound_audit.json',
             ROOT / 'results/checkpoint_edit_route_recovery_v1_restore_20261025.json']
    result = dict(status='binary_projection_checked_four_value_counterexample_found',
        source_sha256=sha(source), analyzer_sha256=sha(__file__), bound={str(p): sha(p) for p in bound},
        source_expressions=required, descriptor_ok_slices=inspected,
        binary_control_valuations=count, binary_events=dict(counts), binary_bit_projection_cases=known_bits,
        known_input_invariant_argument=[
            'Reset clears prepared. Successful stage capture requires configured and IDLE and captures active_payload.',
            'Under prepared, load branches reject overwriting initial/temporary payload and start_ready is false.',
            'While prepared remains set, state stays IDLE; DRAIN current_version update cannot execute.',
            'Reset, attempt reset, discard, abort/fail, or publication clears prepared. No other descriptor/shadow writes exist in this frozen source.',
            'Thus for reachable binary operation since reset, publication can retain the 2272 descriptor bits outside [2271:2240] while writing the 32 version bits.',
        ],
        version_slice_counterexample=version_counterexample,
        unknown_payload_counterexamples=unknown_counterexamples,
        conclusion='Do not claim unconditional equivalence or replace the baseline. The binary invariant does not cover X/Z payloads; the original source can stage and publish an unknown bit that a retained descriptor would hide.',
        rtl_generated=False, rtl_compiled=False, rtl_simulated=False, formal_proof=False,
        candidate_selected=False, timing_benefit_measured=False,
        limitations=['Python guard and bit projections plus a manually source-bound induction argument, not RTL equivalence.',
            'No fault injection into state/registers or unreset start-state guarantee.',
            'Native payload knownness has not been monitored in the full system.',
            'Initial-load write enable may remain on the same deep control cone even if publication writes are reduced.'],
        next_steps=['Reproduce the X/Z counterexample in the original RTL after the existing matrix owner releases the behavioral solver.',
            'Decide between a documented native binary-input specialization with actual-port monitors and a four-value-preserving structural transformation.',
            'Preserve load/start/publish/discard/attempt-reset/abort/backpressure tests and exact-cycle/full-bank comparisons.',
            'Only select a candidate after full-system audit/actual restore and matched synthesis/physical measurements.'])
    out.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    bound.append(out)
    freeze.mkdir()
    files = {}
    for i, source_file in enumerate(bound):
        name = f'{i:02d}_{source_file.name}'
        shutil.copyfile(source_file, freeze / name)
        files[name] = dict(source=str(source_file), sha256=sha(source_file))
        assert sha(freeze / name) == files[name]['sha256']
    (freeze / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
        scope='Source-bound model and counterexamples; no RTL or timing acceptance.'), indent=2, sort_keys=True) + '\n')
    print('CONFIG_PUBLICATION_MODEL', count, dict(counts), 'XZ_COUNTEREXAMPLES', len(unknown_counterexamples))


if __name__ == '__main__':
    main()
