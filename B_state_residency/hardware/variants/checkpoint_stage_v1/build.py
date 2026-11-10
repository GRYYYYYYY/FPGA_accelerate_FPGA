from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources')
def rep(s,a,b):
 assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def make():
 out={}
 s=(BASE/'recovery_coordinator.sv').read_text();idx=s.index(' input wire clk')
 extra=''' input wire cfg_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,staged_valid,
 output wire[63:0]staged_design,output wire[31:0]staged_checkpoint,staged_version,active_version,
 output wire[1:0]staged_query,active_query,output wire[3:0]staged_price,active_price,
''';s=s[:idx]+extra+s[idx:]
 idx=s.index(' always @* begin duplicate')
 decl=''' reg prepared;reg[63:0]shadow_design;reg[31:0]shadow_checkpoint,shadow_version;reg[1:0]shadow_query;reg[3:0]shadow_price;
 assign staged_valid=!cold_rst&&!abort&&prepared&&!cfg_rsp_valid&&state==NORMAL&&!fault;
 assign staged_design=staged_valid?shadow_design:64'd0;
 assign staged_checkpoint=staged_valid?shadow_checkpoint:32'd0;
 assign staged_version=staged_valid?shadow_version:32'd0;
 assign staged_query=staged_valid?shadow_query:2'd0;
 assign staged_price=staged_valid?shadow_price:4'd0;
 assign active_version=current_version;assign active_query=current_query;assign active_price=current_price;
 assign publish_ready=staged_valid&&publish_permit&&!cfg_valid&&!recover_valid&&!j_valid&&!discard_valid&&backend_drained&&normal_retired;
 assign discard_ready=staged_valid&&publish_permit&&!cfg_valid&&!recover_valid&&!j_valid&&!publish_valid&&backend_drained&&normal_retired;
''';s=s[:idx]+decl+s[idx:]
 # Quarantine mutable/recovery activity while a shadow snapshot is pending.
 s=rep(s,'assign permit_work=!cold_rst&&configured', 'assign permit_work=!cold_rst&&!prepared&&configured')
 s=rep(s,'assign j_ready=!cold_rst&&configured','assign j_ready=!cold_rst&&!prepared&&configured')
 s=rep(s,'assign recover_ready=!cold_rst&&configured','assign recover_ready=!cold_rst&&!prepared&&configured')
 s=rep(s,'attempt_version<=0;attempt_query<=0;', 'prepared<=0;shadow_design<=0;shadow_checkpoint<=0;shadow_version<=0;shadow_query<=0;shadow_price<=0;attempt_version<=0;attempt_query<=0;')
 needle="if(!cfg_authoritative||cfg_price!=cfg_version[3:0]||(configured&&((cfg_design==saved_design&&(cfg_checkpoint<=saved_checkpoint||cfg_version<current_version))||(cfg_design!=saved_design&&journal_count!=0))))cfg_status<=1;"
 repl='''if(prepared||(!cfg_stage&&configured))cfg_status<=1;
      else if(cfg_stage)begin
       if(!publish_permit||!configured||!cfg_authoritative||cfg_design==0||cfg_design!=saved_design||cfg_checkpoint<=saved_checkpoint||cfg_version==0||cfg_version!=current_version||cfg_version<attempt_version||cfg_query!=current_query||cfg_price!=current_price||cfg_price!=cfg_version[3:0])cfg_status<=1;
       else begin prepared<=1;shadow_design<=cfg_design;shadow_checkpoint<=cfg_checkpoint;shadow_version<=cfg_version;shadow_query<=cfg_query;shadow_price<=cfg_price;end
      end
      else '''+needle
 s=rep(s,needle,repl)
 tail='''   endcase
   if(publish_valid&&publish_ready)begin
    saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_version;current_query<=shadow_query;current_price<=shadow_price;journal_count<=0;prepared<=0;
    // A new checkpoint does not reset the recovery-attempt floor.
   end
   if((discard_valid&&discard_ready)||abort||fail_now)prepared<=0;
'''
 s=rep(s,'   endcase\n',tail);out['recovery_coordinator.sv']=s
 s=(BASE/'config_restore_controller.sv').read_text();idx=s.index(' input wire clk')
 extra=''' input wire load_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,staged_valid,
 output wire[63:0]staged_design,output wire[31:0]staged_checkpoint,staged_version,active_version,
 output wire[2303:0]staged_payload,active_payload,
''';s=s[:idx]+extra+s[idx:]
 idx=s.index(' wire fail_now=')
 decl=''' reg prepared;reg[2303:0]shadow_payload;reg[63:0]shadow_design;reg[31:0]shadow_checkpoint;
 assign active_version=current_version;
 assign active_payload=configured?{descriptor[2303:2272],current_version,descriptor[2239:0]}:2304'd0;
 assign staged_valid=!rst&&!abort&&prepared&&!load_rsp_valid&&state==IDLE&&!fault;
 assign staged_design=staged_valid?shadow_design:64'd0;
 assign staged_checkpoint=staged_valid?shadow_checkpoint:32'd0;
 assign staged_version=staged_valid?shadow_payload[2240+:32]:32'd0;
 assign staged_payload=staged_valid?shadow_payload:2304'd0;
 assign publish_ready=staged_valid&&publish_permit&&!load_valid&&!start_valid&&!attempt_reset&&!discard_valid&&backend_drained&&normal_retired;
 assign discard_ready=staged_valid&&publish_permit&&!load_valid&&!start_valid&&!attempt_reset&&!publish_valid&&backend_drained&&normal_retired;
''';s=s[:idx]+decl+s[idx:]
 s=rep(s,'assign load_ready=!rst&&!attempt_reset', 'assign load_ready=!rst&&!abort&&!attempt_reset')
 s=rep(s,'assign start_ready=!rst&&!attempt_reset', 'assign start_ready=!rst&&!prepared&&!attempt_reset')
 s=rep(s,'if(rst)begin state<=IDLE;', 'if(rst)begin prepared<=0;shadow_payload<=0;shadow_design<=0;shadow_checkpoint<=0;state<=IDLE;')
 s=rep(s,'stopped<=0;error_code<=0;elapsed<=0;tx_version<=0;sent<=0;retired<=0;', 'prepared<=0;stopped<=0;error_code<=0;elapsed<=0;tx_version<=0;sent<=0;retired<=0;')
 needle='if(!load_authoritative||!descriptor_ok(load_payload,load_design)||(configured&&load_design==saved_design&&(load_checkpoint<=saved_checkpoint||load_payload[2240+:32]<current_version)))load_status<=1;'
 repl='''if(prepared||(!load_stage&&configured))load_status<=1;
      else if(load_stage)begin
       if(!publish_permit||!configured||!load_authoritative||load_design!=saved_design||load_checkpoint<=saved_checkpoint||!descriptor_ok(load_payload,load_design)||load_payload!=active_payload)load_status<=1;
       else begin prepared<=1;shadow_payload<=load_payload;shadow_design<=load_design;shadow_checkpoint<=load_checkpoint;end
      end
      else '''+needle
 s=rep(s,needle,repl)
 tail='''   endcase
   if(publish_valid&&publish_ready)begin descriptor<=shadow_payload;saved_design<=shadow_design;saved_checkpoint<=shadow_checkpoint;current_version<=shadow_payload[2240+:32];prepared<=0;end
   if((discard_valid&&discard_ready)||abort||fail_now)prepared<=0;
''';s=rep(s,'   endcase\n',tail);out['config_restore_controller.sv']=s
 return out
if __name__=='__main__':
 for n,s in make().items():(HERE/n).write_text(s)
