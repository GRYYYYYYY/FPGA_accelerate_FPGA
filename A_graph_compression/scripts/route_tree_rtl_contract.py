"""Independent literal expected sequence, not inferred from a passing DUT log."""
import re
from check_vitis_kernel import require

# op,status,unique_nodes,version,applied,roots_count,complete
ROWS=[
 (0,0,1,1,0,0,0),
 (1,0,524289,2,1,0,0),
 (1,0,1048576,3,1,0,0),
 (2,0,1048576,3,0,1048576,0),
 (3,0,1048576,3,0,0,1),
 (1,2,0,0,0,0,0), (3,2,0,0,0,0,0), (3,1,0,0,0,0,0),
 (0,2,0,0,0,0,0), (0,1,0,0,0,0,0), (0,1,0,0,0,0,0),
 (0,0,1,1,0,0,0), (2,0,1,1,0,1,0), (3,0,1,1,0,0,1), (3,0,1,1,0,0,0),
 (1,0,2,2,1,0,0), (3,0,2,2,0,0,1), (2,0,2,2,0,2,0),
 (1,0,2,2,0,0,0), (1,0,2,2,0,0,0), (1,0,2,2,0,0,0),
 (1,0,2,2,0,0,0), (1,0,2,2,0,0,0), (1,0,2,2,0,0,0),
 (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0),
 (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0),
 (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0),
 (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0),
 (1,0,2,3,1,0,0), (1,3,0,0,0,0,0), (1,1,0,0,0,0,0), (1,1,0,0,0,0,0),
 (4,1,0,0,0,0,0), (2,1,0,0,0,0,0), (1,0,3,4,1,0,0), (2,0,3,4,0,3,0),
 (0,0,1,1,0,0,0), (2,0,1,1,0,1,0),
]
TERMINAL='ROUTE_TREE_RTL_GOLDEN_PASS transactions=50 nodes=1048576 path=524288 full_depths=1'


def golden(text):
    require(not any(x in text for x in ['ERROR:','FATAL_ERROR','runtime error:','Assertion','AddressSanitizer']), 'Error in tree validation')
    rows=[tuple(map(int,r)) for r in re.findall(r'^TREE_RTL_TX (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+) (\d+)$',text,re.M)]
    require(len(ROWS)==50 and rows==[(i,*r) for i,r in enumerate(ROWS)] and text.count('TREE_RTL_TX')==50
            and text.splitlines().count(TERMINAL)==1,'Incomplete/different tree transaction sequence')


def transactions(text):
    rows=[tuple(map(int,r)) for r in re.findall(r'^transaction\s+(\d+):\s+(\d+)\s+(?:\d+|x)\s*$',text,re.M)]
    require([i for i,_ in rows]==list(range(50)) and all(c>0 for _,c in rows)
            and len(re.findall(r'^transaction\b',text,re.M))==50,'Incomplete tree RTL transactions')
    return [c for _,c in rows]
