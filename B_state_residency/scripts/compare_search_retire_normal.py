"""Byte-compare normal traces, physical AXI logs and whole images to baseline."""
from pathlib import Path
import json,sys
from run_query_fault import sha,ROOT
p=Path(sys.argv[1]).resolve();base=ROOT/'results/query_lifecycle_join_v2'
assert json.loads((p/'source_bound_audit.json').read_text())['status']=='passed'
files=['natural_trace.txt']+[n+'_axi.txt' for n in ['graph','design','label','owner','cost','qstate','table']]+['design.bin','owners.bin','cost.bin','labels.bin']
report={}
for mode in ['full','pressure']:
 report[mode]={}
 for n in files:
  a=sha(p/mode/n);b=sha(base/mode/n);assert a==b,(mode,n)
  report[mode][n]=a
out={'status':'passed','reference':str(base),'result':str(p),'audit_sha256':sha(p/'source_bound_audit.json'),'script_sha256':sha(Path(__file__)),'byte_identical':report,'scope':'24 files: complete cycle trace, seven physical AXI streams and four complete images in each capacity. No board speedup inference.'}
(ROOT/'results/search_retire_normal_comparison_20261025.json').write_text(json.dumps(out,indent=2)+'\n');print('NORMAL_BYTE_IDENTICAL',len(files)*2)
