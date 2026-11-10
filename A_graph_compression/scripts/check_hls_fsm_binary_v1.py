#!/usr/bin/env python3
"""Independently replay candidate edits and check every encoding-map obligation."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from audit_hls_fsm_shape_v3 import audit_module
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic


def check_delta(old, new, ledger):
    shape = audit_module(old)
    count, bits = shape['states'], max(1, (shape['states']-1).bit_length())
    require((ledger['states'],ledger['original_width'],ledger['candidate_width'])==(count,count,bits), 'Wrong encoding dimensions')
    require(hashlib.sha256(old.encode()).hexdigest()==ledger['input_sha256'], 'Wrong original digest')
    expected_counts = dict(state_constant=count, cs_width=1, ns_width=1, initial_state=1, state_decode=shape['access_counts']['decodes'])
    counts = dict.fromkeys(expected_counts, 0)
    codebook, previous = set(), 0
    for edit in ledger['edits']:
        start, end, before, after, kind = (edit[k] for k in ('start','end','old','new','kind'))
        require(previous<=start<end<=len(old) and old[start:end]==before, 'Overlapping or false edit span')
        previous = end
        require(kind in counts, 'Unapproved edit kind')
        counts[kind] += 1
        if kind=='state_constant':
            m = re.fullmatch(r"(parameter\s+ap_ST_fsm_state(\d+)\s*=\s*)(\d+)'d(\d+)(\s*;)", before)
            require(m is not None, 'Not a state parameter')
            index = int(m[2])
            require(1<=index<=count and index not in codebook and int(m[3])==count and int(m[4])==1<<(index-1), 'Invalid onehot mapping')
            codebook.add(index)
            require(after==m[1]+str(bits)+"'d"+str(index-1)+m[5], 'Wrong binary state value or extra parameter edit')
        elif kind in ('cs_width','ns_width'):
            name = 'ap_CS_fsm' if kind=='cs_width' else 'ap_NS_fsm'
            require(re.search(r'\b'+name+r';$', before) is not None and '['+str(count-1)+':0]' in before, 'Wrong state register width')
            require(after==before.replace('['+str(count-1)+':0]', '['+str(bits-1)+':0]',1), 'Extra declaration modification')
        elif kind=='initial_state':
            require(before=="#0 ap_CS_fsm = "+str(count)+"'d1;" and after=="#0 ap_CS_fsm = "+str(bits)+"'d0;", 'Initial state mapping differs')
        else:
            m = re.fullmatch(r"assign ap_CS_fsm_state(\d+) = ap_CS_fsm\[32'd(\d+)\];", before)
            require(m is not None, 'Not an original state-bit decode')
            index = int(m[1])
            require(1<=index<=count and int(m[2])==index-1, 'Incorrect original decode')
            require(after=='assign ap_CS_fsm_state'+str(index)+' = (ap_CS_fsm == '+str(bits)+"'d"+str(index-1)+');', 'Incorrect mapped decode or four-state comparison')
    require(counts==expected_counts and codebook==set(range(1,count+1)), 'Incomplete state or access conversion')
    replay = old
    for edit in reversed(ledger['edits']):
        replay = replay[:edit['start']]+edit['new']+replay[edit['end']:]
    require(replay==new and hashlib.sha256(new.encode()).hexdigest()==ledger['output_sha256'], 'Unlisted candidate modification')
    return dict(states=count, original_width=count, candidate_width=bits, counts=counts,
                nonencoding_source_bytes_preserved=True, original_legal_state_closure_checked=True,
                decode_truth_under_legal_state_mapping='onehot bit j equals (binary_state == j) for each original legal state')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    require(not args.output.exists(), 'Refuse overwrite')
    plan = json.loads((args.bundle/'plan.json').read_text())
    files = dict(plan['files'])
    for path, checksum in files.items():
        require(digest(path)==checksum, 'Changed candidate preparation input '+path)
    originals = Path(plan['original_rtl_dir'])
    expected = {p.name for p in originals.iterdir() if p.is_file() and p.suffix in ('.v','.sv','.dat')}
    actual = {p.name for p in (args.bundle/'verilog').iterdir() if p.is_file()}
    require(expected==actual, 'Complete RTL/ROM/model file set changed')
    seen, records = set(), []
    for module in plan['modules']:
        source, target, ledger = (Path(module[k]) for k in ('original','candidate','ledger'))
        require(source.name==target.name and source.name not in seen, 'Duplicate or renamed module')
        seen.add(source.name)
        records.append(dict(module=module['module'], **check_delta(source.read_text(),target.read_text(),json.loads(ledger.read_text()))))
    for row in plan['retained']:
        source, target = Path(row['original']), Path(row['candidate'])
        require(source.name==target.name and source.name not in seen and digest(source)==digest(target), 'Retained file changed')
        seen.add(source.name)
    require(seen==expected, 'Unaccounted source file')
    for path in (args.bundle/'plan.json', Path(__file__).resolve(), Path(__file__).with_name('audit_hls_fsm_shape_v3.py')):
        files[str(path.resolve())] = digest(path)
    atomic(args.output, dict(status='binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked', modules=records,
        retained_files=len(plan['retained']), files=files, full_rtl_executed=False, general_formal_equivalence_proven=False,
        limits=['Structural mapping under the checked initialized legal-state invariant; arbitrary injected illegal states are not covered',
                'No states, transitions, capacities, ports, ROM, AXI models or nonencoding source logic removed',
                'Four-state/reset regression and original full transaction/output/C oracles still required',
                'No measured memory reduction, implementation fit or acceleration claim']))
    print('Checked mappings',len(records),'retained files',len(plan['retained']))


if __name__=='__main__':
    main()
