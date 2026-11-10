"""Accept the observed native candidate only after byte-identical restored audit."""
from pathlib import Path
import json
import shutil
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,restored


def main():
    p=BASE/'config_native_publication_system_v1';m,a,evidence=restored(p)
    assert m['stage']=='complete' and identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_config_native_publication_system_v1.py')
    assert len(a['exact_comparisons'])==27 and a['production_sources']==133 and a['verification_sources']==4
    assert a['state_bits']==4810 and a['output_bits']==7238
    assert a['native_publication']['checks']>0 and a['native_publication']['publications']>0
    assert a['host_edit']['host_writes']==1 and a['host_edit']['final_pending']==0
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    for name,e in m['sources'].items():assert sha(p/'sources'/name)==e['sha256']
    out=ROOT/'results/config_native_publication_system_20261030.json'
    freeze=ROOT/'results/config_native_publication_system_sources_20261030'
    assert not out.exists() and not freeze.exists()
    report=dict(status='native_publication_host_edit_system_actual_restored',audit=a,restoration=read(evidence[2]),
        candidate_selected=False,timing_qualified=False,board_acceptance=False,
        scope='One matched CP host-edit full system with passive original state/output observer and27 exact external files/cycles, actually restored. Original eight-case matrix is a predecessor, not a new candidate eight-case matrix. Matched OOC/physical measurement and remaining scope still required.')
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');freeze.mkdir();files={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        files[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==files[str(relative)]['sha256']
    for name in m['sources']:copy(p/'sources'/name,Path('sources')/name)
    for name in m['bound']:copy(p/'bound'/name,Path('bound')/name)
    for name in ['simulate.log','compile.stdout.log','elaborate.stdout.log','simulate.stdout.log','run.tcl']:
        copy(p/'pressure'/name,Path('logs')/name)
    for source in evidence+[out,Path(__file__).resolve()]:copy(source,Path('reports')/(str(len(files))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,exact_file_comparisons=27,
        candidate_selected=False,timing_qualified=False,board_acceptance=False),indent=2,sort_keys=True)+'\n')
    print('NATIVE_PUBLICATION_SYSTEM_FROZEN',len(files))


if __name__=='__main__':main()
