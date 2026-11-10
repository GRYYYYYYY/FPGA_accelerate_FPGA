"""Freeze all eight actual-restored CP cases only after their unique owner exits."""
from pathlib import Path
import json
import shutil
from run_checkpoint_authority import ROOT, sha

base=Path('/tmp/B_state_residency_offer_20261025');queue=base/'checkpoint_edit_matrix_queue_v1'
qm=json.loads((queue/'manifest.json').read_text())
assert qm['status']=='observed' and qm['stage']=='complete'
assert not Path('/proc',str(qm['runner_pid'])).exists()
report=ROOT/'results/checkpoint_edit_matrix_20261030.json';r=json.loads(report.read_text())
assert sha(report)==qm['result_sha256'] and r['queue_runner_sha256']==qm['runner_sha256']
assert sha(queue/'runner.py')==qm['runner_sha256']==sha(ROOT/'scripts/run_checkpoint_edit_matrix_queue_v1.py')
assert r['status']=='eight_cp_behavioral_cases_restored' and r['total_case_file_comparisons']==216
assert r['cases']==qm['cases'] and r['anchor']==qm['anchor'] and len(r['cases'])==7
assert r['physical_analysis_sha256']==qm['physical_analysis_sha256']==sha(ROOT/'results/checkpoint_edit_route_recovery_timing_20261030.json')
pre=json.loads((ROOT/'results/checkpoint_edit_matrix_preflight_20261030.json').read_text())
assert {c['target'] for c in pre['cases']}=={c['target'] for c in r['cases']}
assert r['anchor']['target']=='checkpoint_edit_system_crc_pressure_v1'
struct=base/'checkpoint_edit_synth_v1';sm=json.loads((struct/'manifest.json').read_text())
sa=json.loads((struct/'source_bound_audit.json').read_text());srp=ROOT/'results/checkpoint_edit_synth_v1_restore_20261025.json'
sr=json.loads(srp.read_text());assert sa['status']==sr['status']=='passed' and sr['audit_byte_identical']
assert sa['manifest_sha256']==sha(struct/'manifest.json') and sr['audit_sha256']==sha(struct/'source_bound_audit.json')
assert sa['check_timing_counts']['loops']==0 and not sa['timing_loop_warnings']
assert len(sm['rtl'])==133
manifests={};audits={};receipts={}
for case in r['cases']+[r['anchor']]:
    name=case['target'];p=base/name;m=json.loads((p/'manifest.json').read_text());a=json.loads((p/'source_bound_audit.json').read_text())
    rp=ROOT/'results'/f'{name}_restore_20261025.json';receipt=json.loads(rp.read_text())
    assert m['status']=='observed' and a['status']==receipt['status']=='passed' and receipt['audit_byte_identical']
    assert sha(rp)==case['restore_sha256'] and receipt['archive_sha256']==case['archive_sha256']
    assert a['manifest_sha256']==sha(p/'manifest.json') and receipt['audit_sha256']==sha(p/'source_bound_audit.json')==case['audit_sha256']
    assert len(a['exact_comparisons'])==27 and a['finish_time']==case['finish_time']
    assert a['checkpoint_edit_exclusion']==case['checkpoint_edit_exclusion']
    assert len(m['rtl'])==136 and set(m['rtl'])==set(sm['rtl'])|{'axi_file_memory.sv','tb_directory_observer.sv','tb_query_fault.sv'}
    for source in sm['rtl']:
        assert sha(p/'sources'/source)==m['sources'][source]['sha256']==sm['sources'][source]
    if name!=r['anchor']['target']:
        assert a['auditor_sha256']==sha(ROOT/'scripts/audit_checkpoint_edit_matrix_case_v1.py')
    manifests[name]=m;audits[name]=a;receipts[name]=rp
freeze=ROOT/'results/checkpoint_edit_matrix_sources_20261030';assert not freeze.exists();freeze.mkdir()
files={};source_map={};seen={}
def copy(source,relative):
    target=freeze/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target)
    files[str(relative)]=dict(source=str(source),sha256=sha(target));assert sha(source)==files[str(relative)]['sha256']
for name,m in manifests.items():
    source_map[name]={};p=base/name
    for n,entry in m['sources'].items():
        source=p/'sources'/n;digest=sha(source);assert digest==entry['sha256']
        if digest not in seen:
            rel=Path('sources')/name/n;copy(source,rel);seen[digest]=str(rel)
        source_map[name][n]=seen[digest]
    for n in ['manifest.json','source_bound_audit.json']:copy(p/n,Path('cases')/name/n)
    copy(receipts[name],Path('cases')/name/'restoration.json')
for name,entry in qm['bound'].items():
    assert sha(Path(entry['source']))==entry['sha256']==sha(queue/'bound'/name)
    copy(queue/'bound'/name,Path('bound')/name)
for source,relative in [(report,'report.json'),(queue/'manifest.json','queue_manifest.json'),
                        (struct/'source_bound_audit.json','structural_audit.json'),(srp,'structural_restoration.json')]:
    copy(source,Path('reports')/relative)
for name in ['freeze_checkpoint_edit_matrix_v1.py','run_checkpoint_edit_matrix_queue_v1.py']:
    copy(ROOT/'scripts'/name,Path('scripts')/name)
(freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=files,source_map=source_map,cases=8,
    case_file_comparisons=216,timing_qualified=False,board_acceptance=False,scope=r['scope']),indent=2,sort_keys=True)+'\n')
print('CP_MATRIX_FROZEN',len(files))
