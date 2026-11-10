"""Literal full-capacity boundary stimulus contract, shared only by auditors."""
import re

def require(ok,message):
    if not ok:raise ValueError(message)

STATUSES=[0,5,5,5,0,1,1,0]

def golden(text,mode,copies=1):
    require('ERROR:' not in text and 'FATAL_ERROR' not in text and 'runtime error:' not in text,'Error in boundary log')
    rows=[tuple(map(int,r)) for r in re.findall(r'^STATE_BOUNDARY_PASS mode=(\d+) transaction=(\d+) status=(\d+) full_capacity=32,16,8 literal_output=1 guards=1$',text,re.M)]
    require(rows==[(mode,i,s) for i,s in enumerate(STATUSES)]*copies,'Missing/reordered boundary cases')
    seen=[tuple(map(int,r)) for r in re.findall(r'^STATE_BOUNDARY_OBSERVED mode=(\d+) transaction=(\d+) status=(\d+) cost=(\d+) expanded=(\d+) path=(\d+)$',text,re.M)]
    require(seen==[(mode,i,s,2 if s==0 else 0,2,2 if s==0 else 0) for i,s in enumerate(STATUSES)]*copies,'Different literal result')
    require(text.count('STATE_BOUNDARY_ALL_PASS transactions=8 production_top=1 full_workspace_limits=1')==copies,'Missing terminal marker')

def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(8)) and all(c>0 for _,c in rows),'Incomplete eight RTL transactions')
    return [c for _,c in rows]
