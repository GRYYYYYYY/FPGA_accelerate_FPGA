"""Bind prepared behavioral-system tools; never submit the guarded experiment."""
import ast
import json
from host_edit_system_common_v1 import ROOT,read,sha,load


def main():
    result=ROOT/'results/stage_static_cp_system_tools_preparation_20261030.json'
    assert not result.exists()
    scripts=['run_stage_static_cp_system_v1.py','audit_stage_static_cp_system_v1.py',
        'freeze_stage_static_cp_system_v1.py','preflight_stage_static_cp_system_v1.py',
        'prepare_stage_static_cp_system_sources_v1.py','host_edit_system_common_v1.py',
        'config_native_publication_synth_common_v1.py','check_host_edit_trace_v1.py',
        'archive_offer_result.py','verify_search_retire_restore.py','restore_offer_result.py']
    paths=[ROOT/'scripts'/name for name in scripts]+[
        ROOT/'hardware/variants'/name/'build.py' for name in
        ['stage_static_cp_system_v1','route_path_system_v1','route_stage_system_v1']]
    for p in paths:ast.parse(p.read_text())
    receipts=[]
    for suffix,key,tool in [('builder','builder_sha256',paths[-3]),
        ('runner','runner_sha256',paths[0]),('auditor','auditor_sha256',paths[1]),
        ('freezer','freezer_sha256',paths[2])]:
        receipt=ROOT/'results'/f'stage_static_cp_system_{suffix}_preparation_20261030.json'
        assert read(receipt)[key]==sha(tool);receipts.append(receipt)
    candidate=ROOT/'hardware/variants/stage_static_cp_system_sources_v1'
    vm=read(candidate/'manifest.json')
    assert set(vm['sources'])=={'route_commit_controller.sv','route_commit_host_adapter.sv'}
    for n,e in vm['sources'].items():
        for role,digest in e.items():assert sha(candidate/role/n)==digest
    adapter=(candidate/'fixed/route_commit_host_adapter.sv').read_text()
    assert adapter.count('.STATIC_STAGE_WRITES(1),')==1
    assert adapter.replace('.STATIC_STAGE_WRITES(1),','',1)==(candidate/'baseline/route_commit_host_adapter.sv').read_text()
    builder=load('stage_static_preflight_builder',paths[-3])
    original=(builder.REFERENCE/'sources/tb_query_fault.sv').read_text()
    generated=builder.monitored_tb(original)
    assert 'ROUTE_PATH_BANK_PASS' in generated and 'ROUTE_STAGE_BANK_PASS' in generated
    assert not (builder.REFERENCE.parent/'stage_static_cp_system_v1').exists()
    result.write_text(json.dumps(dict(status='isolated_stage_system_tools_prepared_not_executed',
        tools={str(p):sha(p) for p in paths},preparation_receipts={str(p):sha(p) for p in receipts},
        candidate_manifest_sha256=sha(candidate/'manifest.json'),two_source_overlay_verified=True,
        full_system_execution_pending=True,full_system_netlist_validation_pending=True,
        scope='Source preparation only. Actual restored/frozen twelve-unit gate remains enforced by builder before directory creation.'),indent=2,sort_keys=True)+'\n')
    print('ISOLATED_STAGE_SYSTEM_TOOLS_BOUND',len(paths))


if __name__=='__main__':main()
