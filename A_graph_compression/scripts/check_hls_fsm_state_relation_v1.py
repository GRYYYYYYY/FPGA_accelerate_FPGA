#!/usr/bin/env python3
"""Exhaustively check legal-state decoder relations on the actual candidate modules."""
import argparse
import json
import re
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic


def check_pair(original, candidate):
    pattern = r'^parameter\s+ap_ST_fsm_state(\d+)\s*=\s*(\d+)\x27d(\d+)\s*;$'
    old_rows = re.findall(pattern, original, re.M)
    new_rows = re.findall(pattern, candidate, re.M)
    count = len(old_rows)
    bits = max(1,(count-1).bit_length())
    require(count>0 and len(new_rows)==count, 'State count changed')
    old = {int(i):(int(w),int(v)) for i,w,v in old_rows}
    new = {int(i):(int(w),int(v)) for i,w,v in new_rows}
    require(len(old)==len(new)==count and set(old)==set(new)==set(range(1,count+1)), 'Incomplete state label domain')
    require(all(old[i]==(count,1<<(i-1)) and new[i]==(bits,i-1) for i in old), 'State relation/code width differs')
    require(len({value for width,value in new.values()})==count, 'Binary encoding is not injective')
    old_decodes = re.findall(r"^assign ap_CS_fsm_state(\d+) = ap_CS_fsm\[32'd(\d+)\];$",original,re.M)
    new_decodes = re.findall(r"^assign ap_CS_fsm_state(\d+) = \(ap_CS_fsm == (\d+)'d(\d+)\);$",candidate,re.M)
    old_map = {int(i):int(index) for i,index in old_decodes}
    new_map = {int(i):(int(width),int(value)) for i,width,value in new_decodes}
    require(len(old_map)==len(old_decodes)==len(new_map)==len(new_decodes) and set(old_map)==set(new_map), 'State predicates changed or duplicated')
    require(all(i in old and old_map[i]==i-1 and new_map[i]==(bits,i-1) for i in old_map), 'Predicate encoding mismatch')
    predicates = [(old_map[i],new_map[i][1]) for i in old_map]
    for state in range(1,count+1):
        onehot, binary = old[state][1],new[state][1]
        for bit_index, constant in predicates:
            if ((onehot>>bit_index)&1) != (binary==constant):
                raise ValueError('Decoder differs at legal state '+str(state))
    for text in (original,candidate):
        require(text.count('case (ap_CS_fsm)')==1, 'Ambiguous state transition case')
    old_case = original.split('case (ap_CS_fsm)',1)[1].split('endcase',1)[0]
    new_case = candidate.split('case (ap_CS_fsm)',1)[1].split('endcase',1)[0]
    require(old_case==new_case, 'Transition conditions or named targets changed')
    labels = list(map(int,re.findall(r'ap_ST_fsm_state(\d+)\s*:\s*begin',old_case)))
    targets = list(map(int,re.findall(r'ap_NS_fsm\s*=\s*ap_ST_fsm_state(\d+)\s*;',old_case)))
    require(len(labels)==count and set(labels)==set(old) and all(i in old for i in targets), 'Transition label/target outside legal codebook')
    require(old_case.count("ap_NS_fsm = 'bx;")==1, 'Unknown default not preserved')
    require(re.findall(r"^#0 ap_CS_fsm = (\d+)'d(\d+);$",original,re.M)==[(str(count),'1')], 'Original initialization changed')
    require(re.findall(r"^#0 ap_CS_fsm = (\d+)'d(\d+);$",candidate,re.M)==[(str(bits),'0')], 'Candidate initialization relation changed')
    for statement in ['ap_CS_fsm <= ap_ST_fsm_state1;', 'ap_CS_fsm <= ap_NS_fsm;']:
        require(original.count(statement)==candidate.count(statement)==1, 'Reset/register transfer changed')
    return dict(states=count, state_predicates=len(predicates), decoder_state_pairs_checked=count*len(predicates),
        named_transition_assignments_checked=len(targets), transition_case_bytes_unchanged=True,
        initialization_and_named_reset_mapping_checked=True,
        scope='All known legal control-state values and named next-state assignments; nonencoding-text/closure premises come from the independent edit audit')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--bundle',type=Path,required=True)
    parser.add_argument('--edit-audit',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    require(not args.output.exists(),'Refuse overwrite')
    edit = json.loads(args.edit_audit.read_text())
    require(edit['status']=='binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked','Missing checked nonencoding-text/closure premises')
    files = dict(edit['files'])
    for path, checksum in files.items():
        require(digest(path)==checksum,'Changed edit-audit evidence '+path)
    plan = json.loads((args.bundle/'plan.json').read_text())
    require(len(plan['modules'])==len(edit['modules'])==43,'Different candidate module set')
    modules = []
    for module in plan['modules']:
        record = check_pair(Path(module['original']).read_text(),Path(module['candidate']).read_text())
        modules.append(dict(module=module['module'],**record))
    for path in (Path(__file__).resolve(),args.edit_audit.resolve(),args.bundle.resolve()/'plan.json'):
        files[str(path)] = digest(path)
    atomic(args.output,dict(status='actual_candidate_legal_state_decoders_and_named_transition_relations_exhaustively_checked',
        modules=modules,legal_states_checked=sum(m['states'] for m in modules),
        decoder_state_pairs_checked=sum(m['decoder_state_pairs_checked'] for m in modules),
        named_transition_assignments_checked=sum(m['named_transition_assignments_checked'] for m in modules),files=files,
        full_rtl_executed=False,general_formal_equivalence_proven=False,
        limits=['Exhaustive known-legal-state arithmetic and identical transition-text checks, not whole-design SMT/RTL formal verification',
                'Arbitrary injected illegal/partly unknown state storage and unobserved transient behavior are outside this check',
                'Four-state mechanism regression is separate; original full capacity/transaction/output/C oracles remain required']))
    print('Modules',len(modules),'state/predicate pairs',sum(m['decoder_state_pairs_checked'] for m in modules))


if __name__=='__main__':
    main()
