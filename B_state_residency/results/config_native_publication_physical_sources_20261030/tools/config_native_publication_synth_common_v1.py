"""Matched OOC source gates, validated child runtime, and non-killing waits."""
from pathlib import Path
import os
import subprocess
import time
from host_edit_system_common_v1 import ROOT,BASE,sha,read,identity,restored,verify_freeze

TARGET=BASE/'config_native_publication_synth_v1'
REFERENCE=BASE/'checkpoint_edit_synth_v1'
FULL=BASE/'config_native_publication_system_v1'
VARIANT=ROOT/'hardware/variants/config_native_publication_v1'
PREPARATION=ROOT/'results/config_native_publication_synth_tools_preparation_20261030.json'
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin/vivado')
TOOLS=['config_native_publication_synth_common_v1.py','prepare_config_native_publication_synth_v1.py',
       'run_config_native_publication_synth_v1.py','inspect_config_native_publication_synth_v1.py',
       'audit_config_native_publication_synth_v1.py','freeze_config_native_publication_synth_v1.py',
       'analyze_restore_seed_loops.py','audit_restore_seed_diagnostics.py','read_tcl_list_records.tcl',
       'archive_offer_result.py','verify_search_retire_restore.py','restore_offer_result.py',
       'host_edit_system_common_v1.py','run_checkpoint_authority.py']
LIBRARIES=[Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/lib/lnx64.o/libtcmalloc.so.4'),
           Path('/lib/x86_64-linux-gnu/libudev.so.1')]


def validate_production_rtl(rtl):
    assert len(rtl)==len(set(rtl))==133
    assert all(not Path(name).name.startswith('tb_') and Path(name).name not in ['axi_file_memory.sv','config_restore_controller_observer.sv'] for name in rtl)
    return rtl


def runtime_environment():
    report=ROOT/'results/udev_runtime_recovery_20261030.json';r=read(report)
    assert r['status']=='runtime_controls_restored' and r['audit']['status']=='passed'
    assert r['restoration']['status']=='passed' and r['restoration']['audit_byte_identical']
    original=Path(r['restoration']['restored_root'])/'source_bound_audit.json'
    assert sha(original)==r['restoration']['audit_sha256'] and read(original)==r['audit']
    expected=r['audit']['runtime_library_sha256'];assert set(expected)==set(map(str,LIBRARIES))
    for path in LIBRARIES:assert sha(path)==expected[str(path)]
    assert not os.environ.get('LD_PRELOAD'),'Use a dedicated child environment'
    env=os.environ.copy();env['LD_PRELOAD']=':'.join(map(str,LIBRARIES))
    return env,dict(LD_PRELOAD=env['LD_PRELOAD'],library_sha256=expected,runtime_report_sha256=sha(report))


def evidence():
    accepted=ROOT/'results/config_native_publication_system_20261030.json'
    assert accepted.exists(),'Wait for candidate full-system actual restore/freeze'
    frozen=verify_freeze(ROOT/'results/config_native_publication_system_sources_20261030')
    fm,fa,full_files=restored(FULL);report=read(accepted)
    assert report['status']=='native_publication_host_edit_system_actual_restored' and report['audit']==fa
    assert fm['stage']=='complete' and identity(fm['runner_pid'])!=str(fm['runner_start_ticks'])
    assert len(fa['exact_comparisons'])==27 and fa['production_sources']==133 and fa['verification_sources']==4
    assert fa['native_publication']['checks']>0 and fa['native_publication']['publications']>0
    rm,ra,reference_files=restored(REFERENCE)
    assert rm['exit_code']==0 and rm['part']=='xcu280-fsvh2892-2L-e' and len(rm['rtl'])==133
    assert ra['check_timing_counts']['loops']==0 and not ra['timing_loop_warnings'] and not ra['critical_warnings']
    assert ra['facts']['latches']==ra['facts']['blackboxes']==0
    cm=read(VARIANT/'manifest.json');assert set(cm['sources'])=={'config_restore_controller.sv','residency_system.sv'}
    for path,digest in cm['bound'].items():assert sha(path)==digest
    assert set(rm['rtl']).issubset(fm['rtl']) and len(fm['rtl'])==137
    for name in rm['rtl']:
        original=sha(REFERENCE/'sources'/name);assert original==rm['sources'][name]
        expected=cm['sources'][name]['fixed'] if name in cm['sources'] else original
        assert sha(FULL/'sources'/name)==fm['sources'][name]['sha256']==expected
    for name,entry in cm['sources'].items():
        assert sha(VARIANT/'baseline'/name)==entry['baseline']==rm['sources'][name]
        assert sha(VARIANT/'fixed'/name)==entry['fixed']
    validate_production_rtl(rm['rtl'])
    tools=read(PREPARATION);assert tools['status']=='native_publication_synth_tools_prepared_not_executed'
    assert set(tools['tools'])=={str(ROOT/'scripts'/name) for name in TOOLS}
    for path,digest in tools['tools'].items():assert sha(path)==digest
    runtime_environment()
    files=full_files+reference_files+[accepted,frozen,VARIANT/'manifest.json',PREPARATION,
        ROOT/'results/udev_runtime_recovery_20261030.json']
    files += [VARIANT/role/name for role in ['baseline','fixed'] for name in cm['sources']]
    files += [ROOT/'scripts'/name for name in TOOLS]
    return rm,ra,fm,fa,{str(path):sha(path) for path in files}


def memory_admission(record,save):
    stable=None;deadline=time.monotonic()+10800
    while True:
        now=time.monotonic();cg=Path('/sys/fs/cgroup');current,limit=int((cg/'memory.current').read_text()),int((cg/'memory.max').read_text())
        stable=(now if stable is None else stable) if current*4<=limit*3 else None
        seconds=0 if stable is None else now-stable
        record['memory_admission']=dict(current_bytes=current,limit_bytes=limit,stable_seconds=seconds);save()
        if seconds>=60:return
        assert now<deadline,'Memory observation expired before launching Vivado'
        time.sleep(10)


def wait_preserving(child,seconds,record,save):
    try:return child.wait(timeout=seconds)
    except subprocess.TimeoutExpired:
        record['status']='observation_timeout'
        record.setdefault('observation_timeouts',[]).append(dict(pid=child.pid,start_ticks=identity(child.pid),after_seconds=seconds))
        save();print('OBSERVATION_TIMEOUT_CHILD_PRESERVED',child.pid,flush=True)
    # Keep wait ownership and the eventual real exit code. This is observation,
    # never a restart, retry, signal or inferred completion after a timeout.
    while True:
        try:return child.wait(timeout=30)
        except subprocess.TimeoutExpired:pass
