"""Literal round decisions, independent of TB reference calculations."""
import re
from check_vitis_kernel import require
# status,node_groups,incomplete,action,next_iteration,next_present,advance,current
ROWS=[
 (0,0,0,0,0,0,0,1),(0,0,1,1,0,0,0,1),(0,1,1,2,1,2,1,1),
 (0,1,1,1,0,0,1,8),(0,1048576,1,2,1,2,1,1),(0,0,0,2,1,2,1,1),
 (0,0,0,0,0,0,0,1),(0,0,0,2,20,1048576,1,524288),
 (0,0,0,2,21,1048576,1,1048576),(0,0,0,2,22,1048576,1,1048576),
 (0,0,0,1,0,0,1,1048576),(0,0,0,1,0,0,1,1),
 (0,0,0,0,0,0,0,1),(0,0,1,1,0,0,0,1),(0,0,0,0,0,0,0,1),
 (1,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,1),
 (2,0,0,0,0,0,0,0),(2,0,0,0,0,0,0,0),(2,0,0,0,0,0,0,0),
 (1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),
 (1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),
 (1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),(1,0,0,0,0,0,0,0),
 (0,1,1,2,1,2,1,1),(0,1,1,1,0,0,1,2),(0,0,1,1,0,0,0,2),
 (0,0,0,0,0,0,0,2),(0,0,0,0,0,0,0,2),(0,0,0,0,0,0,0,2),
 (1,0,0,0,0,0,0,0),(0,0,0,0,0,0,0,1),
]
TERMINAL='ROUND_RTL_GOLDEN_PASS transactions=37 nodes=1048576 nets=65536 full_depths=1 readonly=1'


def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']),'Round-control verification error')
    rows=[tuple(map(int,r)) for r in re.findall(r'^ROUND_RTL_TX (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',text,re.M)]
    require(len(ROWS)==37 and rows==[(i,*r) for i,r in enumerate(ROWS)] and text.count('ROUND_RTL_TX')==37 and text.splitlines().count(TERMINAL)==1,'Different round decision sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(37)) and all(c>0 for _,c in rows) and len(re.findall(r'^transaction\b',text,re.M))==37,'Incomplete round-control RTL performance')
    return [c for _,c in rows]
