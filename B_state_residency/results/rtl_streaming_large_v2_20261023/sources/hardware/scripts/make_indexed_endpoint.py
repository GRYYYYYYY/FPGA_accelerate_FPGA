"""Mechanically propagate the frozen directory variant through the wide endpoint."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def transform(text, replacements):
    for before, after, count in replacements:
        if text.count(before) != count:
            raise ValueError('Ambiguous substitution: ' + before[:80])
        text = text.replace(before, after)
    return text


def outputs(root=ROOT):
    result = {}
    for src, dest, child, new_child in [
        ('backing_page_service_lookup', 'backing_page_service_indexed', 'backing_frame_directory_lookup', 'backing_frame_directory_indexed'),
        ('record_backing_service_wide', 'record_backing_service_indexed', 'backing_page_service_lookup', 'backing_page_service_indexed'),
        ('memory_scratch_endpoint_wide', 'memory_scratch_endpoint_indexed', 'record_backing_service_wide', 'record_backing_service_indexed')]:
        text = (root / f'hardware/rtl/{src}.sv').read_text()
        result[f'hardware/rtl/{dest}.sv'] = transform(text, [
            (f'module {src} #(', f'module {dest} #(', 1),
            ('parameter integer FRAMES=23405,INDEX_BITS=15', 'parameter integer FRAMES=23405,INDEX_BITS=15,HASH_BITS=15,PROBE_LIMIT=64,EPOCH_BITS=8', 1),
            (f'{child} #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS))',
             f'{new_child} #(.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.PROBE_LIMIT(PROBE_LIMIT),.EPOCH_BITS(EPOCH_BITS))', 1)])
    text = (root / 'hardware/tb/tb_memory_endpoint_wide.sv').read_text()
    text = transform(text, [
        ('memory_endpoint_wide_test', 'memory_endpoint_indexed_test', 3),
        ('tb_memory_endpoint_wide_', 'tb_memory_endpoint_indexed_', 2),
        ('memory_scratch_endpoint_wide #(', 'memory_scratch_endpoint_indexed #(', 1),
        ('.INDEX_BITS(TB_INDEX)) dut(.*);', '.INDEX_BITS(TB_INDEX),.HASH_BITS(SMALL?2:15),.PROBE_LIMIT(SMALL?1:64),.EPOCH_BITS(SMALL?2:8)) dut(.*);', 1),
        # The added architecture has a declared full-index scrub. Extend only
        # the watchdog by precisely its maximum duration; retain all oracles.
        ('if(t>30000)$fatal(1,"host response timeout', 'if(t>30000+(1<<(SMALL?2:15)))$fatal(1,"host response timeout', 1)])
    monitor = '''
    // Added index-lifecycle observer: never drives the DUT or changes stimulus.
    integer index_clear_cycles=0,index_wraps=0,index_overflows=0;
    reg [3:0] previous_directory_state=0;
    always @(posedge clk)begin
        if(rst)previous_directory_state<=0;
        else begin
            if(dut.memory.memory_service.directory.state==14)begin
                index_clear_cycles=index_clear_cycles+1;
                if(dut.memory.memory_service.directory.cmd_ready || dut.memory.memory_service.directory.rsp_valid)
                    $fatal(1,"index scrub exposed incomplete directory");
                if(dut.memory.memory_service.directory.clear_response)begin
                    if(previous_directory_state!=14)index_wraps=index_wraps+1;
                    if(!dut.fence_open || cmd_ready)$fatal(1,"index wrap escaped endpoint fence");
                end
            end
            if(dut.memory.memory_service.directory.state==3 && !dut.memory.memory_service.directory.insertion_slot)
                index_overflows=index_overflows+1;
            previous_directory_state<=dut.memory.memory_service.directory.state;
        end
    end
'''
    text = transform(text, [('    task automatic cold_start;', monitor + '\n    task automatic cold_start;', 1),
                           ('        $display("TEST_PASS memory_endpoint ', '''        if(SMALL && (index_wraps<2 || index_overflows==0))$fatal(1,"index endpoint boundary coverage incomplete");
        if(!SMALL && index_clear_cycles!=32768)$fatal(1,"default index initialization not accounted");
        $display("INDEX_ENDPOINT_PASS clear_cycles=%0d wraps=%0d overflows=%0d",index_clear_cycles,index_wraps,index_overflows);
        $display("TEST_PASS memory_endpoint ''', 1)])
    result['hardware/tb/tb_memory_endpoint_indexed.sv'] = text
    text = (root / 'hardware/tb/tb_memory_endpoint_wide_profile.sv').read_text()
    result['hardware/tb/tb_memory_endpoint_indexed_profile.sv'] = transform(text, [
        ('tb_memory_endpoint_wide_profile', 'tb_memory_endpoint_indexed_profile', 1),
        ('memory_endpoint_wide_test', 'memory_endpoint_indexed_test', 1),
        ('directory_cycles[0:6]', 'directory_cycles[0:14]', 1),
        ('i<7;i=i+1)', 'i<15;i=i+1)', 2),
        ('directory.state>6', 'directory.state>14', 1)])
    return result


if __name__ == '__main__':
    for name, text in outputs().items():
        path = ROOT / name
        if path.exists():
            raise FileExistsError(path)
        path.write_text(text)
