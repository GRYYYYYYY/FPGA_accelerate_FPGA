#!/usr/bin/env python3
"""Create an isolated FSM encoding candidate with exact source edit ledgers."""
import argparse
import hashlib
import json
import re
import shutil
from pathlib import Path
from audit_hls_fsm_shape_v3 import audit_module
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic


def transform(text):
    shape = audit_module(text)
    count, bits = shape['states'], shape['minimum_binary_width']
    edits = []

    def replace(pattern, kind, convert):
        for match in re.finditer(pattern, text, re.M):
            edits.append(dict(start=match.start(), end=match.end(), old=match[0], new=convert(match), kind=kind))

    replace(r'^parameter\s+ap_ST_fsm_state(\d+)\s*=\s*\d+\x27d\d+\s*;', 'state_constant',
            lambda m: re.sub(r"\d+'d\d+", str(bits)+"'d"+str(int(m[1])-1), m[0]))
    replace(r'^\(\* fsm_encoding = "none" \*\) reg\s+\[\d+:0\] ap_CS_fsm;', 'cs_width',
            lambda m: re.sub(r'\[\d+:0\]', '['+str(bits-1)+':0]', m[0]))
    replace(r'^reg\s+\[\d+:0\] ap_NS_fsm;', 'ns_width',
            lambda m: re.sub(r'\[\d+:0\]', '['+str(bits-1)+':0]', m[0]))
    replace(r"^#0 ap_CS_fsm = \d+'d1;", 'initial_state', lambda m: "#0 ap_CS_fsm = "+str(bits)+"'d0;")
    replace(r"^assign ap_CS_fsm_state(\d+) = ap_CS_fsm\[32'd(\d+)\];", 'state_decode',
            lambda m: 'assign ap_CS_fsm_state'+m[1]+' = (ap_CS_fsm == '+str(bits)+"'d"+m[2]+');')
    edits.sort(key=lambda e:e['start'])
    require(sum(e['kind']=='state_constant' for e in edits)==count, 'Incomplete state codebook conversion')
    previous = 0
    for edit in edits:
        require(previous <= edit['start'] < edit['end'], 'Overlapping edits')
        previous = edit['end']
    candidate = text
    for edit in reversed(edits):
        candidate = candidate[:edit['start']]+edit['new']+candidate[edit['end']:]
    ledger = dict(input_sha256=hashlib.sha256(text.encode()).hexdigest(), output_sha256=hashlib.sha256(candidate.encode()).hexdigest(),
        states=count, original_width=count, candidate_width=bits, encoding='original state i maps to binary integer i-1',
        edits=edits, limits=['Candidate only; original-source shape acceptance is not candidate equivalence or RTL acceptance'])
    return candidate, ledger


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--shape-audit', type=Path, required=True)
    parser.add_argument('--rtl-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, required=True)
    args = parser.parse_args()
    shape = json.loads(args.shape_audit.read_text())
    for path, checksum in shape['files'].items():
        require(digest(path)==checksum, 'Changed original shape audit input')
    eligible = {m['module'] for m in shape['modules']}
    output = args.output_dir.resolve()
    output.mkdir(exist_ok=False)
    (output/'verilog').mkdir()
    (output/'ledgers').mkdir()
    files, modules, retained = {}, [], []
    for source in sorted(args.rtl_dir.resolve().iterdir()):
        if not source.is_file() or source.suffix not in ('.v', '.sv', '.dat'):
            continue
        target = output/'verilog'/source.name
        files[str(source)] = digest(source)
        if source.stem in eligible and source.suffix=='.v':
            candidate, ledger = transform(source.read_text())
            target.write_text(candidate)
            ledger_path = output/'ledgers'/(source.stem+'.json')
            atomic(ledger_path, ledger)
            files[str(ledger_path)] = digest(ledger_path)
            modules.append(dict(module=source.stem, original=str(source), candidate=str(target), ledger=str(ledger_path),
                                states=ledger['states'], original_width=ledger['original_width'], candidate_width=ledger['candidate_width']))
        else:
            shutil.copyfile(source, target)
            require(digest(target)==digest(source), 'Retained source changed')
            retained.append(dict(original=str(source), candidate=str(target)))
        files[str(target)] = digest(target)
    require({m['module'] for m in modules}==eligible, 'Eligible module set differs')
    for path in (args.shape_audit.resolve(), Path(__file__).resolve(), Path(__file__).with_name('audit_hls_fsm_shape_v3.py')):
        files[str(path)] = digest(path)
    atomic(output/'plan.json', dict(status='isolated_binary_control_fsm_candidate_generated_not_simulated', modules=modules,
        retained=retained, files=files, original_rtl_dir=str(args.rtl_dir.resolve()),
        full_rtl_execution=False, candidate_equivalence_proven=False,
        limits=['All original RTL/ROM/model filenames retained; unsupported modules copied unchanged',
                'Only declared FSM representation edited; ledger checker and four-state/reset checks still required',
                'No compilation, synthesis, platform execution or speedup claim']))
    print('Candidate modules',len(modules),'unchanged files',len(retained))


if __name__=='__main__':
    main()
