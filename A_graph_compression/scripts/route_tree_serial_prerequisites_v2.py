"""Full50 admission after the naming-corrected native and both bus64 RTL audits."""
import json
from pathlib import Path

from check_vitis_kernel import digest, require
from binary_nonzero_full44_prerequisites_v2 import full_outputs

ROOT = Path(__file__).resolve().parents[1]
NATIVE = 'collision_safe_recovered_native_rtl_audit_20261030_v2.json'
CSR = 'collision_safe_bus64_full_rtl_mode_0_audit_20261030_v1.json'
COMPACT = 'collision_safe_bus64_full_rtl_mode_1_audit_20261030_v1.json'


def validate_predecessors(root=ROOT):
    files = {str(Path(__file__).resolve()): digest(__file__)}
    for mode, name in ((None, NATIVE), (0, CSR), (1, COMPACT)):
        path = root / 'results' / name
        require(path.is_file(), 'Naming-corrected full RTL prerequisite missing: ' + name)
        report = json.loads(path.read_text())
        expected = ('recovered_collision_safe_native_full4tx_full44_original_C_independently_verified'
                    if mode is None else
                    'collision_safe_bus64_full4tx_full44_original_C_oracle_independently_verified')
        require(report.get('status') == expected and report.get('rtl_verified') is True,
                'Unaccepted full RTL predecessor: ' + name)
        require((report.get('transactions'), report.get('pointers'), report.get('models')) ==
                (4, 44, 30), 'Partial predecessor interface')
        full_outputs(report)
        if mode is not None:
            require(report.get('graph_mode') == mode and report.get('pointer_address_offset') == 4096,
                    'Different bus64 mode/address environment')
            for earlier in ([NATIVE] if mode == 0 else [NATIVE, CSR]):
                p = str(root / 'results' / earlier)
                require(report.get('files', {}).get(p) == files[p],
                        'Predecessor accepted a different earlier audit')
        bindings = report.get('files')
        require(isinstance(bindings, dict) and bindings, 'Missing predecessor evidence')
        for p, checksum in bindings.items():
            require(p not in files or files[p] == checksum, 'Conflicting predecessor evidence')
            if p not in files:
                require(digest(p) == checksum, 'Changed predecessor evidence: ' + p)
            files[p] = checksum
        files[str(path)] = digest(path)
    return files
