"""Compare literal synthesized LUTs; never infer FSM encodings from net names."""
import json
import re
from host_edit_system_common_v1 import ROOT, BASE, read, sha, restored


def main():
    p = BASE/'config_native_publication_synth_v1'
    m, a, _ = restored(p)
    source = p/'synth.v'
    assert sha(source) == a['artifact_sha256']['synth.v']
    text = source.read_text()
    begin = text.index('\nmodule route_commit_controller\n')
    end = text.index('\nendmodule', begin)
    module = text[begin:end]

    def lut(instance):
        pattern = r'LUT(\d) #\(\s*\.INIT\((\d+)\x27h([0-9A-Fa-f]+)\)\)\s*'+re.escape(instance)+r'\s*\((.*?)\);'
        matches = list(re.finditer(pattern, module, re.S))
        assert len(matches) == 1, instance
        hit = matches[0]
        width = int(hit[1]); assert int(hit[2]) == 2**width
        pins = dict(re.findall(r'\.(I\d|O)\(([^)]+)\)', hit[4]))
        pins = {k: v.strip() for k, v in pins.items()}
        assert set(pins) == {'O'} | {f'I{i}' for i in range(width)}
        return dict(width=width, init=int(hit[3], 16), pins=pins, literal=hit[0])

    ready = lut('cp_s_ready_INST_0')
    handshake = lut('\\cp_stage[154][31]_i_3')
    enable = lut('\\cp_stage[154][31]_i_1')
    assert ready['width'] == 4 and handshake['width'] == 5 and enable['width'] == 3
    assert ready['pins']['O'] == 'cp_s_ready'
    for i in range(4): assert ready['pins'][f'I{i}'] == handshake['pins'][f'I{i}']
    assert handshake['pins']['I4'] == 'cp_s_valid'
    assert enable['pins']['I0'] == handshake['pins']['O']
    # Compare all valuations, including physically unreachable state encodings.
    for bits in range(32):
        r = (ready['init'] >> (bits & 15)) & 1
        h = (handshake['init'] >> bits) & 1
        assert h == (r & (bits >> 4))
    for bits in range(8):
        assert ((enable['init'] >> bits) & 1) == ((bits & 1) & (1-((bits >> 1) & 1)) & (1-(bits >> 2)))
    result = dict(status='source_bound_two_state_netlist_handshake_factor_verified',
        analyzer_sha256=sha(__file__), source_sha256=sha(source), source=str(source),
        synthesized_audit_sha256=sha(p/'source_bound_audit.json'),
        literal_luts=dict(ready=ready, handshake=handshake, enable=enable),
        handshake_valuations_checked=32, enable_valuations_checked=8,
        conclusion='In synthesized netlist, measured bank CE = cp_s_ready & cp_s_valid & ~B & ~C; '
            'B and C remain additional literal gate inputs, not removed or relabeled.',
        implications=['This CE requires the import-stream handshake at the optimized module boundary.',
            'It is not justified to describe this measured net as an export-capture enable.',
            'Complete routed CE loads were independently observed, but export storage/data mapping is a separate question.'],
        limitations=['Two-state local synthesized LUT identity, not four-state RTL equivalence.',
            'Synthesized and routed netlists are distinct; no claim all control aliases are unchanged.',
            'No RTL guard deletion, cycle change, or timing benefit demonstrated.'])
    out = ROOT/'results/native_stage_handshake_factor_20261030.json'
    assert not out.exists()
    out.write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    print('NATIVE_STAGE_HANDSHAKE_FACTOR_VERIFIED', 32, 8)


if __name__ == '__main__': main()
