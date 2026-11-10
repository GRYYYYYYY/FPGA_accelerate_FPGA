"""Source-bound four-value selector model; no RTL or timing acceptance."""
from pathlib import Path
from itertools import product
from collections import Counter
import json
import re
from run_checkpoint_authority import ROOT, sha

VALUES = ('0', '1', 'x', 'z')


def logical_and(*args):
    if '0' in args:
        return '0'
    return '1' if all(x=='1' for x in args) else 'x'


def logical_or(*args):
    if '1' in args:
        return '1'
    return '0' if all(x=='0' for x in args) else 'x'


def equal_literal(bits, value):
    literal = f'{value:04b}'
    if any(a in ('0','1') and a!=b for a,b in zip(bits,literal)):
        return '0'
    return 'x' if any(a in ('x','z') for a in bits) else '1'


def main():
    base = Path('/tmp/B_state_residency_offer_20261025')
    q = json.loads((base/'route_stage_synth_followup_v1/manifest.json').read_text())
    assert q['status']=='observed' and q['stage']=='complete'
    stage = base/'route_stage_synth_v1'
    m = json.loads((stage/'manifest.json').read_text())
    a = json.loads((stage/'source_bound_audit.json').read_text())
    receipt = ROOT/'results/route_stage_synth_v1_restore_20261025.json'
    restored = json.loads(receipt.read_text())
    assert a['status']==restored['status']=='passed' and restored['audit_byte_identical']
    assert a['manifest_sha256']==sha(stage/'manifest.json')
    assert restored['audit_sha256']==sha(stage/'source_bound_audit.json')
    path_file = ROOT/'results/route_stage_timing_path_20261029.json'
    path = json.loads(path_file.read_text())
    assert path['audit_sha256']==sha(stage/'source_bound_audit.json')
    selected_nets = [n for n in path['unplaced_data_nets'] if n['name']=='inner/host_fence/selected_ready']
    assert len(selected_nets)==1
    names = ['search_host_fence.sv','search_scheduler.sv','search_residency_system.sv']
    sources = {}
    for name in names:
        source = stage/'sources'/name
        assert sha(source)==m['sources'][name]
        sources[name] = source.read_text()
        # The planned selector study also applies to the CP and path references;
        # verify their actual source identity rather than inheriting a claim.
        for reference in ['checkpoint_edit_synth_v1','route_path_synth_v1']:
            rm = json.loads((base/reference/'manifest.json').read_text())
            assert sha(base/reference/'sources'/name)==rm['sources'][name]==m['sources'][name]
    fence = sources['search_host_fence.sv']
    allowed_expr = re.search(r'wire scheduler_lane=([^;]+);',fence)[1]
    assert allowed_expr=='c_lane==6||c_lane==8||c_lane==11||c_lane==12'
    allowed = tuple(map(int,re.findall(r'c_lane==(\d+)',allowed_expr)))
    cases = re.findall(r"4'd(\d+):begin selected_ready=s_ready\[(\d+)\];selected_valid=s_rsp_valid\[(\d+)\];selected_reply=s_rsp_payload\[(\d+)\+:256\];end",fence)
    assert len(cases)==16
    table = {}
    for lane,ready,valid,offset in cases:
        lane,ready,valid,offset = map(int,(lane,ready,valid,offset))
        assert lane==ready==valid and offset==lane*256 and lane not in table
        table[lane] = ready
    assert sorted(table)==list(range(16))
    required = [
        'selected_ready=0;selected_valid=0;selected_reply=0;',
        'case(c_lane)',
        'assign c_ready=search_busy&&scheduler_lane&&selected_ready;',
        "assign h_ready=host_open?s_ready:16'd0;",
    ]
    for expression in required:
        assert expression in fence, expression
    # There is exactly one external use of this combinational temporary.
    assert len(re.findall(r'\bselected_ready\b',fence))==19
    scheduler = sources['search_scheduler.sv']
    assert 'wire unexpected=reply_valid&&state!=WAIT_REPLY&&!(state==SEND&&req_ready);' in scheduler
    wrapper = sources['search_residency_system.sv']
    for expression in ['.c_ready(c_ready)','.req_ready(c_ready)','.s_ready(b_f_sr)',
                       '.f_sr(b_f_sr)','.h_ready(f_sr)']:
        assert expression in wrapper, expression

    # Each exact case reads one bit. Other bits have no fan-in in this source
    # expression. Unknown selector patterns hit the default zero. Thus projecting
    # s_ready to the selected bit represents every vector, not only one-hot data.
    counts = Counter()
    observed = Counter()
    for bits,busy,selected_bit in product(product(VALUES,repeat=4),VALUES,VALUES):
        lane = int(''.join(bits),2) if all(x in ('0','1') for x in bits) else None
        scheduler_lane = logical_or(*(equal_literal(bits,x) for x in allowed))
        original_selected = selected_bit if lane in table else '0'
        proposed_selected = selected_bit if lane in allowed else '0'
        original = logical_and(busy,scheduler_lane,original_selected)
        proposed = logical_and(busy,scheduler_lane,proposed_selected)
        assert original==proposed,(bits,busy,selected_bit,original,proposed)
        category = 'unknown_lane_default' if lane is None else 'allowed_lane' if lane in allowed else 'masked_lane'
        counts[category] += 1
        observed[original] += 1
    assert sum(counts.values())==4096 and observed['1'] and observed['x']
    # Removing the mask while retaining all sixteen selections would be wrong.
    counterexample = dict(lane=0,search_busy='1',selected_ready='1',
                          original=logical_and('1','0','1'),unmasked=logical_and('1','1'))
    assert counterexample['original']!=counterexample['unmasked']
    out = ROOT/'results/search_ready_selection_20261029.json'
    assert not out.exists()
    record = dict(status='source_bound_selector_model_passed_not_rtl_validation',
                  analyzer_sha256=sha(Path(__file__)),reference=str(stage),
                  reference_audit_sha256=sha(stage/'source_bound_audit.json'),
                  restoration_sha256=sha(receipt),timing_path_sha256=sha(path_file),
                  source_sha256={name:m['sources'][name] for name in names},
                  same_sources_in=['checkpoint_edit_synth_v1','route_path_synth_v1'],
                  checked_source_expressions=required,
                  original_ready_inputs=list(table),proposed_ready_inputs=list(allowed),
                  valuations=dict(counts),output_values=dict(observed),
                  required_mask_counterexample=counterexample,reported_selected_ready_net=selected_nets[0],
                  proposed_change='Keep the existing scheduler_lane mask and full selected_valid/reply cases. Only leave selected_ready at its zero default in the twelve non-scheduler cases. Host h_ready and all sixteen host lanes remain unchanged.',
                  scope='Bounded four-value Python model tied to literal static case assignments and the sole selected_ready consumer. Not compiled RTL, formal equivalence, new full-system coverage, mapped mux-size proof or physical timing benefit. Unknown selector patterns use the original case default; X/Z data propagate through the same logical mask.',
                  next_steps=['After current physical measurement, choose a separately versioned selector experiment if warranted',
                              'Compare all external outputs in original/default/reduced RTL, including X/Z selectors and invalid lanes',
                              'Preserve scheduler fault/cancel/backpressure and all host service tests',
                              'Full-system exact outputs/cycles and restored matched synthesis/physical measurement before selection'])
    out.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('SEARCH_READY_SELECTION_MODEL',dict(counts),dict(observed))


if __name__=='__main__':
    main()
