"""Directed codec and retained-state mutation checks for the small-page model."""
import json
from pathlib import Path
from replay_small_page_checkpoint import Planner,encode_page,decode_page,sha

def main():
    checks=[]
    values={0:0,7:(1<<136)-1,3:0x7fc00000}
    raw=encode_page(values);assert decode_page(raw)==values
    assert len(raw)==192 and raw[0]==137
    checks.append('valid zero, boundary offsets, all 136 bits, NaN bit pattern')
    for position in [18,160,161,191]:
        bad=bytearray(raw);bad[position]=1
        try:decode_page(bytes(bad))
        except AssertionError:checks.append('padding corruption detected at '+str(position))
        else:raise AssertionError('padding guard missing')
    for mutation in ['drop_backing','corrupt_word','skip_dirty_flush']:
        p=Planner();p.access(7,0,True,123)
        if mutation=='skip_dirty_flush':p.live[0]['dirty']=False
        p.checkpoint()
        if mutation=='drop_backing':p.backing.clear()
        if mutation=='corrupt_word':
            bad=bytearray(p.backing[0]);bad[1+7*20]^=1;p.backing[0]=bytes(bad)
        try:p.access(7,0,False,123)
        except AssertionError:checks.append(mutation+' detected')
        else:raise AssertionError('missing retained-data guard: '+mutation)
    out=Path('results/small_page_checkpoint_faults_20261023');out.mkdir()
    source=Path(__file__);model=source.with_name('replay_small_page_checkpoint.py')
    for f in [source,model]:(out/f.name).write_bytes(f.read_bytes())
    result={'status':'passed','checks':checks,'sources':{str(f.resolve()):sha(f) for f in [source,model]},'scope':'software reference only; mutations alter stored values or flush eligibility, no RTL proof'}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
