from pathlib import Path
import runpy

HERE = Path(__file__).resolve().parent
builder = runpy.run_path(str(HERE/'build.py'))
BASE, replace = builder['BASE'], builder['replace']

def make():
    s = (BASE/'sources/tb_query_fault.sv').read_text()
    s = replace(s, 'module tb_candidate_offer;', '''module tb_candidate_offer;
`ifdef RESTORE_SEED_BYPASS
localparam SEED_BYPASS=1;
`else
localparam SEED_BYPASS=0;
`endif''')
    s = replace(s, 'reg g4_warm_mode=0;', '''reg g4_warm_mode=0;
reg seed_start_consumed=0;
wire seed_enable=SEED_BYPASS&&g4_warm_mode&&!seed_start_consumed;
integer seed_log,seed_requests=0;
initial seed_log=$fopen("restore_seed_trace.txt","w");''')
    s = replace(s, 'query_residency_system #(.PATH_SLOTS(4),',
                'query_residency_system #(.ENABLE_RESTORE_SEED_BYPASS(SEED_BYPASS),.PATH_SLOTS(4),')
    s = replace(s, '))system(.baseline_', '))system(.restore_seed_enable(seed_enable),.baseline_')
    observer = '''
// Observe actual downstream acceptance after the frontend queue, including WW.
`define SEED_PM system.inner.backend.dut.core.p.pager
`define SEED_LR system.inner.backend.label_restore
always @(posedge clk)if(!rst)begin
 if(lr_start_valid&&lr_start_ready&&g4_warm_mode&&SEED_BYPASS)begin
  if(!seed_enable||seed_start_consumed)$fatal(1,"seed permission not offered at start");
  seed_start_consumed<=1;
  $fdisplay(seed_log,"START %0d",cycles);
 end
 if(`SEED_PM.io_valid&&`SEED_PM.io_ready)begin
  if(`SEED_PM.baseline_restore_write)begin
   if(!SEED_BYPASS||!g4_warm_mode||!seed_start_consumed||seed_enable||
      !f_recovery_owned||!system.inner.backend.k_labels_valid||!`SEED_LR.l_import||
      !`SEED_PM.io_write||`SEED_PM.baseline_raw_probe)
       $fatal(1,"unauthorized restore seed bypass");
   seed_requests<=seed_requests+1;
   $fdisplay(seed_log,"WRITE %0d %0d %0d %08h %0d",cycles,
    `SEED_PM.io_node,`SEED_PM.io_field,`SEED_PM.io_value,`SEED_LR.state);
  end
  if(SEED_BYPASS&&g4_warm_mode&&`SEED_LR.l_import&&
     !`SEED_PM.baseline_restore_write)$fatal(1,"lost queued restore provenance");
 end
 if(SEED_BYPASS&&g4_warm_mode&&lr_rsp_ready&&system.inner.backend.lr_rsp_valid)begin
  if(lr_rsp_status!=0||lr_written!=781||lr_verified!=781||seed_requests!=3905)
   $fatal(1,"seed bypass restore completion mismatch");
  $fdisplay(seed_log,"PASS %0d %0d %0d %0d",cycles,seed_requests,lr_written,lr_verified);
 end
end
`undef SEED_PM
`undef SEED_LR
'''
    s = replace(s, 'endmodule', observer+'\nendmodule')
    return s

if __name__ == '__main__':
    (HERE/'tb_restore_seed.sv').write_text(make())
