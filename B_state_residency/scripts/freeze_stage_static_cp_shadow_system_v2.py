"""Freeze an actually restored complete-host functional shadow run, no timing claim."""
from pathlib import Path
import json
import shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity,verify_freeze


def main():
    p=BASE/'stage_static_cp_shadow_system_v2'
    receipt=ROOT/'results/stage_static_cp_shadow_system_v2_restore_20261025.json'
    assert receipt.exists(), 'Wait for full system actual restore and byte-identical audit'
    m,a,files=restored(p)
    assert m['stage']=='complete' and m['mode']=='full_netlist_shadow'
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_stage_static_cp_shadow_system_v2.py')
    assert len(a['exact_comparisons'])==27 and a['host_edit']['host_writes']==1
    assert a['full_system_functional_netlist_validated'] and a['shadow_checks']>0 and a['parameters']['SLOTS']==32
    assert a['production_sources']==133 and a['verification_sources']==3
    for obs in a['route_bank_observations'].values():assert all(value>0 for value in obs.values())
    r=read(receipt);index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
    prep=ROOT/'results/stage_static_cp_shadow_system_v2_tools_preparation_20261030.json'
    tools=read(prep)['tools']
    for source,digest in tools.items():assert sha(source)==digest
    out=ROOT/'results/stage_static_cp_shadow_system_v2_20261030.json'
    freeze=ROOT/'results/stage_static_cp_shadow_system_v2_sources_20261030'
    assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status='full_capacity_host_netlist_shadow_actual_restored',audit=a,restoration=r,
        candidate_selected=False,timing_qualified=False,board_acceptance=False,
        full_system_functional_netlist_validated=True,
        scope='One complete-host structural shadow fixture,346 strict outputs and27 exact external files with original behavioral monitors retained. Gate receives RTL-driven inputs, not independent memory agents. Arbitrary parameter/XZ/formal, physical timing and board proof remain separate.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();entries={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        entries[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==entries[str(relative)]['sha256']
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256'];copy(p/'sources'/name,Path('sources')/name)
    for name,digest in m['shadow_inputs'].items():
        assert sha(p/'sources'/name)==digest;copy(p/'sources'/name,Path('shadow')/name)
    assert sha(p/'namespace.json')==m['namespace_sha256'];copy(p/'namespace.json',Path('shadow/namespace.json'))
    for name,e in m['bound'].items():
        assert sha(e['source'])==sha(p/'bound'/name)==e['sha256'];copy(p/'bound'/name,Path('bound')/name)
    for source in files+[out,prep]:copy(source,Path('reports')/(str(len(entries))+'_'+source.name))
    for source in tools:copy(Path(source),Path('tools')/(str(len(entries))+'_'+Path(source).name))
    for name in a['exact_comparisons']:
        assert sha(p/'pressure'/name)==a['exact_comparisons'][name]['sha256']
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,
        timing_qualified=False,full_system_functional_netlist_validated=True),indent=2,sort_keys=True)+'\n')
    verify_freeze(freeze)
    print('FULL_HOST_NETLIST_SHADOW_ACTUAL_RESTORE_FROZEN',len(entries))


if __name__=='__main__':main()
