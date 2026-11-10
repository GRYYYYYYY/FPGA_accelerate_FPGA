from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'iter2_g2_v1/build_tb.py'
def make():
 s=runpy.run_path(str(BASE))['make']()
 s=s.replace('.ENABLE_WARM_RECOVERY(1))system(','.ENABLE_WARM_RECOVERY(1),.RESTORE_RECORDS(1024))system(')
 s=s.replace(".wm_source_version(32'd4),.wm_source_query(2'd2),.wm_source_price(4'd4)",".wm_source_version(32'd3),.wm_source_query(2'd1),.wm_source_price(4'd3)")
 s=s.replace(".snapshot_count(32'd328)",".snapshot_count(32'd822)").replace(".snapshot_probe(32'd150697)",".snapshot_probe(32'd204279)")
 marker=' query_index=1;selected_sink=67922;selected_connection=170996;selected_sequence=180328;stopped=0;\n autonomous_query;'
 assert s.count(marker)==1
 s=s.replace(marker,''' query_index=1;selected_sink=67922;selected_connection=170996;selected_sequence=180328;stopped=0;
 replayed=0;armed=1;injection_seen=0;fault_case=5;wm_enable=1;warm_fault_node=558358;warm_running=1;
 fault_query;
 iter2_g2_warm_restore;
 autonomous_query;''')
 s=s.replace('system.controller.last_sequence!=180328||system.controller.last_version!=3||p_active_query!=1||p_active_price!=3','system.controller.last_sequence!=180328||system.controller.last_version!=4||p_active_query!=2||p_active_price!=4')
 warm=(HERE.parent/'iter2_warm_v1/tb_warm.sv').read_text()
 extra=warm[warm.index('task iter2_warm_restore;'):warm.index('\nend endtask',warm.index('task iter2_warm_restore;'))+12]
 extra=extra.replace('task iter2_warm_restore;','task iter2_g2_warm_restore;')
 extra=extra.replace("as_bound_generation!=64'h100000001","as_bound_generation!=64'h100000002")
 extra=extra.replace('rc=$fseek(imports_fd,0,0);if(rc)$fatal(1,"iter2 label rewind");', '''if(!$value$plusargs("warmimports=%s",warm_path))$fatal(1,"warm source labels");warm_fd=$fopen(warm_path,"r");if(!warm_fd)$fatal(1,"warm source open");''')
 extra=extra.replace('$fscanf(imports_fd,','$fscanf(warm_fd,')
 extra=extra.replace('p_active_price!=4||rc_slots)', 'p_active_price!=4||rc_slots!=1||system.controller.last_sequence!=180327)')
 extra=extra.replace('offers=0;count1=0;count2=0;', 'offers=0;count2=0;')
 extra=extra.replace('replayed=1;','replayed=1;warm_running=0;retry_started=1;')
 s=s.replace('\nendmodule',extra+'\nendmodule')
 return s
if __name__=='__main__':HERE.joinpath('tb_g2_warm.sv').write_text(make())
