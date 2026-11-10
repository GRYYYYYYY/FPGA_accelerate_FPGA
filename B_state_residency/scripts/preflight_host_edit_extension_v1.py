"""Test insertion and log-parser rejection using explicitly artificial suffixes."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json

ROOT = Path(__file__).resolve().parents[1]
VARIANT = ROOT / 'hardware/variants/checkpoint_host_edit_system_v1'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    value = importlib.util.module_from_spec(spec); spec.loader.exec_module(value)
    return value


def main():
    builder_file = VARIANT / 'build.py'
    parser_file = ROOT / 'scripts/check_host_edit_trace_v1.py'
    for file in [builder_file, parser_file, Path(__file__)]:
        ast.parse(file.read_text())
    builder = module('host_edit_builder_preflight', builder_file)
    parser = module('host_edit_parser_preflight', parser_file)
    original, binding = builder.evidence()
    generated = builder.instrument(original)
    rejected_insertions = []
    for name, bad in [
        ('missing_anchor', original.replace(builder.MARKER, '')),
        ('duplicate_anchor', original + '\n' + builder.MARKER),
        ('already_has_host_write', original + '\nlabel_write(1,3,0);'),
        ('double_instrumentation', generated),
    ]:
        try:
            builder.instrument(bad)
        except AssertionError:
            rejected_insertions.append(name)
        else:
            raise AssertionError(name)
    old_file = builder.REFERENCE / 'pressure/natural_trace.txt'
    old_trace = old_file.read_text()
    old_lines = old_trace.splitlines(keepends=True)
    stop = next(i for i, line in enumerate(old_lines) if line.startswith('FOURTH_PASS '))
    prefix = ''.join(old_lines[:stop + 1]); start = int(old_lines[stop].split()[1])
    clean = [int(line.split()[3], 16) for line in prefix.splitlines() if line.startswith('FOURTH_QUERY_WORD ')]
    dirty = [word ^ (0x80 if i == 7 else 0) for i, word in enumerate(clean)]
    ccrc, dcrc = parser.crc(clean), parser.crc(dirty)
    label = (180330 << 96) | 0x12345678
    rows = [f'HOST_EDIT_CLEAN_WORD {start} {i} {word:08x}' for i, word in enumerate(clean)]
    rows += [f'HOST_EDIT_BEGIN {start} {ccrc:08x} 3 20',
             f'HOST_EDIT_LABEL_BEFORE {start+2} {label:040x}',
             f'HOST_EDIT_WRITE {start+4} 66893 3 0002c06a',
             f'HOST_EDIT_WRITE_REPLY {start+6} 0',
             f'HOST_EDIT_LABEL_AFTER {start+8} {label:040x}']
    for i, word in enumerate(dirty):
        rows += [f'HOST_EDIT_DIRTY_WORD {start+10+i} {i} {word:08x}',
                 f'QCM 9 {i} {word:08x} {int(i==9)}']
    rows += [f'QCP 9 0 {dcrc:08x} 0 180330', f'HOST_EDIT_CP_REPLY {start+22} 2 0 {dcrc:08x} 0']
    for index, phase, words, checksum, status, delta in [
        (10, 3, clean, ccrc, 1, 23), (11, 4, dirty, dcrc, 0, 26),
    ]:
        rows += [f'QCS {index} {i} {word:08x} {int(i==9)}' for i, word in enumerate(words)]
        rows += [f'HOST_EDIT_CP_CHECK {start+delta} {phase} {checksum:08x} {checksum:08x} 1 {int(phase==4)} 0 0 0 0 0 0 1 180330 180330',
                 f'QCP {index} {status} {checksum:08x} 1 180330',
                 f'HOST_EDIT_CP_REPLY {start+delta+2} {phase} {status} {checksum:08x} 1']
    rows += [f'HOST_EDIT_PASS {start+30} 3 3 1 1 3 3 20 10 1 1 20 30 {ccrc:08x} {dcrc:08x} 0 1 180330 15 0']
    suffix = '\n'.join(rows) + '\n'
    stdout = ('HOST_EDIT_NATIVE_PASS writes=1 replies=1 clean_rejected=1 dirty_accepted=1 atomic_checks=20\n'
              'CHECKPOINT_EDIT_EXCLUSION_PASS cycles=4828845 safe=65030 edit=1 busy=400 requests=15 replies=15 imports=60 exports=90\n')
    parsed = parser.check(prefix + suffix, stdout, old_trace)
    assert parsed['host_edit_events'] == 31 and parsed['actual_raw_cp_records'] == 33
    def replace_once(text, old, new):
        assert text.count(old) == 1, old
        return text.replace(old, new, 1)
    bad_suffixes = {
        'different_label': replace_once(suffix, f'HOST_EDIT_LABEL_AFTER {start+8} {label:040x}', f'HOST_EDIT_LABEL_AFTER {start+8} {label^1:040x}'),
        'wrong_write_field': replace_once(suffix, f'HOST_EDIT_WRITE {start+4} 66893 3', f'HOST_EDIT_WRITE {start+4} 66893 2'),
        'wrong_dirty_word': replace_once(suffix, f'HOST_EDIT_DIRTY_WORD {start+17} 7 000000e2', f'HOST_EDIT_DIRTY_WORD {start+17} 7 000000e3'),
        'wrong_raw_stream': replace_once(suffix, 'QCS 10 7 00000062 0', 'QCS 10 7 000000e2 0'),
        'missing_raw_word': replace_once(suffix, 'QCS 10 7 00000062 0\n', ''),
        'alternative_metadata_cause': replace_once(suffix, f'1 0 0 0 0 0 0 0 1 180330 180330\n', '1 0 1 0 0 0 0 0 1 180330 180330\n'),
        'wrong_received_crc': replace_once(suffix, f'HOST_EDIT_CP_CHECK {start+23} 3 {ccrc:08x} {ccrc:08x}', f'HOST_EDIT_CP_CHECK {start+23} 3 {ccrc^1:08x} {ccrc:08x}'),
        'wrong_raw_result': replace_once(suffix, f'QCP 10 1 {ccrc:08x} 1 180330', f'QCP 10 0 {ccrc:08x} 1 180330'),
        'unknown_label': replace_once(suffix, f'HOST_EDIT_LABEL_BEFORE {start+2} {label:040x}', f'HOST_EDIT_LABEL_BEFORE {start+2} ' + 'x'*40),
        'no_atomic_checks': replace_once(suffix, '20 30 '+f'{ccrc:08x} {dcrc:08x}', '0 30 '+f'{ccrc:08x} {dcrc:08x}'),
        'wrong_elapsed_cycles': replace_once(suffix, '20 30 '+f'{ccrc:08x} {dcrc:08x}', '20 31 '+f'{ccrc:08x} {dcrc:08x}'),
        'pending_not_cleared': replace_once(suffix, f'{dcrc:08x} 0 1 180330 15 0\n', f'{dcrc:08x} 1 1 180330 15 0\n'),
        'lease_not_released': replace_once(suffix, f'{dcrc:08x} 0 1 180330 15 0\n', f'{dcrc:08x} 0 1 180330 15 1\n'),
        'raw_after_terminal_pass': '\n'.join(rows[:25] + rows[26:] + [rows[25]]) + '\n',
    }
    rejected_logs = []
    for name, bad in bad_suffixes.items():
        try:
            parser.check(prefix + bad, stdout, old_trace)
        except (AssertionError, ValueError):
            rejected_logs.append(name)
        else:
            raise AssertionError(name)
    for name, bad_trace, bad_stdout in [
        ('changed_original_prefix', prefix.replace('QCP 0 ', 'QCP 99 ', 1) + suffix, stdout),
        ('zero_actual_edit', prefix + suffix, stdout.replace('edit=1 ', 'edit=0 ')),
        ('wrong_cp_totals', prefix + suffix, stdout.replace('imports=60 ', 'imports=40 ')),
        ('duplicate_terminal_pass', prefix + suffix, stdout + stdout.splitlines()[0] + '\n'),
        ('fatal_after_pass', prefix + suffix, stdout + 'Fatal: synthetic negative control\n'),
    ]:
        try:
            parser.check(bad_trace, bad_stdout, old_trace)
        except (AssertionError, ValueError):
            rejected_logs.append(name)
        else:
            raise AssertionError(name)
    report = ROOT / 'results/checkpoint_host_edit_preflight_20261030.json'
    assert not report.exists()
    builder.prepare()
    preparation = ROOT / 'results/checkpoint_host_edit_testbench_preparation_20261030.json'
    bound = [Path(__file__).resolve(), builder_file, parser_file, VARIANT / 'declarations.svh',
             VARIANT / 'extension.svh', VARIANT / 'CONTRACT.md', VARIANT / 'prepared/tb_query_fault.sv',
             old_file, preparation]
    report.write_text(json.dumps(dict(status='static_insertion_and_artificial_parser_preflight_only',
        bound={str(p):sha(p) for p in bound}, reference_source_bindings=binding,
        insertion_negative_controls=rejected_insertions, parser_negative_controls=rejected_logs,
        synthetic_suffix=suffix, synthetic_stdout=stdout, synthetic_parsed_result=parsed,
        synthetic_values_are_not_measured_rtl_results=True, new_solver_started=False,
        scope='Python parsed and source-bound generation only. No SV compile, simulation or full-system auditor/runner exists for this extension yet.'),
        indent=2, sort_keys=True)+'\n')
    print('HOST_EDIT_PREFLIGHT', len(rejected_insertions), 'insertion rejections', len(rejected_logs), 'parser rejections; NO RTL RUN')


if __name__ == '__main__':
    main()
