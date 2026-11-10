"""Literal37-operation contract separate from the RTL testbench's map oracle."""
import re
from check_vitis_kernel import require
# op,status,total_pairs,total_nets,version,returned_count
ROWS=[
 (0,0,0,0,1,0),(1,0,1048576,1,2,0),(1,0,2097152,2,3,0),
 (2,0,2097152,2,3,1048576),(2,0,2097152,2,3,0),(1,2,0,0,0,0),
 (2,0,2097152,2,3,1048576),(1,0,1048576,1,4,0),(1,0,2097152,2,5,0),
 (1,2,0,0,0,0),(1,1,0,0,0,0),(1,1,0,0,0,0),(1,3,0,0,0,0),
 (1,1,0,0,0,0),(1,1,0,0,0,0),(0,2,0,0,0,0),(0,1,0,0,0,0),
 (0,0,0,0,1,0),(1,0,2,1,2,0),(2,0,2,1,2,2),(1,0,3,2,3,0),
 (2,0,3,2,3,0),(1,0,2,2,4,0),(2,0,2,2,4,1),(1,0,1,1,5,0),
 (2,0,1,1,5,0),(0,0,0,0,1,0),(1,2,0,0,0,0),
 (2,0,65536,65536,1,1),(1,0,65536,65536,2,0),(2,0,65536,65536,2,1),
 (1,0,65535,65535,3,0),(1,0,65536,65536,4,0),(2,0,65536,65536,4,1),
 (3,1,0,0,0,0),(0,0,0,0,1,0),(2,0,0,0,1,0),
]
TERMINAL='RETAINED_RTL_GOLDEN_PASS transactions=37 pairs=2097152 seeded_nets=65536 full_depths=1'


def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']),'Retention verification error')
    rows=[tuple(map(int,r)) for r in re.findall(r'^RETAINED_RTL_TX (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',text,re.M)]
    require(rows==[(i,*r) for i,r in enumerate(ROWS)] and len(ROWS)==37 and text.count('RETAINED_RTL_TX')==37 and text.splitlines().count(TERMINAL)==1,'Different retention transaction sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(37)) and all(c>0 for _,c in rows) and len(re.findall(r'^transaction\b',text,re.M))==37,'Incomplete retention RTL performance')
    return [c for _,c in rows]
