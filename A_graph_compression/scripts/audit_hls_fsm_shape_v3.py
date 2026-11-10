#!/usr/bin/env python3
"""Fail-closed audit of generated onehot FSM access and transition shapes."""
import argparse
import json
import re
from pathlib import Path
from check_vitis_kernel import digest
from run_compact_native_stack_recovery_v1 import atomic


class ShapeError(ValueError):
    pass


def demand(condition, message):
    if not condition:
        raise ShapeError(message)


class BranchParser:
    """Accept only blocks, if/else, and named-state assignments; track totality."""
    def __init__(self, text, states):
        self.text, self.states, self.pos = text, states, 0

    def consume(self, pattern):
        match = re.match(r'\s*(?:'+pattern+r')', self.text[self.pos:])
        if match:
            self.pos += match.end()
        return match

    def statement(self):
        if self.consume(r'begin\b'):
            assigned = False
            while not self.consume(r'end\b'):
                before = self.pos
                assigned = self.statement() or assigned
                demand(self.pos > before, 'Parser made no progress')
            return assigned
        if self.consume(r'if\s*\('):
            depth = 1
            start = self.pos
            while self.pos < len(self.text) and depth:
                char = self.text[self.pos]
                demand(char not in '"{};`', 'Unsupported condition syntax')
                depth += (char == '(') - (char == ')')
                self.pos += 1
            demand(depth == 0 and self.pos > start+1, 'Unbalanced/empty condition')
            yes = self.statement()
            no = self.statement() if self.consume(r'else\b') else False
            return yes and no
        assignment = self.consume(r'ap_NS_fsm\s*=\s*ap_ST_fsm_state(\d+)\s*;')
        demand(assignment is not None, 'Unsupported transition statement at '+self.text[self.pos:self.pos+80])
        demand(int(assignment[1]) in self.states, 'Transition to missing state')
        return True


def audit_module(text):
    # Every reference to state storage/constants must be in a supported full line.
    parameters = re.findall(r'^parameter\s+ap_ST_fsm_state(\d+)\s*=\s*(\d+)\x27d(\d+)\s*;$', text, re.M)
    demand(parameters, 'No supported FSM parameters')
    count = len(parameters)
    ids = {int(i) for i, width, value in parameters}
    demand(ids == set(range(1, count+1)), 'Duplicate or noncontiguous state IDs')
    demand(all(int(width) == count and int(value) == 1 << (int(i)-1) for i, width, value in parameters), 'Invalid onehot codebook')
    counts = dict(cs_decl=0, ns_decl=0, initial=0, reset=0, transfer=0, case=0, unknown_default=0, decodes=0, assignments=0, labels=0)
    for line in text.splitlines():
        if not re.search(r'\b(?:ap_CS_fsm|ap_NS_fsm|ap_ST_fsm_state\d+)\b', line):
            continue
        line = line.strip()
        if re.fullmatch(r'parameter\s+ap_ST_fsm_state\d+\s*=\s*\d+\x27d\d+\s*;', line):
            continue
        m = re.fullmatch(r'\(\* fsm_encoding = "none" \*\) reg\s+\[(\d+):0\] ap_CS_fsm;', line)
        if m:
            demand(int(m[1])+1 == count, 'CS width mismatch'); counts['cs_decl'] += 1; continue
        m = re.fullmatch(r'reg\s+\[(\d+):0\] ap_NS_fsm;', line)
        if m:
            demand(int(m[1])+1 == count, 'NS width mismatch'); counts['ns_decl'] += 1; continue
        m = re.fullmatch(r'#0 ap_CS_fsm = (\d+)\x27d1;', line)
        if m:
            demand(int(m[1]) == count, 'Initial width mismatch'); counts['initial'] += 1; continue
        if line == 'ap_CS_fsm <= ap_ST_fsm_state1;':
            counts['reset'] += 1; continue
        if line == 'ap_CS_fsm <= ap_NS_fsm;':
            counts['transfer'] += 1; continue
        if line == 'case (ap_CS_fsm)':
            counts['case'] += 1; continue
        if line == "ap_NS_fsm = 'bx;":
            counts['unknown_default'] += 1; continue
        m = re.fullmatch(r'assign ap_CS_fsm_state(\d+) = ap_CS_fsm\[32\x27d(\d+)\];', line)
        if m:
            demand(int(m[1]) in ids and int(m[2]) == int(m[1])-1, 'State-bit decode mismatch')
            counts['decodes'] += 1; continue
        m = re.fullmatch(r'ap_NS_fsm = ap_ST_fsm_state(\d+);', line)
        if m:
            demand(int(m[1]) in ids, 'Unknown transition target'); counts['assignments'] += 1; continue
        m = re.fullmatch(r'ap_ST_fsm_state(\d+) : begin', line)
        if m:
            demand(int(m[1]) in ids, 'Unknown case label'); counts['labels'] += 1; continue
        raise ShapeError('Unsupported state use: '+line[:160])
    demand(all(counts[key] == 1 for key in ('cs_decl', 'ns_decl', 'initial', 'reset', 'transfer', 'case', 'unknown_default')), 'Missing or duplicate state storage operation')
    # Restrict register updates to the standard clocked reset/next-state block.
    demand(re.search(r'initial begin\s*#0 ap_CS_fsm = '+str(count)+r"'d1;", text) is not None, 'Initialization is not an unconditional first statement')
    clocked = re.findall(r'always @ \(posedge ap_clk\) begin\s*if \((?:ap_rst|ap_rst_n_inv) == 1\x27b1\) begin\s*ap_CS_fsm <= ap_ST_fsm_state1;\s*end else begin\s*ap_CS_fsm <= ap_NS_fsm;\s*end\s*end', text)
    demand(len(clocked) == 1, 'Unsupported reset/clock transfer context')
    match = re.search(r'always @ \(\*\) begin\s*case \(ap_CS_fsm\)(.*?)endcase\s*end', text, re.S)
    demand(match is not None, 'FSM case not in canonical combinational block')
    parser = BranchParser(match[1], ids)
    labels = []
    while True:
        label = parser.consume(r'ap_ST_fsm_state(\d+)\s*:')
        if label is None:
            break
        labels.append(int(label[1]))
        demand(parser.statement(), 'A transition branch may retain unknown/unassigned next state')
    demand(parser.consume(r"default\s*:\s*begin\s*ap_NS_fsm\s*=\s*'bx;\s*end") is not None, 'Unknown default was changed or moved')
    demand(not parser.text[parser.pos:].strip(), 'Unsupported statements after case branches')
    demand(len(labels) == count and set(labels) == ids, 'Missing or duplicate legal-state case branch')
    return dict(states=count, onehot_width=count, minimum_binary_width=max(1, (count-1).bit_length()), access_counts=counts,
                initialized_and_reset_to_state1=True, every_legal_state_branch_assigns_a_named_legal_next_state=True,
                unknown_default_preserved_and_unreachable_from_initialized_legal_states=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rtl-dir', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    demand(not args.output.exists(), 'Refuse overwrite')
    files, modules, rejected = {}, [], []
    for path in sorted(args.rtl_dir.resolve().glob('*.v')):
        text = path.read_text()
        if 'ap_ST_fsm_state' not in text:
            continue
        files[str(path)] = digest(path)
        try:
            modules.append(dict(module=path.stem, **audit_module(text)))
        except ShapeError as error:
            rejected.append(dict(module=path.stem, reason=str(error)))
    demand(modules or rejected, 'No FSM modules examined')
    files[str(Path(__file__).resolve())] = digest(__file__)
    result = dict(status='generated_control_fsm_shape_audited_no_candidate_created', modules=modules, rejected_modules=rejected,
        files=files, candidate_generated=False, rtl_equivalence_proven=False,
        limits=['Strict original-source shape and legal-state closure audit only',
                'No candidate RTL, semantic encoding-map proof or simulation acceptance established',
                'Four-state/reset/output behavior must be checked before relying on a recoded design'])
    atomic(args.output, result)
    print('Eligible', len(modules), 'rejected', len(rejected))


if __name__ == '__main__':
    main()
