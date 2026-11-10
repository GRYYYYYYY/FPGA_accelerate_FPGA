"""Two immutable reader banks; explicit quiescent publication, no journal changes."""
from pathlib import Path
import re
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1/sources/checkpoint_authority_reader.sv')
def ports(s):
 text=s[s.index(' input wire clk'):s.index('\n);')];out=[]
 for chunk in text.replace('\n',' ').split(','):
  m=re.match(r'\s*(input|output)\s+(wire|reg)\s*(\[[^]]+\])?\s*(\w+)\s*$',chunk)
  if m:direction,_,width,name=m.groups();width=width or ''
  else:name=chunk.strip()
  out.append((direction,width,name))
 return out

def make():
 source=BASE.read_text();ps=ports(source)
 head=source[:source.index('\n);')+4].replace('module checkpoint_authority_reader','module checkpoint_authority_rotator').replace('output reg','output wire')
 extra=''' input wire cfg_stage,publish_valid,publish_permit,discard_valid,
 output wire publish_ready,discard_ready,active_slot,staged_valid,
 output wire[63:0]staged_design,staged_generation,output wire[31:0]staged_checkpoint,
'''
 head=head.replace(' input wire clk',extra+' input wire clk')
 body='''
 localparam IDLE=0,RESET_BANK=1,SEND_CFG=2,WAIT_CFG=3,HELD_CFG=4;
 reg[2:0]state;reg active_bank,target,staging,prepared;reg[2:0]held_status;
'''
 payload=[(w,n)for d,w,n in ps if d=='input'and n.startswith('cfg_')and n not in ['cfg_valid','cfg_permit','cfg_rsp_ready']]
 body+=''.join(f' reg {w}h_{n};\n'for w,n in payload)
 for i in range(2):
  body+=''.join(f' wire {w}b{i}_{n};\n'for d,w,n in ps if d=='output')
 body+='''
 wire cfg_busy=state!=IDLE;
 wire axi_bank=cfg_busy?target:active_bank;
 wire all_quiet=!b0_busy&&!b1_busy&&b0_drained&&b1_drained;
 wire active_fault=active_bank?b1_fault:b0_fault;
 wire inactive_configured=active_bank?b0_configured:b1_configured;
 wire inactive_fault=active_bank?b0_fault:b1_fault;
 assign active_slot=active_bank;
 assign configured=active_bank?b1_configured:b0_configured;
 assign bound_design=active_bank?b1_bound_design:b0_bound_design;
 assign bound_generation=active_bank?b1_bound_generation:b0_bound_generation;
 assign bound_checkpoint=active_bank?b1_bound_checkpoint:b0_bound_checkpoint;
 assign fault=active_fault;
 assign busy=cfg_busy||b0_busy||b1_busy;
 assign drained=b0_drained&&b1_drained;
 assign cfg_ready=!rst&&state==IDLE&&cfg_permit&&!abort&&!publish_valid&&!discard_valid&&!rearm_valid&&all_quiet;
 assign cfg_rsp_valid=!rst&&(state==HELD_CFG||(state==IDLE&&(active_bank?b1_cfg_rsp_valid:b0_cfg_rsp_valid)));
 assign cfg_status=state==HELD_CFG?held_status:(active_bank?b1_cfg_status:b0_cfg_status);
 assign cfg_rearmed=state==HELD_CFG?1'b0:(active_bank?b1_cfg_rearmed:b0_cfg_rearmed);
 assign rearm_ready=!rst&&state==IDLE&&!cfg_valid&&!publish_valid&&!discard_valid&&(active_bank?b1_rearm_ready:b0_rearm_ready);
 assign req_ready=!rst&&state==IDLE&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&(active_bank?b1_req_ready:b0_req_ready);
 assign staged_valid=!rst&&!abort&&state==IDLE&&prepared&&inactive_configured&&!inactive_fault;
 assign staged_design=staged_valid?(active_bank?b0_bound_design:b1_bound_design):64'd0;
 assign staged_generation=staged_valid?(active_bank?b0_bound_generation:b1_bound_generation):64'd0;
 assign staged_checkpoint=staged_valid?(active_bank?b0_bound_checkpoint:b1_bound_checkpoint):32'd0;
 assign publish_ready=!rst&&!abort&&staged_valid&&publish_permit&&!cfg_valid&&!rearm_valid&&!discard_valid&&!req_valid&&!active_fault&&all_quiet;
 assign discard_ready=!rst&&!abort&&staged_valid&&publish_permit&&!cfg_valid&&!rearm_valid&&!publish_valid&&!req_valid&&all_quiet;
'''
 for d,w,n in ps:
  if d!='output':continue
  if n.startswith('m_'):body+=f' assign {n}=axi_bank?b1_{n}:b0_{n};\n'
  elif n.startswith('rsp_'):body+=f' assign {n}=active_bank?b1_{n}:b0_{n};\n'
 for i in range(2):
  con=[]
  for d,w,n in ps:
   if d=='output':v=f'b{i}_{n}'
   elif n=='rst':v=f'rst||(state==RESET_BANK&&target=={i})'
   elif n.startswith('cfg_')and n not in ['cfg_valid','cfg_permit','cfg_rsp_ready']:v='h_'+n
   elif n=='cfg_valid':v=f'state==SEND_CFG&&target=={i}'
   elif n=='cfg_rsp_ready':v=f'(state==WAIT_CFG&&target=={i})||(state==IDLE&&active_bank=={i}&&cfg_rsp_ready)'
   elif n=='rearm_valid':v=f'state==IDLE&&active_bank=={i}&&!cfg_valid&&!publish_valid&&!discard_valid&&rearm_valid'
   elif n=='req_valid':v=f'state==IDLE&&active_bank=={i}&&!cfg_valid&&!publish_valid&&!discard_valid&&!rearm_valid&&req_valid'
   elif n=='rsp_ready':v=f'state==IDLE&&active_bank=={i}&&rsp_ready'
   elif n.startswith('m_')and n in ['m_arready','m_awready','m_wready','m_rvalid','m_bvalid']:v=f'axi_bank=={i}&&{n}'
   else:v=n
   con.append(f'.{n}({v})')
  body+=f' checkpoint_authority_reader #(.MAX_CYCLES(MAX_CYCLES)) bank{i}('+','.join(con)+');\n'
 body+='''
 always @(posedge clk)begin
  if(rst)begin state<=IDLE;active_bank<=0;target<=0;staging<=0;prepared<=0;held_status<=0;
'''+''.join(f'   h_{n}<=0;\n'for w,n in payload)+'''
  end else begin
   case(state)
    IDLE:begin
     if(cfg_valid&&cfg_ready)begin
      staging<=cfg_stage;held_status<=0;
      if((!cfg_stage&&(bound_generation!=0))||(cfg_stage&&(!configured||prepared||cfg_design!=bound_design||cfg_generation<=bound_generation||cfg_checkpoint<=bound_checkpoint)))begin held_status<=1;state<=HELD_CFG;end
      else begin
       target<=cfg_stage?~active_bank:active_bank;prepared<=0;
'''+''.join(f'       h_{n}<={n};\n'for w,n in payload)+'''
       state<=RESET_BANK;
      end
     end else if(publish_valid&&publish_ready)begin active_bank<=~active_bank;prepared<=0;end
     else if(discard_valid&&discard_ready)prepared<=0;
    end
    RESET_BANK:if(abort||!cfg_permit)begin held_status<=3;state<=HELD_CFG;end else state<=SEND_CFG;
    SEND_CFG:if(abort||!cfg_permit)begin held_status<=3;state<=HELD_CFG;end
             else if(target?b1_cfg_ready:b0_cfg_ready)state<=WAIT_CFG;
    WAIT_CFG:if(target?b1_cfg_rsp_valid:b0_cfg_rsp_valid)begin
     held_status<=target?b1_cfg_status:b0_cfg_status;
     if(staging&&(target?b1_cfg_status:b0_cfg_status)==0)prepared<=1;
     state<=HELD_CFG;
    end
    HELD_CFG:if(cfg_rsp_ready)state<=IDLE;
    default:state<=IDLE;
   endcase
   // Cancellation never changes the active selector; it invalidates pending publication.
   if(abort)prepared<=0;
  end
 end
endmodule
'''
 return head+body
if __name__=='__main__':(HERE/'checkpoint_authority_rotator.sv').write_text(make())
