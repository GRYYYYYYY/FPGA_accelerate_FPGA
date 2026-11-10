"""Isolate native recovery-coordinator / label-service reset-retirement feedback."""
from pathlib import Path
import re
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/restore_seed_synth_on_v1/sources')

def sources(fixed):
    out={n:(BASE/n).read_text()for n in ['recovery_coordinator.sv','label_restore_controller.sv','residency_system.sv']}
    if fixed:
        s=out['label_restore_controller.sv']
        old='input wire start_skip_seed,output wire l_import,'
        assert s.count(old)==1;s=s.replace(old,'output wire rearm_retired,\n '+old)
        old=' assign busy=!rst&&state!=IDLE;'
        assert s.count(old)==1;s=s.replace(old,''' // Retirement must not be made true by the reset it authorizes. The
 // synchronous service state and outstanding reply are the authority.
 assign rearm_retired=state==IDLE&&!rsp_valid;
 assign busy=!rst&&state!=IDLE;''')
        out['label_restore_controller.sv']=s
        s=out['recovery_coordinator.sv']
        old='assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!unexpected;'
        assert s.count(old)==1;s=s.replace(old,'''// In REARM neither response belongs to an active AS/AW/OS/OW request.
 // Use the direct response qualifiers, avoiding irrelevant READY feedback.
 assign attempt_reset=!cold_rst&&state==REARM&&retry_safe&&!a_rsp_valid&&!o_rsp_valid;''')
        out['recovery_coordinator.sv']=s
        s=out['residency_system.sv']
        for old,new in [('wire lr_busy;','wire lr_busy;wire lr_rearm_retired;'),
                        ('&&!cf_busy&&!lr_busy&&!cf_rsp_valid','&&!cf_busy&&lr_rearm_retired&&!cf_rsp_valid'),
                        ('label_restore(.start_skip_seed','label_restore(.rearm_retired(lr_rearm_retired),.start_skip_seed')]:
            assert s.count(old)==1,(old,s.count(old));s=s.replace(old,new)
        out['residency_system.sv']=s
    return out

def ports(text):
    header=text[text.index('input wire'):].split('\n);',1)[0]
    # The new output preceding the first input is added explicitly by the caller.
    result=[];direction=width=None
    for token in header.split(','):
        token=token.strip()
        m=re.match(r'^(input|output)\s+(?:wire|reg)\s*(\[[^]]+\])?\s*(\w+)$',token)
        if m:direction,width,name=m.groups();width=width or ''
        else:
            assert re.fullmatch(r'\w+',token),token
            assert direction is not None;name=token
        result.append((direction,width,name))
    return result

def wrapper(fixed):
    s=sources(False);kp=ports(s['recovery_coordinator.sv']);lp=ports(s['label_restore_controller.sv'])
    external=[('input','','clk'),('input','','cold_rst'),('input','','external_abort'),
              ('input','','external_safe'),('input','','external_normal_retired'),('input','','physical_drained'),
              ('input','','l_start_offer'),('output','','l_rearm_retired')]
    km={'clk':'clk','cold_rst':'cold_rst','abort':'external_abort||l_fault',
        'retry_safe':'external_safe&&l_rearm_retired',
        'normal_retired':'external_normal_retired&&!l_busy&&!l_rsp_valid','backend_drained':'physical_drained'}
    for d,w,n in kp:
        if n not in km:external.append((d,w,'k_'+n));km[n]='k_'+n
    lm={'clk':'clk','rst':'cold_rst||k_attempt_reset','abort':'external_abort',
        'backend_drained':'physical_drained','start_valid':'k_labels_valid&&l_start_offer',
        'start_design':'k_saved_design','start_checkpoint':'k_saved_checkpoint',
        'start_version':'k_new_version','start_query':'k_new_query','start_price':'k_new_price'}
    for d,w,n in lp:
        if n not in lm:external.append((d,w,'l_'+n));lm[n]='l_'+n
    assert len(external)==len({n for _,_,n in external})
    text='`timescale 1ns/1ps\nmodule rearm_loop_slice(\n'+',\n'.join(f' {d} wire {w} {n}'for d,w,n in external)+'\n);\n'
    text+='recovery_coordinator #(.ENTRIES(4),.RESET_HOLD(3),.MAX_CYCLES(2048))k(\n'+',\n'.join(f'.{n}({km[n]})'for _,_,n in kp)+');\n'
    if fixed:lm['rearm_retired']='l_rearm_retired'
    else:text+='assign l_rearm_retired=!l_busy&&!l_rsp_valid;\n'
    text+='label_restore_controller #(.MAX_RECORDS(4),.CHECK_SOURCE_CRC(1),.MAX_CYCLES(1024))l(\n'+',\n'.join(f'.{n}({v})'for n,v in lm.items())+');\nendmodule\n'
    return text,external

def testbench():
    _,external=wrapper(True)
    text='`timescale 1ns/1ps\nmodule tb_rearm_loop;\n'
    for direction,width,name in external:text+=(f'reg {width} {name}=0;\n'if direction=='input'else f'wire {width} {name};\n')
    text+='''always #5 clk=~clk;
rearm_loop_slice dut(.*);
reg started=0;reg[159:0]ram=0;reg present=0;
integer scenario=0,checks=0,resets=0,writes=0,reads=0,successes=0,failures=0;
reg[159:0]payload=160'h0000000500000004000000030000000200000001;
function[31:0]crcword(input[31:0]c0,w);reg[31:0]c;begin c=c0;for(integer j=0;j<32;j=j+1)c=(c[0]^w[j])?((c>>1)^32'hedb88320):(c>>1);crcword=c;end endfunction
function[31:0]payload_crc;reg[31:0]c;begin c=crcword(32'hffffffff,7);for(integer j=0;j<5;j=j+1)c=crcword(c,payload[j*32+:32]);payload_crc=~c;end endfunction
always @(posedge clk)begin
 if(cold_rst)begin l_c_rsp_valid<=0;l_l_rsp_valid<=0;ram<=0;present<=0;started<=0;k_labels_done<=0;resets<=0;writes<=0;reads<=0;end
 else begin
  if(k_a_valid||k_o_valid)$fatal(1,"J0 unexpectedly accessed owner or authority");
  if(k_attempt_reset)begin
   if(!external_safe||!external_normal_retired||!physical_drained||l_rsp_valid||!l_rearm_retired||k_a_rsp_valid||k_o_rsp_valid)$fatal(1,"unsafe rearm pulse");
   resets<=resets+1;started<=0;k_labels_done<=0;
   $display("RESET %0d %0d",scenario,k_new_version);
  end
  if(k_target_reset)begin started<=0;k_labels_done<=0;end
  if(k_labels_valid&&l_start_offer&&l_start_ready)started<=1;
  if(l_rsp_valid&&l_rsp_ready&&l_rsp_status==0)k_labels_done<=1;
  if(l_c_rsp_valid&&l_c_rsp_ready)l_c_rsp_valid<=0;
  if(l_c_valid&&l_c_ready)begin
   if(l_c_rsp_valid)$fatal(1,"config overlap");l_c_rsp_valid<=1;l_c_status<=0;
   if(l_c_op==0)begin ram<=0;present<=0;end
  end
  if(l_l_rsp_valid&&l_l_rsp_ready)l_l_rsp_valid<=0;
  if(l_l_valid&&l_l_ready)begin
   if(l_l_rsp_valid)$fatal(1,"label overlap");l_l_rsp_valid<=1;l_l_status<=0;l_l_present<=present;l_l_payload<=ram;
   if(l_l_write)begin
    if(l_l_node!=7||l_l_field>4||l_l_value!=payload[l_l_field*32+:32])$fatal(1,"restore data mismatch");
    ram[l_l_field*32+:32]<=l_l_value;present<=1;writes<=writes+1;
    $display("WRITE %0d %0d %h",scenario,l_l_field,l_l_value);
   end else begin reads<=reads+1;if(l_l_probe&&present)$fatal(1,"probe not empty");end
  end
 end
end
always @*l_start_offer=!started;
task tick;begin @(posedge clk);#1;end endtask
task init(input integer mode);begin
 @(negedge clk);scenario=mode;cold_rst=1;external_abort=0;external_safe=1;external_normal_retired=1;physical_drained=1;
 k_cfg_valid=0;k_recover_valid=0;k_rsp_ready=0;k_cfg_rsp_ready=0;k_a_rsp_valid=0;k_o_rsp_valid=0;
 l_rsp_ready=0;l_s_valid=1;l_s_node=7;l_s_cookie=17;l_s_payload=payload;l_s_last=1;
 l_expected_design=99;l_expected_checkpoint=17;l_start_cookie=17;l_start_count=1;l_start_nodes=16;l_start_probe=7;l_start_skip_seed=1;
 l_start_source_crc=payload_crc()^1;l_c_ready=1;l_l_ready=1;k_reconfigure_done=1;
 repeat(3)tick;@(negedge clk);cold_rst=0;
 k_cfg_authoritative=1;k_cfg_design=99;k_cfg_checkpoint=17;k_cfg_version=1;k_cfg_query=1;k_cfg_price=1;k_cfg_valid=1;
 do tick;while(!k_cfg_rsp_valid);@(negedge clk);k_cfg_valid=0;
 if(k_cfg_status)$fatal(1,"configuration failed");k_cfg_rsp_ready=1;tick;@(negedge clk);k_cfg_rsp_ready=0;
 k_recover_design=99;k_recover_checkpoint=17;k_recover_version=2;k_recover_query=2;k_recover_price=2;k_recover_cookie=100;
end endtask
task request;begin
 @(negedge clk);k_recover_valid=1;do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;
end endtask
task result(input integer status);begin
 wait(k_rsp_valid);@(negedge clk);
 repeat(8)begin tick;
  if(!k_rsp_valid||k_rsp_status!=status||k_rsp_cookie!=k_recover_cookie||k_permit_work||k_rsp_corrected||k_journal_count)$fatal(1,"held coordinator result");checks=checks+1;
 end
 $display("RESULT %0d %0d %0d %0d",scenario,k_rsp_status,k_new_version,resets);
 if(status==0)successes=successes+1;else failures=failures+1;
 @(negedge clk);k_rsp_ready=1;tick;@(negedge clk);k_rsp_ready=0;tick;
end endtask
task fail_labels;begin
 request;wait(l_rsp_valid);@(negedge clk);
 repeat(8)begin tick;if(l_rsp_status!=8||k_rsp_valid||l_rearm_retired||!l_busy||writes)$fatal(1,"failed service not retired");checks=checks+1;end
 @(negedge clk);l_rsp_ready=1;tick;@(negedge clk);l_rsp_ready=0;result(6);
 if(!l_rearm_retired||!k_fault||k_permit_work||resets)$fatal(1,"failure did not stay closed");
end endtask
task success_labels;begin
 wait(l_rsp_valid);@(negedge clk);
 repeat(8)begin tick;if(l_rsp_status||l_written!=1||l_verified!=1||k_rsp_valid||l_rearm_retired||writes!=5||ram!==payload)$fatal(1,"success before full restoration/retirement");checks=checks+1;end
 @(negedge clk);l_rsp_ready=1;tick;@(negedge clk);l_rsp_ready=0;result(0);
 if(!k_permit_work||k_fault||!l_rearm_retired||resets!=1)$fatal(1,"successful retry did not release");
end endtask
initial begin
 for(integer mode=0;mode<3;mode=mode+1)begin
  init(mode);fail_labels;
  // Old attempt remains consumed; no transient reset is permitted.
  k_recover_cookie=101;k_recover_query=3;request;result(1);
  if(resets||!k_fault)$fatal(1,"rejected attempt reset state");
  k_recover_version=3;k_recover_query=3;k_recover_price=3;k_recover_cookie=102;l_start_source_crc=payload_crc();
  external_safe=0;@(negedge clk);k_recover_valid=1;
  repeat(5)begin tick;if(k_recover_ready||k_attempt_reset)$fatal(1,"unsafe retry admitted");checks=checks+1;end
  @(negedge clk);external_safe=1;external_normal_retired=0;
  repeat(4)begin tick;if(k_recover_ready||k_attempt_reset)$fatal(1,"unretired retry admitted");checks=checks+1;end
  @(negedge clk);external_normal_retired=1;
  do @(posedge clk);while(!k_recover_ready);@(negedge clk);k_recover_valid=0;
  if(mode!=0)begin
   if(mode==1)external_safe=0;else begin k_a_rsp_valid=1;external_normal_retired=0;end
   #1;if(k_attempt_reset)$fatal(1,"rearm ignored withdrawn safety or late response");
   repeat(4)tick;
   if(resets||!k_fault)$fatal(1,"unsafe rearm cleared service");
   @(negedge clk);external_safe=1;k_a_rsp_valid=0;external_normal_retired=1;
   result(6);
   k_recover_cookie=103;k_recover_query=0;request;result(1);
   if(resets)$fatal(1,"failed retry floor lost");
   k_recover_version=4;k_recover_query=0;k_recover_price=4;k_recover_cookie=104;request;
  end
  success_labels;
 end
 if(successes!=3||failures!=10)$fatal(1,"scenario accounting %0d %0d",successes,failures);
 $display("REARM_LOOP_PASS scenarios=3 successes=%0d failures=%0d checks=%0d",successes,failures,checks);$finish;
end
initial begin #1000000;$fatal(1,"watchdog");end
endmodule
'''
    return text

if __name__=='__main__':
    for mode in ['baseline','fixed']:
        d=HERE/mode;d.mkdir(exist_ok=False)
        for name,s in sources(mode=='fixed').items():(d/name).write_text(s)
        (d/'rearm_loop_slice.sv').write_text(wrapper(mode=='fixed')[0])
    (HERE/'tb_rearm_loop.sv').write_text(testbench())
