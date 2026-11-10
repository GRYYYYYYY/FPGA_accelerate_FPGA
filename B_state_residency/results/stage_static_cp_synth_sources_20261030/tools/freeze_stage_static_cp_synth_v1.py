"""Freeze actually restored OOC observations without claiming timing closure."""
from pathlib import Path
import json
import shutil
from stage_static_cp_synth_common_v1 import ROOT,TARGET,REFERENCE,TOOLS,sha,read,identity,restored


def main():
    p=TARGET;m,a,evidence=restored(p)
    assert m['stage']=='complete' and m['exit_code']==0 and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_stage_static_cp_synth_v1.py')
    assert a['timing_qualified'] is False and m['reference']==str(REFERENCE)
    ra=read(REFERENCE/'source_bound_audit.json');assert sha(REFERENCE/'source_bound_audit.json')==m['reference_audit_sha256']
    delta={key:a['utilization'][key]-ra['utilization'][key] for key in ['LUT','FF','BRAM','DSP','URAM']}
    out=ROOT/'results/stage_static_cp_synth_20261030.json'
    freeze=ROOT/'results/stage_static_cp_synth_sources_20261030'
    assert not out.exists() and not freeze.exists()
    for name,digest in m['sources'].items():assert sha(p/'sources'/name)==digest
    for name,e in m['bound'].items():assert sha(e['source'])==e['sha256']==sha(p/'bound'/name)
    report=dict(status='matched_static_stage_ooc_actual_restored',audit=a,restoration=read(evidence[2]),
        reference_audit_sha256=sha(REFERENCE/'source_bound_audit.json'),utilization_delta_candidate_minus_reference=delta,
        preplacement_wns_delta_ns=a['preplacement_wns_ns']-ra['preplacement_wns_ns'],
        candidate_selected=False,timing_qualified=False,full_behavior_matrix_complete=False,board_acceptance=False,
        scope='Matched133-source isolated static stage OOC on preferred CP baseline; same top parameters/U280/10ns XDC and actual-restored functional predecessor. Worst endpoints may differ, so slack delta is not same-path proof. New static-stage eight-case matrix, physical implementation, IO timing and board proof remain separate.')
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');freeze.mkdir();files={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        files[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==files[str(relative)]['sha256']
    for name in m['sources']:copy(p/'sources'/name,Path('sources')/name)
    for name in m['bound']:copy(p/'bound'/name,Path('bound')/name)
    for source in evidence+[out,REFERENCE/'source_bound_audit.json']:
        copy(source,Path('reports')/(str(len(files))+'_'+source.name))
    for name in TOOLS:copy(ROOT/'scripts'/name,Path('tools')/name)
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,candidate_selected=False,
        timing_qualified=False,board_acceptance=False),indent=2,sort_keys=True)+'\n')
    print('STAGE_STATIC_CP_OOC_FROZEN',len(files))


if __name__=='__main__':main()
