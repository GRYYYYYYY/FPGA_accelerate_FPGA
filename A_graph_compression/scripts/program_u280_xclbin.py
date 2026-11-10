#!/usr/bin/env python3
"""Prepare or execute volatile U280 user-image loading with XRT 2022.2.

Default: validate the named artifact and print a command, without opening a card.
Use a hardware xclbin from the completed RTL/link audit, with its recorded SHA256.
This utility neither builds the image nor proves kernel functional correctness.
"""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

XRT_BIN = Path('/opt/xilinx/xrt/bin')


def checksum(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(4*1024*1024), b''):
            h.update(block)
    return h.hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--xclbin', type=Path, required=True)
    parser.add_argument('--expected-sha256', required=True)
    parser.add_argument('--device', required=True, help='Explicit PCI BDF, for example 0000:65:00.1')
    parser.add_argument('--execute', action='store_true', help='Actually load the image; otherwise only print the plan')
    parser.add_argument('--output', type=Path, help='New directory for the programming log/receipt, required with --execute')
    args = parser.parse_args()
    if not re.fullmatch(r'[0-9a-fA-F]{4}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}\.[0-7]', args.device):
        parser.error('An explicit PCI BDF is required')
    if not re.fullmatch(r'[0-9a-fA-F]{64}', args.expected_sha256):
        parser.error('Expected SHA256 must contain 64 hexadecimal digits')
    path = args.xclbin.resolve()
    if not path.is_file():
        parser.error('Hardware xclbin file does not exist')
    before = checksum(path)
    if before != args.expected_sha256.lower():
        parser.error('xclbin SHA256 differs from the expected build artifact')
    if args.execute and (args.output is None or args.output.exists()):
        parser.error('--execute requires a new --output directory')
    inspection = subprocess.run([str(XRT_BIN/'xclbinutil'), '--info', '--input', str(path)],
                                capture_output=True, text=True, timeout=120)
    if inspection.returncode != 0:
        parser.error('xclbinutil rejected the artifact: '+inspection.stderr[-1000:])
    command = [str(XRT_BIN/'xbutil'), 'program', '--device', args.device.lower(), '--user', str(path)]
    plan = dict(action='volatile_user_image_load',command=command,xclbin_sha256=before,
                execute=args.execute,kernel_functional_validation=False,
                prerequisite='Use the hardware image already accepted by the RTL/link audit; this loader does not replace that audit.')
    if not args.execute:
        print(json.dumps(plan, indent=2, ensure_ascii=False))
        return
    out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    (out/'plan.json').write_text(json.dumps(plan, indent=2)+'\n')
    (out/'xclbin_info.log').write_text(inspection.stdout+inspection.stderr)
    if checksum(path) != before:
        raise RuntimeError('xclbin changed after inspection')
    started = time.monotonic()
    with (out/'program.log').open('x') as log:
        result = subprocess.run(command, stdout=log, stderr=subprocess.STDOUT)
    unchanged = checksum(path) == before
    receipt = dict(status='image_loaded' if result.returncode == 0 and unchanged else 'failed',
                   exit_code=result.returncode,elapsed_seconds=time.monotonic()-started,
                   xclbin_unchanged=unchanged,log_sha256=checksum(out/'program.log'),
                   kernel_functional_validation=False)
    (out/'receipt.json').write_text(json.dumps(receipt, indent=2)+'\n')
    print(json.dumps(receipt))
    if receipt['status'] != 'image_loaded':
        raise SystemExit(1)


if __name__ == '__main__':
    main()
