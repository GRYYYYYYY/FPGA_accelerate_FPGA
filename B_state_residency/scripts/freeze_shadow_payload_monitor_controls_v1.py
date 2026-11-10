"""Freeze only actually restored read-only logger calibrations."""
from pathlib import Path
import json,shutil
from host_edit_system_common_v1 import ROOT,BASE,read,sha,restored,verify_freeze


def main():
    p=BASE/'shadow_payload_monitor_controls_v1';m,a,files=restored(p)
    assert m['stage']=='complete' and set(a['cases'])=={'matching','ready_nba'}
    assert a['auditor_sha256']==sha(ROOT/'scripts/audit_shadow_payload_monitor_controls_v1.py')
    assert a['parser_sha256']==sha(ROOT/'scripts/check_shadow_payload_transfer_logs_v1.py')
    for values in a['cases'].values():assert values['authority']['requests']==values['pager_write']['write_beats']==values['cp_words']==5 and values['pager_write']['addresses']==1
    r=read(ROOT/'results/shadow_payload_monitor_controls_v1_restore_20261025.json');idx=read(r['archive_index']);assert sha(idx['archive'])==r['archive_sha256']
    prep=ROOT/'results/shadow_payload_monitor_tools_preparation_20261030.json'
    for f,h in read(prep)['tools'].items():assert sha(f)==h
    out=ROOT/'results/shadow_payload_monitor_controls_20261030.json';freeze=ROOT/'results/shadow_payload_monitor_controls_sources_20261030';assert not out.exists() and not freeze.exists()
    out.write_text(json.dumps(dict(status='three_stream_logger_controls_actual_restored',audit=a,restoration=r,full_system_functional_netlist_validated=False,scope='Two bounded fake-model read-only logger calibrations; parser14 synthetic negatives separately passed. No real FPGA netlist result.'),indent=2,sort_keys=True)+'\n')
    freeze.mkdir();entries={}
    def copy(source,relative):
        dest=freeze/relative;dest.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(source,dest);entries[str(relative)]=dict(source=str(source),sha256=sha(source));assert sha(dest)==entries[str(relative)]['sha256']
    for n in ['tb_shadow_cp_transfer_monitor_v1.sv','tb_shadow_payload_transfer_monitor_v1.sv']:copy(ROOT/'hardware/tests'/n,Path('monitor')/n)
    for n in ['run_shadow_payload_monitor_controls_v1.py','audit_shadow_payload_monitor_controls_v1.py','check_shadow_payload_transfer_logs_v1.py','freeze_shadow_payload_monitor_controls_v1.py','run_shadow_payload_contract_controls_v1.py']:copy(ROOT/'scripts'/n,Path('tools')/n)
    for source in files+[out,prep]:copy(source,Path('reports')/(str(len(entries))+'_'+source.name))
    (freeze/'manifest.json').write_text(json.dumps(dict(status='frozen',files=entries,full_system_functional_netlist_validated=False),indent=2,sort_keys=True)+'\n');verify_freeze(freeze);print('THREE_STREAM_LOGGER_CALIBRATIONS_FROZEN',len(entries))


if __name__=='__main__':main()
