"""Check the actual native feedback wiring, preserving four-value distinctions."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')
VALUES = ('0', '1', 'x', 'z')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def neg(a):
    return {'0': '1', '1': '0', 'x': 'x', 'z': 'x'}[a]


def land(*args):
    return '0' if '0' in args else '1' if all(x == '1' for x in args) else 'x'


def lor(*args):
    return '1' if '1' in args else '0' if all(x == '0' for x in args) else 'x'


def mux(select, yes, no):
    if select == '1':
        return yes
    if select == '0':
        return no
    return yes if yes == no else 'x'


def stage_capture(front_handshake, prepared, configured, permit, authoritative,
                  bad_design, bad_checkpoint, bad_descriptor, bad_payload):
    # Procedural if takes its true arm only when the logical condition is 1.
    if front_handshake != '1':
        return False
    if lor(prepared, land(neg(permit), configured)) == '1':
        return False
    if permit != '1':
        return False  # The original else-if(load_stage) does not take X/Z.
    reject = lor(neg(permit), neg(configured), neg(authoritative), bad_design,
                 bad_checkpoint, bad_descriptor, bad_payload)
    return reject != '1'


def main():
    physical = BASE / 'checkpoint_edit_route_recovery_v1'
    mfile = physical / 'manifest.json'; m = json.loads(mfile.read_text())
    assert m['status'] == 'observed' and m['stage'] == 'complete'
    cfile = physical / 'sources/config_restore_controller.sv'
    sfile = physical / 'sources/residency_system.sv'
    c = cfile.read_text(); s = sfile.read_text()
    for f in [cfile, sfile]:
        assert sha(f) == m['inputs']['sources/' + f.name]
        sm = json.loads((BASE / 'checkpoint_edit_synth_v1/manifest.json').read_text())
        assert sha(f) == sm['sources'][f.name]
    model_file = ROOT / 'results/config_publication_retention_20261030.json'
    model = json.loads(model_file.read_text())
    assert model['source_sha256'] == sha(cfile)
    freeze = ROOT / 'results/config_publication_retention_sources_20261030'
    for name, entry in json.loads((freeze / 'manifest.json').read_text())['files'].items():
        assert sha(freeze / name) == entry['sha256'] == sha(entry['source'])
    for expression in model['source_expressions']:
        assert expression in c
    # All occurrences of this wire are the declaration, one output driver and
    # the conditional input of the SAME instance. Preserve the whole source SHA.
    topology = [
        'wire[2303:0]jp_effective;',
        'config_restore_controller #(.MAX_CYCLES(1048576))config_restore(',
        '.load_stage(jp_permit)', '.publish_permit(jp_permit)',
        '.active_payload(jp_effective)',
        '.load_payload(jp_permit?jp_effective:(fd_fc_payload))',
        ".load_authoritative(jp_permit?1'b1:(fd_fc_authoritative))",
    ]
    assert all(x in s for x in topology)
    assert len(re.findall(r'\bjp_effective\b', s)) == 3
    instance = s.split('config_restore_controller #(.MAX_CYCLES(1048576))config_restore(', 1)[1].split('\n', 1)[0]
    assert all(x in instance for x in topology[2:])
    assert re.findall(r'\bprepared\s*<=\s*([^;]+);', c) == ['0', '0', '1', '0', '0']
    assert re.findall(r'\bconfigured\s*<=\s*([^;]+);', c) == ['0', '1']
    assert set(re.findall(r'\bstate\s*<=\s*([^;]+);', c)) <= {'IDLE', 'FIRST', 'OTHERS', 'DRAIN', 'DONE'}
    assert re.findall(r'\bdescriptor\s*<=\s*([^;]+);', c) == ['0', 'load_payload', 'shadow_payload']
    counts = Counter(); captures = Counter(); aliases = Counter()
    # All four-value rejection predicates, projected independently; this is a
    # conservative superset of reachable data/descriptor predicate combinations.
    for prepared, configured in product(('0', '1'), repeat=2):
        for front, permit, auth, bad_d, bad_cp, bad_desc, bad_p in product(VALUES, repeat=7):
            counts['guard_projections'] += 1
            capture = stage_capture(front, prepared, configured, permit, auth, bad_d, bad_cp, bad_desc, bad_p)
            if capture:
                assert prepared == '0' and configured == permit == front == '1'
                reject = lor(neg(permit), neg(configured), neg(auth), bad_d, bad_cp, bad_desc, bad_p)
                captures[reject] += 1
    assert counts['guard_projections'] == 65536 and captures['0'] and captures['x']
    for is_version, configured in product((False, True), repeat=2):
        for permit, descriptor, current_version, host_payload in product(VALUES, repeat=4):
            counts['feedback_bit_projections'] += 1
            active = mux('1' if configured else '0', current_version if is_version else descriptor, '0')
            load = mux(permit, active, host_payload)
            authoritative = mux(permit, '1', host_payload)
            # True stage capture forces the selector and configured to one,
            # regardless of X/Z in unrelated guards or the carried data bit.
            if permit == '1' and configured:
                assert load == active and authoritative == '1'
                full_publish = load
                partial_publish = load if is_version else descriptor
                assert full_publish == partial_publish
                aliases[full_publish] += 1
    assert counts['feedback_bit_projections'] == 1024
    assert sum(aliases.values()) == 128 and all(aliases[x] for x in VALUES)
    # Under prepared=1 the first load rejection is known 1 even with X/Z
    # load_stage; start_ready contains !prepared and is known 0.
    stability = 0
    for permit, other_start_guard in product(VALUES, repeat=2):
        assert lor('1', land(neg(permit), '1')) == '1'
        assert land(neg('1'), other_start_guard) == '0'
        stability += 1
    assert stability == 16
    broken_alias = dict(permit='1', configured='1', descriptor_bit='0', host_payload_bit='x',
        correct_feedback_bit=mux('1', '0', 'x'), wrongly_selected_host_bit='x',
        original_generic_reject_condition='x', generic_capture=True,
        generic_full_publish='x', retained_publish='0')
    assert broken_alias['correct_feedback_bit'] != broken_alias['wrongly_selected_host_bit']
    out = ROOT / 'results/config_native_feedback_20261030.json'
    frozen = ROOT / 'results/config_native_feedback_sources_20261030'
    assert not out.exists() and not frozen.exists()
    bound = [Path(__file__).resolve(), cfile, sfile, mfile, model_file,
             ROOT / 'results/checkpoint_edit_route_recovery_timing_20261030.json',
             ROOT / 'results/checkpoint_edit_route_recovery_v1_restore_20261025.json']
    report = dict(status='native_feedback_four_value_projection_passed_not_rtl_equivalence',
        bound={str(f): sha(f) for f in bound}, topology_expressions=topology,
        jp_effective_occurrences=3, valuations=dict(counts), capture_reject_values=dict(captures),
        publication_bit_values=dict(aliases), prepared_stability_projections=stability,
        binary_control_origin='After a real reset, state/prepared/configured are assigned only constants; data registers may retain X/Z.',
        invariant_argument=[
            'A successful stage branch requires load_stage to evaluate exactly 1; load_stage and the payload mux selector are the same jp_permit wire.',
            'With jp_permit=1, load_payload is the exact active_payload of this same controller, including X/Z, and authoritative is 1.',
            'Stage rejection cannot be bypassed with configured=0 because !configured is a known true rejection term; prepared=1 rejects all loads even if stage is X/Z.',
            'While prepared stays asserted, start_ready is known 0, the IDLE state cannot transition to recovery, initial/shadow loads are rejected, and no descriptor write can occur before publication.',
            'Reset/cancel/discard/attempt reset clear preparation; publication copies the 32 version bits but all 2272 other bits already match the shadow bit-for-bit, including X/Z.',
        ],
        generic_counterexample_retained=broken_alias,
        implication='A separately flagged controller specialization could retain the non-version descriptor bits under the native self-feedback contract without assuming all payload bits are known. Generic interface behavior must remain the default.',
        limits=['This is source-bound four-value Python projection plus an induction argument, not RTL formal or simulation.',
            'Do not remove saved_design/saved_checkpoint/current_version updates: those are not established as the same native feedback bits.',
            'No arbitrary unreset state, hierarchical force, or register upset equivalence.',
            'No measured area or timing benefit; initial load may retain the deep write-enable cone.'],
        production_rtl_changed=False, candidate_selected=False, timing_benefit_measured=False,
        next_steps=['First execute the already prepared original-controller generic X/Z probe after the CP matrix is released.',
            'Create an isolated default-off specialization only with explicit native feedback wiring and exact actual-port alias monitors.',
            'Cover binary and X/Z initial descriptors, generic counterexamples, version advancement, cancellation and every-cycle full descriptor equality in native/default/baseline RTL.',
            'Require complete-system output/cycle comparison, actual restore, and matched physical measurement before selecting the variant.'])
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    bound.append(out); frozen.mkdir(); files = {}
    for i, f in enumerate(bound):
        name = f'{i:02d}_{f.name}'; shutil.copyfile(f, frozen / name)
        files[name] = dict(source=str(f), sha256=sha(f)); assert sha(frozen / name) == files[name]['sha256']
    (frozen / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
        scope='Native topology and four-value model only; not a candidate or timing acceptance.'), indent=2, sort_keys=True) + '\n')
    print('NATIVE_FEEDBACK_MODEL', dict(counts), dict(captures), dict(aliases))


if __name__ == '__main__':
    main()
