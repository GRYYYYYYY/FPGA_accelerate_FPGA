"""Locate synthesis deltas; hierarchy counts are not a causal proof."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):
 rows={}
 for line in p.read_text().splitlines():
  f=[s.strip() for s in line.split('|')]
  if len(f)!=13 or not f[3].isdigit():continue
  rows[f[1]]={'LUT':int(f[3]),'FF':int(f[7]),'RAMB36':int(f[8])}
 return rows
if __name__=='__main__':
 out=ROOT/'results/epoch6_hierarchy_comparison_20261023';out.mkdir()
 paths=[ROOT/'results'/n/'utilization_hierarchical.rpt' for n in ['rtl_static_endpoint_synthesis_20261023','rtl_epoch6_endpoint_synthesis_20261023']]
 a,b=map(read,paths);assert a.keys()==b.keys()
 delta={n:{k:b[n][k]-a[n][k] for k in a[n]} for n in a}
 top='memory_scratch_endpoint_small_staticcodec'
 assert delta[top]['LUT']==568 and delta['memory']['LUT']+delta['pages']['LUT']==568
 result={'status':'verified_report_comparison','rows':{n:{'epoch8':a[n],'epoch6':b[n],'delta':delta[n]} for n in a},'inputs':{str(p):sha(p) for p in paths},'source_sha256':sha(Path(__file__)),'interpretation':'Directory LUT -126, codec +29, memory subtree -97; pages subtree +665 including work FIFO +566. Global synthesis result, not proof of direct epoch comparator cost. Nested rows overlap and must not be added indiscriminately.'}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(delta)
