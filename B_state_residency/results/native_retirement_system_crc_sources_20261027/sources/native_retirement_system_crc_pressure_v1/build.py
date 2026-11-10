"""Isolated candidate; default-off, start-latched native restore permission."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/B_state_residency_offer_20261025/fourth_warm_full_v2')
DEEP = ['priced/candidate_recursive_engine.sv',
        'priced/candidate_recursive_query_core.sv',
        'expansion_20261024/pager/pager/paged_exclusion_engine.sv']
MANAGER = 'expansion_20261024/pager/pager/resident_page_manager.sv'

def replace(s, old, new, count=1):
    assert s.count(old) == count, (old, s.count(old), count)
    return s.replace(old, new)

def make():
    manifest = json.loads((BASE/'manifest.json').read_text())
    def read(name):
        data = (BASE/'sources'/name).read_bytes()
        assert hashlib.sha256(data).hexdigest() == manifest['sources'][name]['sha256']
        return data.decode()
    out = {}
    for name in DEEP:
        s = replace(read(name), 'input wire baseline_raw_probe,',
                    'input wire baseline_restore_write,\ninput wire baseline_raw_probe,')
        s = replace(s, '.baseline_raw_probe(baseline_raw_probe),',
                    '.baseline_restore_write(baseline_restore_write),.baseline_raw_probe(baseline_raw_probe),')
        out[name] = s
    s = replace(read(MANAGER), 'input wire baseline_raw_probe,',
                'input wire baseline_restore_write,\ninput wire baseline_raw_probe,')
    s = replace(s, 'reg raw_probe;reg writing;', 'reg restore_write;reg raw_probe;reg writing;')
    s = replace(s, 'if(ENABLE_BASELINE&&!raw_probe)probe_access',
                'if(ENABLE_BASELINE&&!raw_probe&&!restore_write)probe_access', 2)
    s = replace(s, 'writing<=0;raw_probe<=0;', 'writing<=0;raw_probe<=0;restore_write<=0;', 2)
    s = replace(s, 'raw_probe<=ENABLE_BASELINE&&baseline_raw_probe;writing<=io_write;',
                'restore_write<=ENABLE_BASELINE&&(baseline_restore_write===1\'b1)&&io_write;\n'
                '                        raw_probe<=ENABLE_BASELINE&&baseline_raw_probe;writing<=io_write;')
    # An asserted restore qualifier never permits a read or raw-probe write.
    s = replace(s, 'else if(ENABLE_BASELINE&&baseline_raw_probe&&io_write)',
                'else if(ENABLE_BASELINE&&(baseline_restore_write===1\'b1)&&!io_write)begin io_status<=3;state<=IO_REPLY;end\n'
                '                        else if(ENABLE_BASELINE&&baseline_raw_probe&&io_write)')
    out[MANAGER] = s
    s = replace(read('label_restore_controller.sv'), 'output wire l_probe,',
                'input wire start_skip_seed,output wire l_import,\n output wire l_probe,')
    s = replace(s, 'reg[31:0]running_crc,expected_crc;', 'reg skip_seed;reg[31:0]running_crc,expected_crc;')
    s = replace(s, 'assign l_probe=',
                'assign l_import=!rst&&skip_seed&&(state==WS||state==WW);\n assign l_probe=')
    s = replace(s, 'if(rst)begin running_crc', 'if(rst)begin skip_seed<=0;running_crc')
    s = replace(s, 'IDLE:if(start_valid&&start_ready)begin',
                'IDLE:if(start_valid&&start_ready)begin\n     skip_seed<=(start_skip_seed===1\'b1);')
    out['label_restore_controller.sv'] = s
    for name in ['residency_system.sv', 'search_residency_system.sv', 'query_residency_system.sv']:
        s = replace(read(name), 'ENABLE_BASELINE=0,', 'ENABLE_BASELINE=0,ENABLE_RESTORE_SEED_BYPASS=0,')
        s = replace(s, 'input wire baseline_permit,', 'input wire restore_seed_enable,\ninput wire baseline_permit,')
        if name != 'residency_system.sv':
            s = replace(s, '.ENABLE_BASELINE(ENABLE_BASELINE),',
                        '.ENABLE_BASELINE(ENABLE_BASELINE),.ENABLE_RESTORE_SEED_BYPASS(ENABLE_RESTORE_SEED_BYPASS),')
            s = replace(s, '.baseline_permit(baseline_permit),',
                        '.restore_seed_enable(restore_seed_enable),.baseline_permit(baseline_permit),')
        else:
            s = replace(s, 'wire lr_busy;wire lr_l_probe;',
                        'wire lr_busy;wire lr_l_probe;wire lr_l_import;\n'
                        'wire baseline_restore_write=ENABLE_BASELINE&&f_recovery_owned&&k_labels_valid&&lr_l_import;')
            s = replace(s, '.baseline_raw_probe(baseline_raw_probe),',
                        '.baseline_restore_write(baseline_restore_write),.baseline_raw_probe(baseline_raw_probe),')
            s = replace(s, '))label_restore(.l_probe(lr_l_probe),',
                        '))label_restore(.start_skip_seed(ENABLE_RESTORE_SEED_BYPASS&&restore_seed_enable),'
                        '.l_import(lr_l_import),.l_probe(lr_l_probe),')
        out[name] = s
    return out

if __name__ == '__main__':
    for name, content in make().items():
        p = HERE/'sources'/name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content)
    print('generated', len(make()), 'candidate sources')
