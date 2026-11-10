"""Gate a CP-only stage overlay on actual unit acceptance and retain monitors."""
from pathlib import Path
import sys
import importlib.util

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from host_edit_system_common_v1 import BASE,sha,read,restored,identity,verify_freeze

REFERENCE=BASE/'checkpoint_host_edit_system_v1'
CANDIDATE=ROOT/'hardware/variants/stage_static_cp_system_sources_v1'


def load(path,name):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    return module


def sources(reference):
    assert reference==REFERENCE
    # Check accepted evidence before touching the possibly live/restoring unit root.
    report=ROOT/'results/stage_static_cp_units_20261030.json'
    assert report.exists(), 'Wait for twelve units actual restore and freeze'
    accepted=read(report)
    assert accepted['status']=='isolated_stage_twelve_units_actual_restored'
    frozen=verify_freeze(ROOT/'results/stage_static_cp_units_sources_20261030')
    unit=BASE/'stage_static_cp_units_v2';um,ua,uf=restored(unit)
    assert accepted['audit']==ua and um['stage']=='complete' and um['exit_code']==0
    assert identity(um['runner_pid'])!=str(um['runner_start_ticks'])
    assert len(ua['cases'])==12 and ua['exact_trace_comparisons']==8 and ua['generic_overlap_preserved']
    for mode in ['baseline','default','factored']:
        for suite in ['checkpoint','checkpoint32']:
            c=ua['cases'][mode+'_'+suite]
            assert c['stage_captures']>0 and c['stage_imports']>0 and c['stage_checked_cycles']>0
    functional=ROOT/'results/stage_bank_functional_matrix_20261030.json'
    fa=read(functional)
    assert fa['status']=='four_slot_functional_matrix_outcomes_actual_restored'
    assert fa['audit']['functional_passed_modes']==['static']
    ff=verify_freeze(ROOT/'results/stage_bank_functional_matrix_sources_20261030')
    rm,ra,rf=restored(reference)
    assert len(ra['exact_comparisons'])==27 and ra['host_edit']['host_writes']==1
    vm=read(CANDIDATE/'manifest.json')
    for n,h in vm['bound'].items():assert sha(n)==h
    fixed={}
    for name,entry in vm['sources'].items():
        assert sha(reference/'sources'/name)==entry['baseline']
        for role in ['baseline','fixed']:assert sha(CANDIDATE/role/name)==entry[role]
        fixed[name]=(CANDIDATE/'fixed'/name).read_text()
    assert set(fixed)=={'route_commit_controller.sv','route_commit_host_adapter.sv'}
    tools=[HERE/'build.py',ROOT/'hardware/variants/route_path_system_v1/build.py',
           ROOT/'hardware/variants/route_stage_system_v1/build.py',CANDIDATE/'manifest.json']
    evidence={str(p):sha(p) for p in uf+rf+[report,frozen,functional,ff]+tools}
    return fixed,evidence


def monitored_tb(original):
    # These independently preserved references never use candidate sw_* wires.
    path=load(ROOT/'hardware/variants/route_path_system_v1/build.py','cp_stage_old_path_bank')
    stage=load(ROOT/'hardware/variants/route_stage_system_v1/build.py','cp_stage_old_stage_bank')
    return stage.monitored_tb(path.monitored_tb(original))
