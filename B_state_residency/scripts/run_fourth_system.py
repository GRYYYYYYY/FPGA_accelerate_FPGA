"""Run frozen G3-warm production hierarchy with four slots, G4 and natural q4."""
from pathlib import Path
import copy
import json
import runpy
import shutil
import struct
import subprocess
import sys
import time
from run_checkpoint_authority import ROOT, sha

out = Path(sys.argv[1]).resolve()
case = sys.argv[2] if len(sys.argv) > 2 else 'full'
assert case in ['full','pressure']
base = out.parent/'third_warm_full_v2'
bm = json.loads((base/'manifest.json').read_text())
ba = json.loads((base/'source_bound_audit.json').read_text())
assert ba['status']=='passed' and ba['manifest_sha256']==sha(base/'manifest.json')
variant = ROOT/'hardware/variants/four_path_v1'
assert runpy.run_path(str(variant/'build_system.py'))['make']()==(variant/'tb_fourth.sv').read_text()
fourth = out.parent/'followup_iter2_fourth_plain_v1'
cost = out.parent/'followup_iter2_fourth_cost_v1'
oracle = out.parent/'followup_iter2_fourth_oracle_v1'
for p in [fourth,cost,oracle]: assert json.loads((p/'source_bound_audit.json').read_text())['status']=='passed'
for n in ['cost.bin','connections.bin']: assert sha(cost/n)==sha(out.parent/'followup_iter2_third_cost_v1'/n)
out.mkdir(); src=out/'sources';src.mkdir();d=out/case;d.mkdir()
m = copy.deepcopy(bm)
m.update(status='running', cases={case:dict(status='running',commands=[])}, parent_run=str(base), parent_audit_sha256=sha(base/'source_bound_audit.json'),
         scope='Four-slot full G3-warm prefix, native cumulative G4 copy to inactive A bank/CP20 joint publication, then natural q180330 historical metadata/ripup/CPU-checked query. Fixed price/history, trusted initial G1 clones/baseline; no G4 failure recovery or board claim.')
for n,e in bm['sources'].items():
    assert sha(base/'sources'/n)==e['sha256'],n
    target=src/n;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/n,target)
for n,p in {'runner.py':Path(__file__),'tb_query_fault.sv':variant/'tb_fourth.sv','fourth_build.py':variant/'build_system.py','fourth_tasks.sv':variant/'fourth_tasks.sv'}.items():
    shutil.copyfile(p,src/n);m['sources'][n]=dict(path=str(p),sha256=sha(src/n))
for key in ['scoreboards','next_scoreboards','third_scoreboards']:
    for n,h in bm[key].items():
        assert sha(base/n)==h;shutil.copyfile(base/n,out/n)
rows=[t.split()for t in(fourth/'events.txt').read_text().splitlines()]
(out/'polls4.txt').write_text(''.join(' '.join(t[1:4])+'\n'for t in rows if t[0]=='P'))
(out/'candidates4.txt').write_text(''.join(' '.join([t[1],t[2],t[3],str(int(i+1<len(rows)and rows[i+1][0]=='W')),t[8]])+'\n'for i,t in enumerate(rows)if t[0]=='C'))
ids=[int(line.split()[0])for line in(out/'imports.txt').read_text().splitlines()]
with(fourth/'search_final_nodes.u32').open('rb')as f,(out/'finals4.txt').open('w')as g:
    for node in ids:
        f.seek(node*44);u=struct.unpack('<11I',f.read(44));v=[u[0],u[1],u[3],u[4],u[5]]
        if node==6954:v[4]=0
        g.write(str(node)+' '+' '.join(f'{x:08x}'for x in v)+'\n')
m['fourth_inputs']={str(p):sha(p/'source_bound_audit.json')for p in [fourth,cost,oracle]}
m['fourth_scoreboards']={n:sha(out/n)for n in ['polls4.txt','candidates4.txt','finals4.txt']}
reg=json.loads(Path(m['binding']).read_text())['regions']
assert sha(Path(m['binding']))==m['binding_sha256']
for n,k in [('design.bin','design'),('cost.bin','cost_history_prices_nets')]:shutil.copyfile(Path(reg[k]['path']),d/n)
with(d/'owners.bin').open('wb')as f:
    for k in ['owners','owner_pool','owner_allocator']:f.write(Path(reg[k]['path']).read_bytes())
for n in ['g3.bin','snapshot.bin','pool.bin']:shutil.copyfile(d/'owners.bin',d/n)
shutil.copyfile(Path(reg['owner_allocator']['path']),d/'allocator.bin')
with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
for f in src.rglob('*.dat'):shutil.copyfile(f,d/f.name)
def save(): (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
save()
try:
    for old in bm['cases']['full']['commands']:
        stage=old['stage'];argv=[a.replace(str(base/'full'),str(d)).replace(str(base),str(out))for a in old['argv']]
        if stage=='compile' and case=='pressure':argv[1:1]=['--define','PRESSURE']
        if stage=='simulate':
            (d/'run.tcl').write_text('run 100ms\nquit\n')
            for k,v in dict(cost4=cost/'cost_vectors.txt',polls4=out/'polls4.txt',candidates4=out/'candidates4.txt',finals4=out/'finals4.txt',g4imports=d/'runtime_g4_labels.txt').items():
                argv+=['--testplusarg',k+'='+str(v)]
        start=time.monotonic()
        with(d/(stage+'.stdout.log')).open('w')as log:
            r=subprocess.run(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
        m['cases'][case]['commands'].append(dict(stage=stage,argv=argv,exit_code=r.returncode,elapsed_s=time.monotonic()-start));save()
        assert r.returncode==0,stage
        print(stage,'completed',flush=True)
    log=(d/'simulate.log').read_text()
    assert 'Fatal:'not in log and '$finish called'in log
    for marker in ['THIRD_WARM_PASS','G4_PUBLISH_PASS','FOURTH_PASS polls=83 expands=82 candidates=402 costs=231']:assert marker in log,marker
    m['status']=m['cases'][case]['status']='observed'
except Exception as e:
    m.update(status='failed',error=repr(e));raise
finally:save()
print('FOURTH_SYSTEM_OBSERVED',case)
