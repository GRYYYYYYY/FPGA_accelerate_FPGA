"""Create a new route-only attempt after terminal failure and verified runtime controls."""
from pathlib import Path
import json
import shutil
import sys
from run_checkpoint_authority import ROOT, sha

def main():
    out=Path(sys.argv[1]).resolve(); base=out.parent
    assert base==Path('/tmp/B_state_residency_offer_20261025')
    assert out.name=='checkpoint_edit_route_recovery_v1' and not out.exists()
    failed=base/'checkpoint_edit_physical_v1'; queue=base/'checkpoint_edit_physical_queue_v2'
    fm=json.loads((failed/'manifest.json').read_text()); qm=json.loads((queue/'manifest.json').read_text())
    assert fm['status']=='failed' and fm['exit_code']==134
    assert qm['status']=='failed' and qm['stage']=='physical_run'
    assert not Path('/proc',str(qm['runner_pid'])).exists()
    for pid in [2164892,2164928]: assert not Path('/proc',str(pid)).exists()
    assert not (failed/'routed.dcp').exists() and (failed/'placed.dcp').stat().st_size>0
    crash=failed/'hs_err_pid2164928.log'
    assert 'udev_enumerate_scan_devices' in crash.read_text() and 'prepAndTransmitWebtalkData' in crash.read_text()
    assert 'Router Completed Successfully' in (failed/'stdout.log').read_text()
    for name,entry in qm['bound'].items():
        assert sha(Path(entry['source']))==entry['sha256']==sha(queue/'bound'/name),name
    for name,digest in fm['inputs'].items(): assert sha(failed/name)==digest,name
    assert sha(failed/'run.tcl')==fm['tcl_sha256']
    assert sha(failed/'runner.py')==fm['runner_sha256']==sha(ROOT/'scripts/run_state_ooc_physical.py')
    assert fm['preparer_sha256']==sha(ROOT/'scripts/prepare_state_ooc_physical.py')
    assert fm['template_sha256']==sha(ROOT/'hardware/scripts/implement_state_ooc.tcl')
    ref=Path(fm['reference']); full=Path(fm['full_system_reference'])
    assert ref.name=='checkpoint_edit_synth_v1' and full.name=='checkpoint_edit_system_crc_pressure_v1'
    rm=json.loads((ref/'manifest.json').read_text()); sm=json.loads((full/'manifest.json').read_text())
    assert len(fm['rtl'])==133 and fm['rtl']==rm['rtl'] and fm['parameters']==rm['parameters']
    for root,key in [(ref,'synthesis_audit_sha256'),(full,'full_system_audit_sha256')]:
        audit=json.loads((root/'source_bound_audit.json').read_text())
        receipt=json.loads((ROOT/'results'/f'{root.name}_restore_20261025.json').read_text())
        assert audit['status']==receipt['status']=='passed' and receipt['audit_byte_identical']
        assert audit['manifest_sha256']==sha(root/'manifest.json')
        assert receipt['audit_sha256']==sha(root/'source_bound_audit.json')==fm[key]
    for name in fm['rtl']:
        assert sha(failed/'sources'/name)==sha(ref/'sources'/name)==sha(full/'sources'/name)==rm['sources'][name]==sm['sources'][name]['sha256']
    controls=base/'udev_route_probe_v2'
    ca=json.loads((controls/'source_bound_audit.json').read_text())
    crp=ROOT/'results/udev_route_probe_v2_restore_20261025.json'
    cr=json.loads(crp.read_text())
    assert ca['status']==cr['status']=='passed' and cr['audit_byte_identical']
    assert ca['manifest_sha256']==sha(controls/'manifest.json')
    assert cr['audit_sha256']==sha(controls/'source_bound_audit.json')
    assert ca['auditor_sha256']==sha(ROOT/'scripts/audit_udev_route_probe_v2.py')
    assert ca['vivado_controls']['preloaded_udev']['reopened']
    for name,digest in ca['artifact_sha256'].items(): assert sha(controls/name)==digest
    for name,digest in ca['external_evidence_sha256'].items(): assert sha(Path(name))==digest
    libs=list(ca['runtime_library_sha256'])
    assert libs[0].endswith('/libtcmalloc.so.4') and libs[1]=='/lib/x86_64-linux-gnu/libudev.so.1'
    for name,digest in ca['runtime_library_sha256'].items(): assert sha(Path(name))==digest
    memory=Path('/sys/fs/cgroup')
    assert int((memory/'memory.current').read_text())*4<=int((memory/'memory.max').read_text())*3
    out.mkdir(); copied={}
    def copy(src,relative):
        dest=out/relative; dest.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(src,dest); copied[str(relative)]=sha(dest); assert copied[str(relative)]==sha(src)
    for name in fm['inputs']: copy(failed/name,name)
    copy(failed/'placed.dcp','inputs/resume_placed.dcp')
    prior=['manifest.json','run.tcl','runner.py','stdout.log','vivado.log','milestones.txt',crash.name,
           'clocks_input.rpt','utilization_input.rpt','methodology_input.rpt','check_timing_input.rpt',
           'loops_input.rpt','constraints_input.xdc','utilization_placed.rpt','timing_placed.rpt']
    for name in prior: copy(failed/name,'prior/'+name)
    copy(queue/'manifest.json','prior/queue_manifest.json')
    copy(controls/'source_bound_audit.json','inputs/runtime_audit.json')
    copy(crp,'inputs/runtime_restoration.json')
    for name in ['scripts/prepare_state_route_recovery_v1.py','scripts/run_state_route_recovery_v1.py',
                 'scripts/run_checkpoint_authority.py','hardware/scripts/resume_state_route_v1.tcl',
                 'hardware/scripts/inspect_state_route_v1.tcl']:
        copy(ROOT/name,'tools/'+Path(name).name)
    for name,template in [('run.tcl','resume_state_route_v1.tcl'),('inspect.tcl','inspect_state_route_v1.tcl')]:
        (out/name).write_text((ROOT/'hardware/scripts'/template).read_text().replace('@OUT@',str(out)))
    m={key:fm[key] for key in ['reference','full_system_reference','part','top','clock_period_ns','parameters','rtl',
                              'synthesis_audit_sha256','full_system_audit_sha256']}
    m.update(status='prepared',failed_attempt=str(failed),failed_queue=str(queue),inputs=copied,
             saved_placement_sha256=sha(out/'inputs/resume_placed.dcp'),
             runtime_preload=':'.join(libs),runtime_library_sha256=ca['runtime_library_sha256'],
             runtime_audit_sha256=sha(controls/'source_bound_audit.json'),
             tcl_sha256=sha(out/'run.tcl'),inspect_tcl_sha256=sha(out/'inspect.tcl'),
             preparer_sha256=sha(Path(__file__)),runner_sha256=sha(ROOT/'scripts/run_state_route_recovery_v1.py'),
             timing_qualified=False,board_acceptance=False,
             scope='Route-only recovery from the exact original saved placement. Original 133 RTL sources, '
                   'U280 part, parameters and 10ns research clock remain bound. Child-process preload of '
                   'unchanged bundled tcmalloc and system libudev; no library stub, patch, license or preference change. '
                   'No new placement, IO budgets, clock source locations, timing exceptions or board claim.')
    (out/'manifest.json').write_text(json.dumps(m,indent=2,sort_keys=True)+'\n')
    print('STATE_ROUTE_RECOVERY_PREPARED',out.name,len(copied))

if __name__=='__main__': main()
