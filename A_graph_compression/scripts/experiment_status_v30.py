#!/usr/bin/env python3
"""Read-only original-chain and full O2 run status with bounded log inspection."""
import argparse
import json
from pathlib import Path
import re
import time
from experiment_status_v29 import collect as original_collect
from experiment_status_v6 import process
from run_native_o2_full_rtl_v1 import OUT, REPORT


def o2_status():
    row = dict(trial=str(OUT), identity_verified=False, functional_acceptance_inferred=False)
    try:
        state = json.loads((OUT/'state.json').read_text())
        row.update(status=state['status'], stage=state['stage'])
        actual_path = OUT/'rtl.actual_limits.json'
        if actual_path.exists():
            recorded = json.loads(actual_path.read_text())
            actual = process(recorded['pid'])
            row['identity_verified'] = bool(actual and actual['state'] != 'Z' and
                actual['start_ticks'] == str(recorded['start_ticks']) and actual['command'] == recorded['command'])
            row['pid'] = recorded['pid']
        path = OUT/'rtl.log'
        if path.exists():
            with path.open('rb') as stream:
                stream.seek(max(0, path.stat().st_size-65536))
                text = stream.read().decode(errors='replace')
            row['log_age_seconds'] = round(time.time()-path.stat().st_mtime, 3)
            samples = []
            for chunk in re.split(r'(?m)^A_O2_PROGRESS ',text)[1:]:
                header = re.match(r'step=(\d+) wall_ms=(\d+)',chunk)
                if not header:
                    continue
                values = dict(re.findall(r'(?m)^A_O2_VALUE (\d+) (\S+)$',chunk))
                if set(values) != {str(i) for i in range(13)}:
                    continue
                sample = dict(step=int(header[1]), wall_ms=int(header[2]), values=values)
                for key, index in [('completed',0),('clock_count',2),('init_index',4),('trace_scan_1_index',9),('trace_scan_2_index',10)]:
                    value = values[str(index)]
                    sample[key] = int(value,16) if re.fullmatch(r'[0-9a-fA-F]+',value) else None
                samples.append(sample)
            if samples:
                row['last_sample'] = samples[-1]
            if len(samples) >= 2:
                a,b = samples[-2:]
                if a['clock_count'] is not None and b['clock_count'] is not None and b['wall_ms'] > a['wall_ms'] and b['clock_count'] >= a['clock_count']:
                    row['last_interval_cycles_per_wall_second'] = (b['clock_count']-a['clock_count'])*1000/(b['wall_ms']-a['wall_ms'])
        row['rtl_receipt_exists'] = (OUT/'rtl.receipt.json').exists()
        row['audit_report_exists'] = REPORT.exists()
        row['terminal_receipt_exists'] = (OUT/'terminal.json').exists()
        row['note'] = 'Samples are recorded DUT/TB values. Report existence or process activity alone is not acceptance; the independent audit and its exit receipt are required.'
    except (OSError, ValueError, KeyError) as exc:
        row['observation_error'] = str(exc)
    return row


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    if args.json:
        result = original_collect()
        result['native_O2_full_run'] = o2_status()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(json.dumps(o2_status(), ensure_ascii=False, indent=2))
