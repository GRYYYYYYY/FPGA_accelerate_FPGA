"""Freeze failed v4 and all-port snapshot evidence without reclassifying it PASS."""
from pathlib import Path
import json,re,shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,identity,verify_freeze


def main():
    refs={}
    for name,script in [('stage_static_cp_shadow_failure_probe_v2','audit_stage_static_cp_shadow_failure_probe_v2.py'),('stage_static_cp_shadow_system_v4','audit_stage_static_cp_shadow_failure_v2.py')]:
        p=BASE/name;receipt=ROOT/'results'/f'{name}_restore_20261025.json'
        assert receipt.exists(),'Wait for both actual restores'
        r=read(receipt);m=read(p/'manifest.json');a=read(p/'source_bound_audit.json')
        assert r['status']=='passed' and r['audit_byte_identical'] and r['auditor']==script
        assert sha(p/'source_bound_audit.json')==r['audit_sha256']
        assert a['status']=='passed' and not a['full_system_functional_netlist_validated']
        assert a['manifest_sha256']==sha(p/'manifest.json') and a['auditor_sha256']==sha(ROOT/'scripts'/script)
        assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
        index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
        refs[name]=dict(root=p,receipt=receipt,manifest=m,audit=a,restore=r)
    probe=refs['stage_static_cp_shadow_failure_probe_v2'];failed=refs['stage_static_cp_shadow_system_v4']
    assert failed['manifest']['status']=='failed' and failed['audit']['shadow_verdict']=='failed'
    assert probe['manifest']['status']=='observed' and probe['audit']['snapshot_and_checker_unchanged']
    pa=probe['audit'];expected={'cp_m_data','k_a_net','k_a_node','p_m_wdata'}
    for label,row in pa['output_inventory'].items():
        assert set(row['differences'])==expected and set(row['unknown_expected'])==expected and not row['unknown_actual']
        values=pa['observations'][label]
        for n in ['k_a_valid','k_a_ready','p_m_wvalid','cp_m_valid']:
            assert values['actual_'+n]==values['expected_'+n]=='0'
        assert values['drive_p_m_wready']=='1'
    sources=failed['root']/'sources'
    recovery=sources/'recovery_coordinator.sv';pager=sources/'expansion_20261024/pager/backend/scratch_page_axi_small.sv'
    rs=recovery.read_text();ps=pager.read_text()
    assert 'assign a_valid=!cold_rst&&state==AS;' in rs
    assert 'assign a_node=nodes[index];assign a_net=nets[index];' in rs
    assert 'if(j_valid&&j_ready&&!duplicate)begin nodes[journal_count]<=j_node;nets[journal_count]<=j_net;' in rs
    reset=rs.split('if(cold_rst)begin',1)[1].split('end else begin',1)[0]
    assert 'nodes[' not in reset and 'nets[' not in reset
    assert 'assign m_wdata=buffer_data;' in ps and 'assign m_wvalid=!rst && state==WRITE_DATA && buffer_valid;' in ps
    reset=ps.split('if(rst) begin',1)[1].split('end else begin',1)[0]
    assert 'buffer_data' not in reset and 'buffer_valid<=0' in reset
    assert 'if(in_valid && in_ready)begin buffer_valid<=1;buffer_data<=in_data;end' in ps
    for source in [recovery,pager]:
        rel=str(source.relative_to(sources));assert sha(source)==failed['manifest']['sources'][rel]['sha256']
    report=ROOT/'results/stage_static_cp_shadow_v4_failure_20261030.json'
    freeze=ROOT/'results/stage_static_cp_shadow_v4_failure_sources_20261030'
    assert not report.exists() and not freeze.exists()
    record=dict(status='v4_shadow_failure_and_all_port_probe_actual_restored',
        failed_audit=failed['audit'],probe_audit=pa,
        restorations={name:e['restore'] for name,e in refs.items()},
        sampled_differing_outputs=sorted(expected),sampled_other_output_differences=0,
        source_facts=dict(recovery_authority_payload='nodes/nets arrays not reset; direct read; request valid only in AS',pager_write_payload='buffer_data not reset; WVALID requires WRITE_DATA and buffer_valid'),
        shadow_verdict='failed',full_system_functional_netlist_validated=False,all_pin_strict_equivalence=False,
        candidate_selected=False,timing_qualified=False,board_acceptance=False,
        next_step='Systematic explicit interface-contract review before any new observer; no blanket X masking or automatic qualification from names.',
        scope='Exact failed snapshot observed at two timestamps only. Four known-vs-uninitialized payload differences while associated valid signals0. Original v4 still failed; no real CP transfer occurred. Does not prove later behavior, arbitrary inputs, valid-payload correctness, full protocol equivalence or simulator defect.')
    report.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n');freeze.mkdir();copied={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        copied[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==copied[str(relative)]['sha256']
    for name,e in refs.items():
        for source in [e['root']/'manifest.json',e['root']/'source_bound_audit.json',e['receipt'],Path(e['restore']['archive_index']),e['root']/'full/simulate.log',e['root']/'full/run.tcl']:
            copy(source,Path('evidence')/name/source.name)
    for name in ['shadow.sv','tb_query_fault.sv','recovery_coordinator.sv','expansion_20261024/pager/backend/scratch_page_axi_small.sv']:
        copy(sources/name,Path('sources')/name)
    tools=['probe_stage_static_cp_shadow_failure_v2.py','audit_stage_static_cp_shadow_failure_probe_v2.py','audit_stage_static_cp_shadow_failure_v2.py','freeze_stage_static_cp_shadow_failure_v2.py','run_stage_static_cp_shadow_system_v4.py','continue_stage_static_cp_shadow_system_v4.py','stage_static_cp_shadow_common_v4.py']
    for name in tools:copy(ROOT/'scripts'/name,Path('tools')/name)
    for source in [report,ROOT/'results/stage_static_cp_port_schema_20261030.json',ROOT/'results/stage_static_cp_shadow_system_v4_tools_preparation_20261030.json']:
        copy(source,Path('reports')/source.name)
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=copied,full_system_functional_netlist_validated=False,shadow_verdict='failed'),indent=2,sort_keys=True)+'\n')
    verify_freeze(freeze);print('V4_FAILURE_FROZEN',len(copied))


if __name__=='__main__':main()
