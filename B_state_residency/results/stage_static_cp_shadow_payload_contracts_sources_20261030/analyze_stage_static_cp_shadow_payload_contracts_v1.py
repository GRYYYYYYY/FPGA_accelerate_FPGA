"""Bind concrete payload/consumer contracts; no checker generation or DUT edits."""
from pathlib import Path
import itertools,json,re
from host_edit_system_common_v1 import ROOT,BASE,read,sha,verify_freeze


def main():
    failure=ROOT/'results/stage_static_cp_shadow_v4_failure_20261030.json'
    assert failure.exists(),'Wait for failed v4 and read-only inventory actual restore/freeze'
    ff=verify_freeze(ROOT/'results/stage_static_cp_shadow_v4_failure_sources_20261030')
    f=read(failure);assert f['shadow_verdict']=='failed'
    assert set(f['sampled_differing_outputs'])=={'cp_m_data','k_a_net','k_a_node','p_m_wdata'}
    root=BASE/'stage_static_cp_shadow_system_v4';m=read(root/'manifest.json');src=root/'sources'
    names=['query_residency_system.sv','recovery_coordinator.sv','checkpoint_authority_rotator.sv','checkpoint_authority_reader.sv','expansion_20261024/pager/backend/scratch_page_axi_small.sv','expansion_20261024/pager/backend/backing_page_service_small.sv','axi_file_memory.sv','tb_query_fault.sv']
    bound={};text={}
    for name in names:
        p=src/name;assert sha(p)==m['sources'][name]['sha256'];bound[str(p)]=sha(p);text[name]=p.read_text()
    q=text['query_residency_system.sv'];r=text['recovery_coordinator.sv'];reader=text['checkpoint_authority_reader.sv'];dma=text[names[4]];memory=text['axi_file_memory.sv']
    for token in ['.req_valid(!ap_owned&&(k_a_valid||ap_offer))','.req_node(ap_offer?ap_node:k_a_node)','.req_net(ap_offer?ap_net:k_a_net)']:
        assert token in q
    assert 'assign a_valid=!cold_rst&&state==AS;' in r
    assert 'assign a_node=nodes[index];assign a_net=nets[index];' in r
    assert 'else if(req_valid&&req_ready)begin' in reader
    assert 'held_node<=req_node;held_net<=req_net;' in reader
    # For every Boolean mux/ownership/ready combination, consuming selected K
    # fields implies K_VALID. No assumed exclusion relation is needed here.
    table=[]
    for owned,offer,valid,ready in itertools.product([0,1],repeat=4):
        req_valid=not owned and (valid or offer)
        k_consumed=bool(req_valid and ready and not offer)
        assert not k_consumed or valid
        table.append(dict(ap_owned=owned,ap_offer=offer,k_a_valid=valid,ready=ready,k_payload_consumed=k_consumed))
    assert sum(row['k_payload_consumed'] for row in table)==1
    assert 'assign m_wdata=buffer_data;' in dma
    assert 'assign m_wvalid=!rst && state==WRITE_DATA && buffer_valid;' in dma
    assert 'if(in_valid && in_ready)begin buffer_valid<=1;buffer_data<=in_data;end' in dma
    assert 'if(wvalid&&wready)begin' in memory and 'wqueue[wrcount]<=wdata;' in memory
    ref=BASE/'stage_static_cp_host_full_static_v1'
    accepted=ROOT/'results/stage_static_cp_host_full_static_20261030.json'
    assert read(accepted)['status']=='full_capacity_host_static_actual_restored'
    ra=read(ref/'source_bound_audit.json')
    gold={}
    for name in ['natural_trace.txt','label_axi.txt']:
        p=ref/'full'/name;assert sha(p)==ra['outputs'][name]['sha256'];gold[name]=p.read_text();bound[str(p)]=sha(p)
    ka=re.findall(r'^KA (\d+) (\d+) (\d+) (\d+) (\d+)$',gold['natural_trace.txt'],re.M)
    writes=re.findall(r'^W ([0-9a-fA-F]+) ([0-9a-fA-F]{16}) ([0-9a-fA-F]{128})$',gold['label_axi.txt'],re.M)
    assert len(ka)==26 and len(writes)==8223
    out=ROOT/'results/stage_static_cp_shadow_payload_contracts_20261030.json';assert not out.exists()
    result=dict(status='source_bound_payload_contract_analysis_only',analyzer_sha256=sha(__file__),source_sha256=bound,
        failed_shadow_report_sha256=sha(failure),failed_shadow_freeze_sha256=sha(ff),authority_mux_boolean_cases=table,
        proposed_groups=[dict(payloads=['cp_m_data'],valid='cp_m_valid',ready='cp_m_ready',prior_controls='17 actual-restored CP controls'),dict(payloads=['k_a_node','k_a_net'],valid='k_a_valid',ready='k_a_ready',consumer='authority mux and reader capture only under request valid/ready'),dict(payloads=['p_m_wdata'],valid='p_m_wvalid',ready='p_m_wready',consumer='AXI file memory write queue only under WVALID/WREADY')],
        sampled_unconditional_output_count=342,qualification_not_applied=True,
        accepted_reference_transfers=dict(cp_export_words=1560,authority_requests=len(ka),label_write_beats=len(writes)),
        required_observer_controls=['Each group valid must be known and equal even idle','Payload must be known/equal whenever valid1 including backpressure','Check pre-clock acceptance and post-edge states','Inject active/stalled/pre-edge payload errors and X/Z','Inject unknown/mismatched valid and nonqualified control errors','Independent gate transfer logs must match gold26 authority requests,8223 AXI write beats and1560 CP words','Do not infer stability or equality of idle payloads, or ignore other342 outputs','Keep failed v3/v4 unchanged; new control suite and new full experiment required'],
        full_system_functional_netlist_validated=False,timing_qualified=False,
        scope='Source and16-case Boolean mux analysis only, not RTL/formal proof or a new observer/full simulation result. Sampled four differences are not proof no later differences exist. No source/checker changed, no new job.')
    out.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('PAYLOAD_CONTRACT_ANALYSIS_BOUND',len(table),'KA',len(ka),'AXI_W',len(writes))


if __name__=='__main__':main()
