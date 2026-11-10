"""Freeze actual-restored59 observer controls; never accept real DUT behavior."""
from pathlib import Path
import json,shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,verify_freeze


def main():
    p=BASE/'shadow_payload_contract_controls_v1';m,a,files=restored(p)
    assert m['stage']=='complete' and a['complete_contract_controls_passed'] and a['completed_expected_cases']==59
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_shadow_payload_contract_controls_v1.py')
    assert a['unconditional_outputs']==342 and a['valid_qualified_outputs']==['cp_m_data','k_a_node','k_a_net','p_m_wdata']
    assert not a['full_system_functional_netlist_validated'] and not a['all_pin_strict_equivalence']
    receipt=ROOT/'results/shadow_payload_contract_controls_v1_restore_20261025.json';r=read(receipt);index=read(r['archive_index']);assert sha(index['archive'])==r['archive_sha256']
    prep=ROOT/'results/shadow_payload_contract_controls_v1_preparation_20261030.json'
    for source,h in read(prep)['tools'].items():assert sha(source)==h
    out=ROOT/'results/shadow_payload_contract_controls_20261030.json';freeze=ROOT/'results/shadow_payload_contract_controls_sources_20261030';assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status='three_payload_contract_controls59_actual_restored',audit=a,restoration=r,all_pin_strict_equivalence=False,full_system_functional_netlist_validated=False,scope='59 bounded fake-model observer controls only; actual full-system netlist and physical timing remain unvalidated.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();entries={}
    def copy(source,relative):
        target=freeze/relative;target.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,target);entries[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(target)==entries[str(relative)]['sha256']
    v=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v5'
    for name in ['shadow.sv','tb_query_fault.sv','manifest.json']:copy(v/name,Path('variant')/name)
    copy(p/'matching/control.sv',Path('controls/control.sv'))
    for name in ['prepare_stage_static_cp_shadow_protocol_v5.py','run_shadow_payload_contract_controls_v1.py','audit_shadow_payload_contract_controls_v1.py','freeze_shadow_payload_contract_controls_v1.py','continue_shadow_payload_contract_controls_v1.py','continue_shadow_payload_contract_controls_v2.py','run_shadow_cp_protocol_controls_v5.py','audit_shadow_cp_protocol_controls_v3.py','host_edit_system_common_v1.py','config_native_publication_synth_common_v1.py','archive_offer_result.py','restore_offer_result.py','verify_search_retire_restore.py']:
        copy(ROOT/'scripts'/name,Path('tools')/name)
    for source in files+[out,prep,ROOT/'results/stage_static_cp_shadow_payload_contracts_20261030.json']:
        copy(source,Path('reports')/(str(len(entries))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,full_system_functional_netlist_validated=False,all_pin_strict_equivalence=False),indent=2,sort_keys=True)+'\n')
    verify_freeze(freeze);print('THREE_PAYLOAD_CONTROLS59_ACTUAL_RESTORE_FROZEN',len(entries))


if __name__=='__main__':main()
