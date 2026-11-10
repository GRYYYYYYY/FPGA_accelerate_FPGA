"""Admit new full shadow only after both three-contract and logger calibrations."""
from shadow_recovered_evidence_v7 import ROOT,BASE,read,sha,restored,verify_freeze,identity
from stage_static_cp_shadow_predecessor_v7a import evidence as parent_evidence,REFERENCE,SYNTH
from prepare_stage_static_cp_shadow_protocol_v5 import render,QUALIFIED

TARGET=BASE/'stage_static_cp_shadow_system_v5'
VARIANT=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5'


def evidence():
    controls=ROOT/'results/shadow_payload_contract_controls_20261030.json'
    logger=ROOT/'results/shadow_payload_monitor_controls_20261030.json'
    assert controls.exists() and logger.exists(),'Wait for59 actual-restored observer controls and actual-restored three-stream logger controls'
    fm,proof=parent_evidence()
    cf=verify_freeze(ROOT/'results/shadow_payload_contract_controls_sources_20261030')
    _,ca,ce=restored(BASE/'shadow_payload_contract_controls_v1')
    assert read(controls)['status']=='three_payload_contract_controls59_actual_restored' and read(controls)['audit']==ca
    assert ca['complete_contract_controls_passed'] and ca['completed_expected_cases']==59 and len(ca['outcomes'])==59
    lf=verify_freeze(ROOT/'results/shadow_payload_monitor_controls_sources_20261030')
    _,la,le=restored(BASE/'shadow_payload_monitor_controls_v1')
    assert read(logger)['status']=='three_stream_logger_controls_actual_restored' and read(logger)['audit']==la and set(la['cases'])=={'matching','ready_nba'}
    vm=read(VARIANT/'manifest.json')
    for n,h in vm['files'].items():assert sha(VARIANT/n)==h
    assert vm['unconditional_outputs']==342 and vm['qualified_outputs']==QUALIFIED
    assert vm['cp_task_body_unchanged'] and vm['all342_comparison_blocks_exact'] and vm['clock_lead_ps']==1 and vm['input_transport_ns']==200
    parent=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4/shadow.sv'
    assert vm['parent_shadow_sha256']==sha(parent) and render(parent.read_text())==(VARIANT/'shadow.sv').read_text()
    assert ca['checker_sha256']==sha(VARIANT/'shadow.sv') and not ca['full_system_functional_netlist_validated']
    assert vm['source_tb_sha256']==sha(REFERENCE/'sources/tb_query_fault.sv')
    cp=ROOT/'hardware/tests/tb_shadow_cp_transfer_monitor_v1.sv';payload=ROOT/'hardware/tests/tb_shadow_payload_transfer_monitor_v1.sv'
    assert la['cp_monitor_sha256']==sha(cp) and la['payload_monitor_sha256']==sha(payload)
    proof.update({str(p):sha(p) for p in ce+le+[controls,logger,cf,lf,VARIANT/'manifest.json',VARIANT/'shadow.sv',VARIANT/'tb_query_fault.sv',parent,cp,payload,ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py',ROOT/'results/stage_static_cp_shadow_payload_contracts_20261030.json']})
    return fm,proof
