"""Freeze only actually restored full-capacity host evidence."""
from pathlib import Path
import json
import shutil
import sys
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity,verify_freeze


def main():
    mode=sys.argv[1];assert mode in ['baseline','static']
    p=BASE/f'stage_static_cp_host_full_{mode}_v1'
    receipt=ROOT/'results'/f'{p.name}_restore_20261025.json'
    assert receipt.exists(),'Wait for full-capacity actual restore'
    m,a,files=restored(p)
    assert m['stage']=='complete' and m['mode']==mode+'_full_capacity'
    assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_stage_static_cp_host_full_v1.py')
    assert a['parameters']['SLOTS']==32 and len(a['outputs'])==27
    assert a['host_edit']['host_writes']==1 and a['host_edit']['final_dirty']==1
    assert a['paired_exact_comparisons']==(27 if mode=='static' else 0)
    r=read(receipt);index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
    prep=ROOT/'results/stage_static_cp_host_full_tools_preparation_20261030.json'
    tools=read(prep)['tools']
    for name,h in tools.items():assert sha(name)==h
    out=ROOT/'results'/f'stage_static_cp_host_full_{mode}_20261030.json'
    freeze=ROOT/'results'/f'stage_static_cp_host_full_{mode}_sources_20261030'
    assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status=f'full_capacity_host_{mode}_actual_restored',
        audit=a,restoration=r,candidate_selected=False,timing_qualified=False,
        full_system_functional_netlist_validated=False,
        scope='Explicit full-capacity host RTL reference/candidate. Full-capacity prefix and host edit/CRC/atomicity checked; static paired27 outputs/timing exact. Functional netlist validation remains separate.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();entries={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(source,dest);entries[str(relative)]=dict(source=str(source),sha256=sha(source))
        assert sha(dest)==entries[str(relative)]['sha256']
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256'];copy(p/'sources'/name,Path('sources')/name)
    for name,e in m['bound'].items():
        assert sha(e['source'])==sha(p/'bound'/name)==e['sha256'];copy(p/'bound'/name,Path('bound')/name)
    for source in files+[out,prep]:copy(source,Path('reports')/f'{len(entries):03d}_{source.name}')
    for source in tools:copy(Path(source),Path('tools')/f'{len(entries):03d}_{Path(source).name}')
    for name,e in a['outputs'].items():assert sha(p/'full'/name)==e['sha256']
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,
        timing_qualified=False,full_system_functional_netlist_validated=False),indent=2,sort_keys=True)+'\n')
    verify_freeze(freeze)
    print('FULL_CAPACITY_HOST_RESTORED_FROZEN',mode,len(entries))


if __name__=='__main__':main()
