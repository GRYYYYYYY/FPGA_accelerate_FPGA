"""Literal contract independent of the RTL TB's runtime oracle."""
import re
from check_vitis_kernel import require

MAX=18446744073709551615
# Each row: op, status, live owners, history keys, version, result groups, snapshot owners.
ROWS=[
    (0,0,0,0,1,0,0),
    (1,0,4,0,2,0,0),
    (1,0,8,0,3,0,0),
    (1,0,11,0,4,0,0),
    (2,0,11,0,4,4,0),
    (4,0,11,0,4,0,7),
    (3,0,11,4,5,4,0),
    (4,0,11,4,5,0,7),
    (1,0,11,4,6,0,0),
    (1,0,7,4,7,0,0),
    (2,0,7,4,7,1,0),
    (3,0,7,4,8,1,0),
    (1,1,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (1,2,7,4,8,0,0),
    (1,1,7,4,8,0,0),
    (4,1,7,4,8,0,0),
    (1,0,10,4,9,0,0),
    (3,3,10,4,9,0,0),
    (3,0,10,4,10,3,0),
    (4,0,10,4,10,0,7),
    (1,3,10,4,MAX,0,0),
    (3,3,10,4,MAX,0,0),
    (4,0,10,4,MAX,0,6),
    (1,0,7,4,11,0,0),
    (0,0,0,0,1,0,0),
    (1,0,65536,0,2,0,0),
    (1,2,65536,0,2,0,0),
    (4,0,65536,0,2,0,65536),
    (1,0,32768,0,3,0,0),
    (1,0,65536,0,4,0,0),
    (3,0,65536,32768,5,32768,0),
    (1,0,32768,32768,6,0,0),
    (1,0,32768,32768,7,0,0),
    (1,0,65536,32768,8,0,0),
    (3,0,65536,65536,9,32768,0),
    (4,0,65536,65536,9,0,65536),
    (1,0,32768,65536,10,0,0),
    (1,0,1,65536,11,0,0),
    (1,0,2,65536,12,0,0),
    (3,2,2,65536,12,0,0),
    (1,0,1,65536,13,0,0),
    (2,0,1,65536,13,0,0),
    (3,0,1,65536,14,0,0),
    (4,0,1,65536,14,0,0),
    (0,0,0,0,1,0,0),
    (4,0,0,0,1,0,0),
    (99,1,0,0,1,0,0),
]
TERMINAL='SITE_OCCUPANCY_RTL_ALL_PASS transactions=52 production_owners=65536 production_history=65536 production_requests=65536 full_depth=1'


def golden(text):
    require(not any(error in text for error in ('ERROR:', 'FATAL_ERROR', 'runtime error:', 'Assertion', 'AddressSanitizer')),
            'Error in site occupancy verification log')
    pattern=(r'^SITE_OCCUPANCY_RTL_CASE_PASS transaction=(\d+) op=(\d+) status=(\d+) owners=(\d+) '
             r'history=(\d+) version=(\d+) groups=(\d+) snapshot=(\d+) full_depth=1 all_state=1 guards=1$')
    actual=[tuple(map(int,r)) for r in re.findall(pattern,text,re.M)]
    require(actual==[(i,*r) for i,r in enumerate(ROWS)] and text.count('SITE_OCCUPANCY_RTL_CASE_PASS')==52
            and text.splitlines().count(TERMINAL)==1,
            'Incomplete/different site occupancy transaction sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(52)) and all(c>0 for _,c in rows)
            and len(re.findall(r'^transaction\b',text,re.M))==52, 'Incomplete site occupancy RTL transactions')
    return [c for _,c in rows]
