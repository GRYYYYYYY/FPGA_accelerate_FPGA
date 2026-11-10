"""Freeze an actually restored complete-host functional shadow run, no timing claim."""
from pathlib import Path
import json
import shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,identity,verify_freeze


def main():
    p=BASE/'stage_static_cp_shadow_system_v6'
    receipt=ROOT/'results/stage_static_cp_shadow_system_v6_restore_20261025.json'
    assert receipt.exists(), 'Wait for full system actual restore and byte-identical audit'
    m,a,files=restored(p)
    assert m['stage']=='complete' and m['mode']=='full_netlist_shadow_three_payload_contracts'
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_stage_static_cp_shadow_system_v6.py')
    assert len(a['exact_comparisons'])==27 and a['host_edit']['host_writes']==1
    assert a['full_system_functional_netlist_validated'] and a['shadow_checks']>0 and a['parameters']['SLOTS']==32
    assert a['unconditional_outputs']==342 and a['qualified_outputs']==['cp_m_data','k_a_node','k_a_net','p_m_wdata'] and not a['all_pin_strict_equivalence']
    assert a['cp_export_words']==1560 and a['cp_export_frames']==10 and a['cp_protocol_counts']['transfers']==1560
    assert sha(p/'full/shadow_cp_export.log')==a['cp_transfer_log_sha256']
    assert a['authority_transfers']['requests']==26 and a['pager_write_transfers']['write_beats']==8223 and a['pager_write_transfers']['addresses']>0
    for name,digest in a['payload_log_sha256'].items():assert sha(p/'full'/name)==digest
    assert a['transfer_parser_sha256']==sha(ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py')
    assert a['production_sources']==133 and a['verification_sources']==3
    for obs in a['route_bank_observations'].values():assert all(value>0 for value in obs.values())
    r=read(receipt);index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
    prep=ROOT/'results/stage_static_cp_shadow_system_v6_tools_preparation_20261030.json'
    tools=read(prep)['tools']
    for source,digest in tools.items():assert sha(source)==digest
    out=ROOT/'results/stage_static_cp_shadow_system_v6_20261030.json'
    freeze=ROOT/'results/stage_static_cp_shadow_system_v6_sources_20261030'
    assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status='full_capacity_three_payload_protocol_shadow_actual_restored',audit=a,restoration=r,
        candidate_selected=False,timing_qualified=False,board_acceptance=False,
        full_system_functional_netlist_validated=True,all_pin_strict_equivalence=False,
        scope='One SLOTS32 host protocol shadow fixture:342 comparisons unchanged; CP/authority/pager-W payloads explicitly valid-qualified with stalls/pre-edge checking;1560 CP words,26 authority requests,8223 AXI write beats independently logged and compared and27 external files exact. Original behavioral monitors retained. Literal all-pin equivalence remains unproven and previous failure retained. Gate receives RTL-driven inputs, not independent memory agents. Arbitrary parameter/XZ/formal, physical timing and board proof remain separate.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();entries={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest)
        entries[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==entries[str(relative)]['sha256']
    for name,e in m['sources'].items():
        assert sha(p/'sources'/name)==e['sha256'];copy(p/'sources'/name,Path('sources')/name)
    for name,digest in m['shadow_inputs'].items():
        assert sha(p/'sources'/name)==digest;copy(p/'sources'/name,Path('shadow')/name)
    assert sha(p/'namespace.json')==m['namespace_sha256'];copy(p/'namespace.json',Path('shadow/namespace.json'))
    for name,e in m['bound'].items():
        assert sha(e['source'])==sha(p/'bound'/name)==e['sha256'];copy(p/'bound'/name,Path('bound')/name)
    copy(p/'full/shadow_cp_export.log',Path('reports/shadow_cp_export.log'))
    for name in a['payload_log_sha256']:copy(p/'full'/name,Path('reports')/name)
    for source in files+[out,prep]:copy(source,Path('reports')/(str(len(entries))+'_'+source.name))
    for source in tools:copy(Path(source),Path('tools')/(str(len(entries))+'_'+Path(source).name))
    for name in a['exact_comparisons']:
        assert sha(p/'full'/name)==a['exact_comparisons'][name]['sha256']
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,
        timing_qualified=False,full_system_functional_netlist_validated=True,all_pin_strict_equivalence=False),indent=2,sort_keys=True)+'\n')
    verify_freeze(freeze)
    print('FULL_HOST_NETLIST_SHADOW_ACTUAL_RESTORE_FROZEN',len(entries))


if __name__=='__main__':main()
