"""Audit the narrow RTL port probe; do not claim netlist/full-system proof."""
from pathlib import Path
import json
import re
import sys
import zlib
from host_edit_system_common_v1 import ROOT, BASE, read, sha, identity


def main():
    p=Path(sys.argv[1]).resolve(); assert p==BASE/'stage_export_static_cp_rtl_v1'
    m=read(p/'manifest.json')
    assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
    assert identity(m['runner_pid'])!=str(m['runner_start_ticks']) and not m.get('active_process')
    assert [x['stage'] for x in m['commands']]==['compile','elaborate','simulate']
    assert all(x['exit_code']==0 for x in m['commands'])
    for n,h in m['sources'].items():assert sha(p/n)==h
    assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_export_static_cp_rtl_v1.py')
    source=ROOT/'hardware/variants/stage_static_cp_v1/fixed.sv'
    assert sha(source)==sha(p/'controller.sv')
    original=(ROOT/'hardware/tests/tb_stage_export_after_reset_v3.sv').read_text()
    current=(p/'tb.sv').read_text()
    assert current==original.replace('route_commit_controller #(.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);',
        'route_commit_controller #(.STATIC_STAGE_WRITES(1),.MAX_PATH(8),.MAX_CYCLES(256))dut(.*);',1)
    assert sha(p/'tb.sv')==sha(ROOT/'hardware/tests/tb_stage_export_static_cp_v1.sv')
    assert not re.search(r'\bforce\b|dut\.',current)
    log=(p/'simulate.stdout.log').read_text()
    assert len(re.findall(r'^PROBE_IMPORT_PASS words=30 slots=01$',log,re.M))==1
    hits=re.findall(r'^STAGE_EXPORT_AFTER_RESET_PASS imports=30 exports=30 crc=([0-9a-fA-F]{8})$',log,re.M)
    assert len(hits)==1 and int(hits[0],16)==zlib.crc32(bytes(30*4))
    assert not re.search(r'Fatal:|^ERROR:',log,re.M)
    artifacts={n:sha(p/n) for n in ['controller.sv','tb.sv','run.tcl','compile.stdout.log','elaborate.stdout.log','simulate.stdout.log']}
    result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
        runner_sha256=m['runner_sha256'],reference_rtl_sha256=sha(source),artifact_sha256=artifacts,
        import_words=30,imported_slots='01',reset_then_export_words=30,
        exported_zero_image_crc32=f'{zlib.crc32(bytes(120)):08x}',timing_qualified=False,
        scope='Isolated CP static-stage enabled RTL,2 slots/MAX_PATH8: one nonzero valid import then reset then zero export with input VALID zero, ordering/backpressure/CRC checked by port-only TB. Not post-synthesis, full system or arbitrary-state equivalence.')
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print('STAGE_EXPORT_RESET_RTL_AUDITED',result['exported_zero_image_crc32'])


if __name__=='__main__':main()
