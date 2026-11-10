"""Index the actual closed pin walks reported by Vivado check_timing.

Overlapping reported walks are grouped for navigation only. This does not claim
an exhaustive SCC decomposition, sensitizability proof or RTL root cause.
"""
from pathlib import Path
from collections import Counter
import json,re,sys
from run_checkpoint_authority import sha

p=Path(sys.argv[1]).resolve()
m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and m['exit_code']==0
t=(p/'check_timing.rpt').read_text()
matches=list(re.finditer(r'^9\. checking loops \((\d+)\)\s*$',t,re.M))
assert len(matches)==2,'expected TOC and actual loops section'
start=matches[-1];expected=int(start[1])
section=t[start.end():].split('10. checking partial_input_delay',1)[0]
walks=[]
for block in re.split(r'\n\s*\n',section):
    lines=[l.strip()for l in block.splitlines()if l.strip()]
    if not lines or '/' not in lines[0]:continue
    assert len(lines)>2 and lines[0]==lines[-1],lines
    assert all(re.search(r'/(?:I\d*|O\d*)$',l)for l in lines),lines
    cells=sorted({l.rsplit('/',1)[0]for l in lines})
    walks.append(dict(index=len(walks)+1,pins=lines,cells=cells,
        hierarchy_counts=dict(Counter(c.rsplit('/',1)[0]for c in cells))))
# Vivado 2022.2 may print fewer explicit walks than its section count (the
# observed on-root reports 20 but lists nine). Preserve this gap; never invent
# missing walks or call these an exhaustive netlist analysis.
assert 0<=len(walks)<=expected,(len(walks),expected)
groups=[]
for walk in walks:
    cells=set(walk['cells']);members={walk['index']}
    # Each merge can connect several pre-existing disjoint groups.
    keep=[]
    for g in groups:
        if cells & g['cells']:
            cells|=g['cells'];members|=g['members']
        else:keep.append(g)
    groups=keep+[dict(cells=cells,members=members)]
# Revisit until transitive overlap closure is stable.
changed=True
while changed:
    changed=False
    for i in range(len(groups)):
        for j in range(i+1,len(groups)):
            if groups[i]['cells'] & groups[j]['cells']:
                groups[i]['cells']|=groups[j]['cells'];groups[i]['members']|=groups[j]['members']
                groups.pop(j);changed=True;break
        if changed:break
indexed=[dict(walk_indices=sorted(g['members']),unique_cells=len(g['cells']),
              hierarchy_counts=dict(sorted(Counter(c.rsplit('/',1)[0]for c in g['cells']).items())))
         for g in sorted(groups,key=lambda g:min(g['members']))]
result=dict(status='observed',design_acceptance='rejected_combinational_loops'if expected else'unresolved',
            check_timing_sha256=sha(p/'check_timing.rpt'),manifest_sha256=sha(p/'manifest.json'),
            analyzer_sha256=sha(Path(__file__)),reported_loops=expected,
            explicit_walks=len(walks),all_reported_loops_have_walks=len(walks)==expected,walks=walks,
            overlapping_reported_walk_groups=indexed,
            scope='Literal closed pin walks from check_timing; grouping by shared cells is diagnostic navigation, not exhaustive SCC analysis or a functional counterexample.')
(p/'loop_walks.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('LOOP_WALKS_INDEXED',p.name,expected,indexed)
