"""Independent literal expected sequence, not inferred from a passing DUT log."""
import re
from check_vitis_kernel import require

# op,status,packet_words,node_occupied,node_history,owners,history,node_version,site_version
ROWS=[
 (0,0,3850849,0,0,65536,65536,3,11),
 (0,2,0,0,0,0,0,0,0), (1,0,3850849,0,0,0,0,0,0),
 (2,1,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,2,0,0,0,0,0,0,0), (0,2,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,1,0,0,0,0,0,0,0), (0,1,0,0,0,0,0,0,0),
 (0,0,3850849,0,0,65536,65536,3,11),
 (1,1,0,0,0,0,0,0,0), (1,1,0,0,0,0,0,0,0), (1,1,0,0,0,0,0,0,0),
 (1,0,3850849,0,0,0,0,0,0),
 (0,0,3850849,1,1,65536,65536,6,12),
 (0,0,3719777,1,1,32768,65536,6,12),
 (0,0,3719777,1,1,32768,65536,6,12),
]
TERMINAL='SNAPSHOT_RTL_GOLDEN_PASS transactions=30 full_depths=1'


def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']), 'Error in tree validation')
    rows=[tuple(map(int,r)) for r in re.findall(r'^SNAPSHOT_RTL_TX (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',text,re.M)]
    require(len(ROWS)==30 and rows==[(i,*r) for i,r in enumerate(ROWS)] and text.count('SNAPSHOT_RTL_TX')==30
            and text.splitlines().count(TERMINAL)==1,'Incomplete/different tree transaction sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(30)) and all(c>0 for _,c in rows)
            and len(re.findall(r'^transaction\b',text,re.M))==30,'Incomplete tree RTL transactions')
    return [c for _,c in rows]
