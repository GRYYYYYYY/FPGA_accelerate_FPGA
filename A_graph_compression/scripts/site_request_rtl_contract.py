"""Literal transaction results, separate from the testbench oracle."""
import re
from check_vitis_kernel import require
COUNTS=[0,3,6,9,12,15,18,21,24,18,21,24,27,30,33,36,39,25,19,22,56,0,1,1,
        0,0,0,0,0,0,0,0,0,56]
STATUSES=[0]*24+[1]*9+[0]
TERMINAL='SITE_REQUEST_RTL_GOLDEN_PASS transactions=34 max_records=56 full_depth=196608'


def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']),'Verification error')
    rows=[tuple(map(int,r)) for r in re.findall(r'^SITE_REQUEST_RTL_TX (\d+) (\d+) (\d+)$',text,re.M)]
    require(rows==list(zip(range(34),STATUSES,COUNTS)) and text.count('SITE_REQUEST_RTL_TX')==34
            and text.splitlines().count(TERMINAL)==1,'Incomplete/different request encoder sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(34)) and all(c>0 for _,c in rows)
            and len(re.findall(r'^transaction\b',text,re.M))==34,'Incomplete request RTL performance')
    return [c for _,c in rows]
