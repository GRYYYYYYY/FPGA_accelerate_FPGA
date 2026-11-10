"""Freeze candidate unit observations only after real archive restoration."""
from pathlib import Path
import json
import shutil
from config_publication_units_common_v1 import ROOT,TARGET,CASES,PAIRS,sha,read,identity,restored


def main():
    p=TARGET;m,a,evidence=restored(p)
    assert m['stage']=='complete' and not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert set(a['cases'])==set(CASES) and a['full_bank_cycle_comparisons']==a['exact_event_comparisons']==3
    assert [(c['reference'],c['candidate']) for c in a['comparisons']]==PAIRS
    assert a['state_bits']==4810 and a['output_bits']==7238
    assert a['native_prepared_full_nonversion_invariant'] and a['generic_default_preserves_unaliased_xz_counterexample']
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_config_publication_units_v1.py')
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    for name in CASES:
        for file,digest in m['cases'][name]['artifacts'].items():assert sha(p/name/file)==digest
    out=ROOT/'results/config_native_publication_units_20261030.json'
    freeze=ROOT/'results/config_native_publication_units_sources_20261030'
    assert not out.exists() and not freeze.exists()
    report=dict(status='five_native_publication_unit_modes_restored',audit=a,restoration=read(evidence[2]),
        candidate_selected=False,timing_qualified=False,board_acceptance=False,
        scope='Actual restored five-mode original/default/native-enabled unit comparison, full binary four-state banks each positive edge. Requires separate native full-system monitor/comparison and matched OOC/physical experiments before selection.')
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');freeze.mkdir();files={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        files[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==files[str(relative)]['sha256']
    for name in m['bound']:copy(p/'bound'/name,Path('bound')/name)
    for name in CASES:
        for file in ['config_restore_controller.sv','tb.sv','run.tcl','events.txt','bank_trace.txt','simulate.log',
                     'compile.stdout.log','elaborate.stdout.log','simulate.stdout.log']:
            copy(p/name/file,Path('cases')/name/file)
    for source in evidence+[out,Path(__file__).resolve()]:copy(source,Path('reports')/(str(len(files))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,
        full_bank_cycle_comparisons=3,candidate_selected=False,timing_qualified=False),indent=2,sort_keys=True)+'\n')
    print('PUBLICATION_UNITS_FROZEN',len(files))


if __name__=='__main__':main()
