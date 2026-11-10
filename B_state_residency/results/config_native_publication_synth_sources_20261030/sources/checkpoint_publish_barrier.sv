`timescale 1ns/1ps
module checkpoint_publish_barrier(
 input wire clk,rst,lease_owned,retired,stage_busy,fault,manifest_ready,
 input wire start_valid,output wire start_ready,input wire[63:0]start_design,start_generation,input wire[31:0]start_checkpoint,start_version,input wire[1:0]start_query,input wire[3:0]start_price,
 input wire commit_valid,cancel_valid,output wire commit_ready,cancel_ready,
 output wire owned,prepare_allowed,done_valid,input wire done_ready,output wire[1:0]done_status,
 input wire[2:0]prepared,publish_ready,discard_ready,output wire[2:0]publish_valid,discard_valid,
 input wire[63:0]a_design,a_generation,k_design,c_design,sa_design,sa_generation,sk_design,sc_design,
 input wire[31:0]a_checkpoint,k_checkpoint,c_checkpoint,k_version,c_version,journal_count,sa_checkpoint,sk_checkpoint,sc_checkpoint,sk_version,sc_version,
 input wire[1:0]k_query,sk_query,input wire[3:0]k_price,sk_price
);
 localparam IDLE=0,OPEN=1,VERIFY=2,CANCEL=3,DONE=4,HALT=5;
 reg[2:0]state;reg[1:0]status;reg halt_reported;
 reg[63:0]d,g,base_generation;reg[31:0]cp,v,base_checkpoint,base_journal;reg[1:0]q;reg[3:0]price;
 wire base_ok=a_design==d&&k_design==d&&c_design==d&&a_generation==base_generation&&a_checkpoint==base_checkpoint&&k_checkpoint==base_checkpoint&&c_checkpoint==base_checkpoint&&k_version==v&&c_version==v&&k_query==q&&k_price==price&&journal_count==base_journal;
 wire stage_ok=sa_design==d&&sk_design==d&&sc_design==d&&sa_generation==g&&sa_checkpoint==cp&&sk_checkpoint==cp&&sc_checkpoint==cp&&sk_version==v&&sc_version==v&&sk_query==q&&sk_price==price;
 wire new_ok=a_design==d&&k_design==d&&c_design==d&&a_generation==g&&a_checkpoint==cp&&k_checkpoint==cp&&c_checkpoint==cp&&k_version==v&&c_version==v&&k_query==q&&k_price==price&&journal_count==0;
 wire start_ok=start_design!=0&&start_design==a_design&&k_design==a_design&&c_design==a_design&&a_checkpoint==k_checkpoint&&a_checkpoint==c_checkpoint&&start_generation>a_generation&&start_checkpoint>a_checkpoint&&start_version==k_version&&c_version==k_version&&start_query==k_query&&start_price==k_price&&start_price==start_version[3:0];
 assign owned=!rst&&state!=IDLE;
 assign prepare_allowed=!rst&&state==OPEN&&lease_owned&&!fault&&!commit_valid&&!cancel_valid;
 assign start_ready=!rst&&state==IDLE&&lease_owned&&retired&&!stage_busy&&!fault&&prepared==0;
 assign commit_ready=!rst&&state==OPEN&&lease_owned&&retired&&!stage_busy&&!fault&&manifest_ready&&(&prepared)&&(&publish_ready)&&!cancel_valid;
 assign cancel_ready=!rst&&state==OPEN&&lease_owned&&!commit_valid;
 assign publish_valid={3{commit_valid&&commit_ready&&stage_ok&&base_ok}};
 assign discard_valid=(!rst&&state==CANCEL)?prepared:3'd0;
 assign done_valid=!rst&&(state==DONE||(state==HALT&&!halt_reported));
 assign done_status=state==HALT?2'd3:status;
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;status<=0;halt_reported<=0;d<=0;g<=0;cp<=0;v<=0;q<=0;price<=0;base_generation<=0;base_checkpoint<=0;base_journal<=0;end
  else begin
   case(state)
    IDLE:if(start_valid&&start_ready)begin
     d<=start_design;g<=start_generation;cp<=start_checkpoint;v<=start_version;q<=start_query;price<=start_price;base_generation<=a_generation;base_checkpoint<=a_checkpoint;base_journal<=journal_count;halt_reported<=0;
     if(start_ok)state<=OPEN;else begin status<=1;state<=DONE;end
    end
    OPEN:begin
     if(!lease_owned||fault||!base_ok)state<=HALT;
     else if(cancel_valid&&cancel_ready)begin status<=2;state<=CANCEL;end
     else if(commit_valid&&commit_ready)begin
      if(stage_ok)begin status<=0;state<=VERIFY;end
      else begin status<=1;state<=CANCEL;end
     end
    end
    VERIFY:if(!lease_owned||fault||!new_ok)state<=HALT;else state<=DONE;
    CANCEL:if(!lease_owned||fault||!base_ok)state<=HALT;
           else if(prepared==0&&!stage_busy&&retired)state<=DONE;
    DONE:if(done_ready)state<=IDLE;
    HALT:if(done_ready)halt_reported<=1;
    default:state<=HALT;
   endcase
  end
 end
endmodule
