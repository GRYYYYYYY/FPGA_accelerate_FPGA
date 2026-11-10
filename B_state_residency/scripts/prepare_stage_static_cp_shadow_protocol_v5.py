"""Prepare three explicit payload contracts while retaining342 unconditional checks."""
import json
from host_edit_system_common_v1 import ROOT,read,sha,verify_freeze

GROUPS={
 'ka':dict(tag='KA',valid='k_a_valid',ready='expected_k_a_ready',actual_ready='actual_k_a_ready',payloads=['k_a_node','k_a_net'],metadata=['k_a_cookie','k_a_checkpoint','k_a_design']),
 'pw':dict(tag='PW',valid='p_m_wvalid',ready='drive_p_m_wready',actual_ready=None,payloads=['p_m_wdata'],metadata=['p_m_wstrb','p_m_wlast'])}
QUALIFIED=['cp_m_data','k_a_node','k_a_net','p_m_wdata']


def group_task(key,g):
    tag=g['tag'];v=g['valid'];ready=g['ready'];payload=g['payloads'];meta=g['metadata']
    unknown=lambda ns:'||'.join(f'(^expected_{n})===1\'bx||(^actual_{n})===1\'bx' for n in ns)
    mismatch=lambda ns:'||'.join(f'actual_{n}!==expected_{n}' for n in ns)
    s=f'''task check_{key}_output;
input integer at_edge;
begin
 if((expected_{v}!==1'b0&&expected_{v}!==1'b1)||(actual_{v}!==1'b0&&actual_{v}!==1'b1))
  $fatal(1,"{tag}_VALID_UNKNOWN phase=%0d time=%0t",at_edge,$time);
 if(actual_{v}!==expected_{v})$fatal(1,"{tag}_VALID_MISMATCH phase=%0d time=%0t",at_edge,$time);
 if(expected_{v}===1'b1)begin
  {key}_active_checks={key}_active_checks+1;
  if(at_edge!=0){key}_edge_checks={key}_edge_checks+1;
'''
    if g['actual_ready']:
        ar=g['actual_ready'];s+=f'''  if(({ar}!==1'b0&&{ar}!==1'b1)||{ar}!=={ready})$fatal(1,"{tag}_READY_UNKNOWN_OR_MISMATCH phase=%0d time=%0t",at_edge,$time);
'''
    s+=f'''  if({ready}===1'b0){key}_stall_checks={key}_stall_checks+1;
  else if({ready}===1'b1)begin
   if(at_edge!=0){key}_transfer_checks={key}_transfer_checks+1;
  end else $fatal(1,"{tag}_READY_UNKNOWN phase=%0d time=%0t",at_edge,$time);
  if({unknown(payload)})$fatal(1,"{tag}_DATA_UNKNOWN phase=%0d time=%0t",at_edge,$time);
  if({mismatch(payload)})$fatal(1,"{tag}_DATA_MISMATCH phase=%0d ready=%b time=%0t",at_edge,{ready},$time);
  if({unknown(meta)})$fatal(1,"{tag}_META_UNKNOWN phase=%0d time=%0t",at_edge,$time);
  if({mismatch(meta)})$fatal(1,"{tag}_META_MISMATCH phase=%0d time=%0t",at_edge,$time);
 end else begin
  {key}_idle_observations={key}_idle_observations+1;
  if({mismatch(payload)}){key}_idle_differences={key}_idle_differences+1;
 end
end endtask
'''
    return s


def render(parent):
    patches=[]
    declarations='\n'.join(f'integer {k}_active_checks=0,{k}_stall_checks=0,{k}_transfer_checks=0,{k}_edge_checks=0,{k}_idle_observations=0,{k}_idle_differences=0;' for k in GROUPS)
    patches += [('integer checks=0,reset_edges=0;','integer checks=0,reset_edges=0;\n'+declarations)]
    patches += [('task check_cp_output;',''.join(group_task(k,g) for k,g in GROUPS.items())+'task check_cp_output;')]
    patches += [('always @(posedge drive_clk)if(armed)check_cp_output(1);','always @(posedge drive_clk)if(armed)begin check_cp_output(1);check_ka_output(1);check_pw_output(1);end')]
    patches += [('  check_cp_output(0);','  check_cp_output(0);check_ka_output(0);check_pw_output(0);')]
    for n in QUALIFIED[1:]:
        old=f'  if(actual_{n}!==expected_{n})\n   $fatal(1,"FULL_SHADOW_MISMATCH port={n} time=%0t actual=%h expected=%h",$time,actual_{n},expected_{n});'
        patches.append((old,f'  // {n} checked by its explicit valid/ready contract task.'))
    coverage=''
    for k,g in GROUPS.items():
        tag=g['tag'];coverage+=f''' if({k}_active_checks==0||{k}_stall_checks==0||{k}_transfer_checks==0||{k}_edge_checks==0||{k}_idle_observations==0)
  $fatal(1,"{tag}_PROTOCOL_COVERAGE_MISSING active=%0d stalled=%0d transfers=%0d edges=%0d idle=%0d",{k}_active_checks,{k}_stall_checks,{k}_transfer_checks,{k}_edge_checks,{k}_idle_observations);
'''
    for k,g in GROUPS.items():
        coverage+=f' $display("PAYLOAD_GROUP_PASS group={g["tag"]} active=%0d stalled=%0d transfers=%0d edges=%0d idle=%0d idle_differences=%0d",{k}_active_checks,{k}_stall_checks,{k}_transfer_checks,{k}_edge_checks,{k}_idle_observations,{k}_idle_differences);\n'
    old=' $display("FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=345 qualified=cp_m_data'
    new=coverage+' $display("FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata'
    patches.append((old,new))
    s=parent
    for a,b in patches:assert s.count(a)==1;s=s.replace(a,b,1)
    inverse=s
    for a,b in reversed(patches):assert inverse.count(b)==1;inverse=inverse.replace(b,a,1)
    assert inverse==parent
    ports=read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports']
    kept=0
    for p in ports:
        if p['direction']!='output' or p['name'] in QUALIFIED:continue
        n=p['name'];block=f'  if(actual_{n}!==expected_{n})\n   $fatal(1,"FULL_SHADOW_MISMATCH port={n} time=%0t actual=%h expected=%h",$time,actual_{n},expected_{n});'
        assert parent.count(block)==s.count(block)==1,n;kept+=1
    assert kept==342
    cp=parent.split('task check_cp_output;',1)[1].split('end endtask',1)[0]
    assert s.split('task check_cp_output;',1)[1].split('end endtask',1)[0]==cp
    return s


def main():
    analysis=ROOT/'results/stage_static_cp_shadow_payload_contracts_20261030.json'
    a=read(analysis);assert a['status']=='source_bound_payload_contract_analysis_only'
    af=verify_freeze(ROOT/'results/stage_static_cp_shadow_payload_contracts_sources_20261030')
    ff=verify_freeze(ROOT/'results/stage_static_cp_shadow_v4_failure_sources_20261030')
    for p,h in a['source_sha256'].items():assert sha(p)==h
    parent=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4';m=read(parent/'manifest.json')
    for n,h in m['files'].items():assert sha(parent/n)==h
    out=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5';assert not out.exists();out.mkdir()
    (out/'shadow.sv').write_text(render((parent/'shadow.sv').read_text()))
    (out/'tb_query_fault.sv').write_text((parent/'tb_query_fault.sv').read_text())
    record=dict(status='three_payload_contract_observer_prepared_not_simulated',files={n:sha(out/n) for n in ['shadow.sv','tb_query_fault.sv']},generator_sha256=sha(__file__),parent_shadow_sha256=sha(parent/'shadow.sv'),contract_analysis_sha256=sha(analysis),predecessor_freeze_sha256={str(p):sha(p) for p in [af,ff]},unconditional_outputs=342,qualified_outputs=QUALIFIED,groups=GROUPS,cp_task_body_unchanged=True,all342_comparison_blocks_exact=True,input_transport_ns=200,clock_lead_ps=1,source_tb_sha256=m['source_tb_sha256'],all_pin_strict_equivalence=False,full_system_functional_netlist_validated=False,scope='Three source-bound payload contracts; controls strict/known even idle, valid payload including stalls/pre-edge strict/known. No DUT change. Not yet simulated or full-system validated.')
    (out/'manifest.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    receipt=ROOT/'results/stage_static_cp_shadow_protocol_v5_preparation_20261030.json';assert not receipt.exists();receipt.write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('THREE_PAYLOAD_OBSERVER_PREPARED_342_BLOCKS_EXACT_CP_TASK_UNCHANGED')


if __name__=='__main__':main()
