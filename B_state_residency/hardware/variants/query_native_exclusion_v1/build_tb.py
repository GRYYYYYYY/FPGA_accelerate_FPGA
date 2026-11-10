"""Reuse lifecycle tests and inject three external same-cycle replies, never force DUT."""
from pathlib import Path

def build(root, mode, early):
    assert mode in ('baseline','default','exclusive') and early in range(4)
    s=(root/'hardware/variants/query_lifecycle_v1/tb_query_lifecycle.sv').read_text()
    marker=' query_lifecycle #(.MAX_CYCLES(300))dut(.*);'
    assert s.count(marker)==1
    extra=',.EXCLUSIVE_BACKEND_RESPONSES(1)' if mode=='exclusive' else ''
    ties=""".cp_rebase(1'b0),.cp_rebase_permit(1'b0),.cp_source_version(32'd0),.cp_source_query(2'd0),.cp_source_price(4'd0),
 .active_generation(64'd1),.cp_valid(1'b0),.cp_restore(1'b0),.cp_safe(1'b0),.cp_ready(),.cp_busy(),
 .cp_expected_crc(32'd0),.cp_rsp_valid(),.cp_rsp_ready(1'b0),.cp_status(),.cp_crc(),
 .cp_s_valid(1'b0),.cp_s_ready(),.cp_s_index(32'd0),.cp_s_data(32'd0),.cp_s_last(1'b0),
 .cp_m_valid(),.cp_m_ready(1'b0),.cp_m_index(),.cp_m_data(),.cp_m_last(),"""
    monitor=f"""
 localparam EARLY={early};
 reg injected=0;integer injected_count=0,observed_cycles=0;
 wire early_service=!rst&&!injected&&EARLY==1&&service_valid&&service_ready;
 wire early_search=!rst&&!injected&&EARLY==2&&search_valid&&search_ready;
 wire early_route=!rst&&!injected&&EARLY==3&&route_valid&&route_ready;
 always @(posedge clk)begin
  if(!rst)begin
   observed_cycles<=observed_cycles+1;
   if(EARLY==0&&((service_ready&&service_rsp_valid)!==1'b0||(search_ready&&search_rsp_valid)!==1'b0||(route_ready&&route_rsp_valid)!==1'b0))$fatal(1,"native pair overlap or unknown");
   if(early_service||early_search||early_route)begin
    injected<=1;injected_count<=injected_count+1;
    $fdisplay(events,"EARLY %0d %0d",EARLY,cycles);
   end
  end
 end
 query_lifecycle #(.MAX_CYCLES(300){extra})dut({ties}
 .service_rsp_valid(service_rsp_valid||early_service),
 .search_rsp_valid(search_rsp_valid||early_search),
 .route_rsp_valid(route_rsp_valid||early_route),.*);
"""
    # All declarations referenced by the monitor precede the module instance.
    s=s.replace(marker,'')
    anchor=' assign service_ready='
    assert s.count(anchor)==1
    s=s.replace(anchor,monitor+'\n'+anchor)
    if early:
        start=s.index('  reset_case;launch(0);finish(0,1);')
        end=s.index('  $fclose(events);',start)
        status=7 if mode=='exclusive' else 0
        committed=1 if mode!='exclusive' or early==3 else 0
        s=s[:start]+f'  reset_case;launch(0);finish({status},{committed});\n  if(injected_count!=1)$fatal(1,"missing unique overlap injection");\n'+s[end:]
    s=s.replace('$fclose(events);$display(', '$fdisplay(events,"MONITOR %0d %0d",observed_cycles,injected_count);$fclose(events);$display(')
    return s
