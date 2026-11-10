"""Freeze an actual-restored early diagnostic without full-system acceptance."""
from pathlib import Path
import json,shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,verify_freeze


def main():
    p=BASE/'stage_static_cp_shadow_runtime_probe_v1';m,a,files=restored(p)
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_stage_static_cp_shadow_runtime_probe_v1.py')
    assert a['same_compiled_snapshot'] and not a['source_or_checker_modified'] and not a['original_solver_restarted']
    assert a['reached_time_ps']==1000000 and a['completed_steps']==100 and not a['delta_limit_reached']
    assert a['final_observer_counters']['checks']==149 and not a['full_system_functional_netlist_validated']
    r=read(ROOT/'results/stage_static_cp_shadow_runtime_probe_v1_restore_20261025.json');index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
    out=ROOT/'results/stage_static_cp_shadow_runtime_probe_20261030.json';freeze=ROOT/'results/stage_static_cp_shadow_runtime_probe_sources_20261030';assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status='bounded_runtime_probe_actual_restored_not_full_gate',audit=a,restoration=r,full_system_functional_netlist_validated=False,candidate_selected=False,timing_qualified=False,official_option_reference='https://www.amd.com/content/dam/xilinx/support/documents/sw_manuals/xilinx2022_1/ug900-vivado-logic-simulation.pdf',local_option_verified='Installed XSim2022.2 -help includes maxdeltaid; no option/source/checker changes applied to original full job.',scope='Early1us diagnostic only. Original full job independently advanced beyond the visible initialization prefix; no original stop/restart. Does not prove full completion or general speed improvement. Legacy ISIM AR41339 was not applied as an XSim fix.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();copied={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);copied[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==copied[str(relative)]['sha256']
    for n in ['probe_stage_static_cp_shadow_runtime_v1.py','audit_stage_static_cp_shadow_runtime_probe_v1.py','freeze_stage_static_cp_shadow_runtime_probe_v1.py']:copy(ROOT/'scripts'/n,Path('tools')/n)
    for n in ['manifest.json','parent_manifest_at_start.json','source_bound_audit.json','full/run.tcl','full/simulate.log','full/stdout.log']:copy(p/n,Path('evidence')/n)
    for source in files+[out]:copy(source,Path('reports')/(str(len(copied))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=copied,full_system_functional_netlist_validated=False),indent=2,sort_keys=True)+'\n');verify_freeze(freeze);print('BOUNDED_RUNTIME_DIAGNOSTIC_FROZEN',len(copied))


if __name__=='__main__':main()
