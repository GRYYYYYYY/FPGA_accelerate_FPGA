"""Independent literal transaction contract for full-depth occupancy RTL checks."""
import re
from check_vitis_kernel import require

STATUSES = [0,0,0,0,0,0,0,0,4,0,0,0,3,1,2,1,0,0,0,0,0,4,0,0,0,0,1,2]
PAIRS = [0,2,3,0,3,6,6,6,6,6,6,4,4,4,4,4,4,4,1,2,2,2,2,2,0,0,0,0]
VERSIONS = [1,2,3,1,2,3,4,4,4,5,5,6,6,6,6,6,6,7,8,9,9,18446744073709551615,10,10,1,1,1,1]
TERMINAL = 'NODE_OCCUPANCY_RTL_ALL_PASS transactions=28 production_nodes=1048576 production_slots=2097152 full_depth=1'


def golden(text):
    require(not any(error in text for error in ('ERROR:', 'FATAL_ERROR', 'runtime error:', 'Assertion', 'AddressSanitizer')),
            'Error in occupancy verification log')
    pattern = (r'^NODE_OCCUPANCY_RTL_CASE_PASS transaction=(\d+) status=(\d+) nodes=(\d+) '
               r'pairs=(\d+) version=(\d+) full_depth=1 all_state=1 guards=1$')
    rows = [tuple(map(int, values)) for values in re.findall(pattern, text, re.M)]
    expected = [(i, STATUSES[i], 1048576 if i<3 else 64, PAIRS[i], VERSIONS[i]) for i in range(28)]
    require(rows == expected and text.count(TERMINAL) == 1, 'Incomplete/different occupancy transaction sequence')


def transactions(text):
    rows = [tuple(map(int, values)) for values in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$', text, re.M)]
    require([i for i, _ in rows] == list(range(28)) and all(c > 0 for _, c in rows), 'Incomplete occupancy RTL transactions')
    return [c for _, c in rows]
