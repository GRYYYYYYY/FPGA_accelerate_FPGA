"""Literal operation/result sequence, independent of the testbench map oracle."""
import re
from check_vitis_kernel import require
ROWS=[
 (0,0,0,0,1,0),(1,0,2097152,1,2,0),(2,0,2097152,1,2,2097152),
 (3,2,0,0,0,0),(1,2,0,0,0,0),(2,0,2097152,1,2,0),
 (1,0,0,0,3,0),(3,0,2,1,4,0),(3,0,4,1,5,0),(2,0,4,1,5,4),
 (1,0,5,2,6,0),(2,0,5,2,6,1),(2,0,5,2,6,4),
 (3,1,0,0,0,0),(3,1,0,0,0,0),(3,1,0,0,0,0),(3,3,0,0,0,0),
 (2,0,5,2,18446744073709551615,4),(0,0,0,0,1,0),
 (0,1,0,0,0,0),(0,2,0,0,0,0),(2,1,0,0,0,0),(2,1,0,0,0,0),
 (3,1,0,0,0,0),(4,1,0,0,0,0),(2,1,0,0,0,0),(0,0,0,0,1,0),
 (3,2,0,0,0,0),(1,0,65537,65536,2,0),(2,0,65537,65536,2,2),
 (1,0,65535,65535,3,0),(3,0,65537,65536,4,0),(2,0,65537,65536,4,2),
 (0,0,0,0,1,0),(3,0,4,1,2,0),(2,0,4,1,2,4),(1,0,0,0,3,0),
]
TERMINAL='EDGE_RTL_GOLDEN_PASS transactions=37 edges=2097152 seeded_nets=65536 full_depths=1'
def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']),'Edge verification error')
    rows=[tuple(map(int,r)) for r in re.findall(r'^EDGE_RTL_TX (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',text,re.M)]
    require(rows==[(i,*r) for i,r in enumerate(ROWS)] and len(ROWS)==37 and text.count('EDGE_RTL_TX')==37 and text.splitlines().count(TERMINAL)==1,'Different edge transaction sequence')
def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(37)) and all(c>0 for _,c in rows) and len(re.findall(r'^transaction\b',text,re.M))==37,'Incomplete edge RTL performance')
    return [c for _,c in rows]
