"""Prepare explicit CP export-data contract checks on the calibrated clock.

Only cp_m_data is valid-qualified. All345 other output comparisons stay exact.
Add pre-clock transfer observations so the final accepted beat is also checked.
"""
import json
from host_edit_system_common_v1 import ROOT,BASE,read,sha,verify_freeze


CP_TASK = '''task check_cp_output;
input integer at_edge;
begin
 if((expected_cp_m_valid!==1'b0&&expected_cp_m_valid!==1'b1)||
    (actual_cp_m_valid!==1'b0&&actual_cp_m_valid!==1'b1))
  $fatal(1,"CP_VALID_UNKNOWN phase=%0d time=%0t actual=%b expected=%b",at_edge,$time,actual_cp_m_valid,expected_cp_m_valid);
 if(actual_cp_m_valid!==expected_cp_m_valid)
  $fatal(1,"CP_VALID_MISMATCH phase=%0d time=%0t actual=%b expected=%b",at_edge,$time,actual_cp_m_valid,expected_cp_m_valid);
 if(expected_cp_m_valid===1'b1)begin
  cp_active_checks=cp_active_checks+1;
  if(at_edge!=0)cp_edge_checks=cp_edge_checks+1;
  if(drive_cp_m_ready===1'b0)cp_stall_checks=cp_stall_checks+1;
  else if(drive_cp_m_ready===1'b1)begin
   if(at_edge!=0)cp_transfer_checks=cp_transfer_checks+1;
  end else $fatal(1,"CP_READY_UNKNOWN phase=%0d time=%0t",at_edge,$time);
  if((^expected_cp_m_data)===1'bx||(^actual_cp_m_data)===1'bx)
   $fatal(1,"CP_DATA_UNKNOWN phase=%0d time=%0t actual=%h expected=%h",at_edge,$time,actual_cp_m_data,expected_cp_m_data);
  if(actual_cp_m_data!==expected_cp_m_data)
   $fatal(1,"CP_DATA_MISMATCH phase=%0d ready=%b time=%0t actual=%h expected=%h",at_edge,drive_cp_m_ready,$time,actual_cp_m_data,expected_cp_m_data);
  if((^expected_cp_m_index)===1'bx||(^actual_cp_m_index)===1'bx||
     (expected_cp_m_last!==1'b0&&expected_cp_m_last!==1'b1)||
     (actual_cp_m_last!==1'b0&&actual_cp_m_last!==1'b1))
   $fatal(1,"CP_META_UNKNOWN phase=%0d time=%0t",at_edge,$time);
  if(actual_cp_m_index!==expected_cp_m_index||actual_cp_m_last!==expected_cp_m_last)
   $fatal(1,"CP_META_MISMATCH phase=%0d time=%0t",at_edge,$time);
 end else begin
  cp_idle_observations=cp_idle_observations+1;
  if(actual_cp_m_data!==expected_cp_m_data)cp_idle_differences=cp_idle_differences+1;
 end
end endtask
always @(posedge drive_clk)if(armed)check_cp_output(1);
'''


def render(parent):
    old_data='  if(actual_cp_m_data!==expected_cp_m_data)\n   $fatal(1,"FULL_SHADOW_MISMATCH port=cp_m_data time=%0t actual=%h expected=%h",$time,actual_cp_m_data,expected_cp_m_data);'
    old_pass=' $display("FULL_SHADOW_PASS outputs=346 bits=14384 checks=%0d reset_edges=%0d original_end=%0t last_checked=%0t",checks,reset_edges,original_end,last_checked);'
    new_pass=''' if(cp_active_checks==0||cp_stall_checks==0||cp_transfer_checks==0||cp_edge_checks==0||cp_idle_observations==0)
  $fatal(1,"CP_PROTOCOL_COVERAGE_MISSING active=%0d stalled=%0d transfers=%0d edges=%0d idle=%0d",cp_active_checks,cp_stall_checks,cp_transfer_checks,cp_edge_checks,cp_idle_observations);
 $display("FULL_SHADOW_PROTOCOL_PASS outputs=346 unconditional=345 qualified=cp_m_data checks=%0d reset_edges=%0d original_end=%0t last_checked=%0t active=%0d stalled=%0d transfers=%0d edges=%0d idle=%0d idle_differences=%0d",checks,reset_edges,original_end,last_checked,cp_active_checks,cp_stall_checks,cp_transfer_checks,cp_edge_checks,cp_idle_observations,cp_idle_differences);'''
    patches=[
      ('integer checks=0,reset_edges=0;', 'integer checks=0,reset_edges=0;\ninteger cp_active_checks=0,cp_stall_checks=0,cp_transfer_checks=0,cp_edge_checks=0,cp_idle_observations=0,cp_idle_differences=0;'),
      ('always @(posedge drive_clk) begin',CP_TASK+'always @(posedge drive_clk) begin'),
      ('  checks=checks+1;last_checked=$time;', '  checks=checks+1;last_checked=$time;\n  check_cp_output(0);'),
      (old_data,'  // cp_m_data checked by the explicit valid/ready contract task.'),
      (old_pass,new_pass)]
    result=parent
    for old,new in patches:
        assert result.count(old)==1
        result=result.replace(old,new,1)
    inverse=result
    for old,new in reversed(patches):
        assert inverse.count(new)==1;inverse=inverse.replace(new,old,1)
    assert inverse==parent
    ports=read(ROOT/'results/stage_static_cp_port_schema_20261030.json')['ports']
    for p in ports:
        if p['direction']=='output' and p['name']!='cp_m_data':
            n=p['name'];block=f'  if(actual_{n}!==expected_{n})\n   $fatal(1,"FULL_SHADOW_MISMATCH port={n} time=%0t actual=%h expected=%h",$time,actual_{n},expected_{n});'
            assert parent.count(block)==result.count(block)==1,n
    return result


def main():
    clock=ROOT/'results/shadow_clock_sampling_controls_20261030.json'
    failed=ROOT/'results/stage_static_cp_shadow_failure_20261030.json'
    assert read(clock)['status']=='shadow_clock_sampling_controls_actual_restored'
    assert read(failed)['validity_probe_audit']['no_export_transfer_at_failure']
    cf=verify_freeze(ROOT/'results/shadow_clock_sampling_controls_sources_20261030')
    ff=verify_freeze(ROOT/'results/stage_static_cp_shadow_failure_sources_20261030')
    parent=ROOT/'hardware/variants/stage_static_cp_shadow_clock_v2/shadow.sv'
    assert sha(parent)==read(parent.parent/'manifest.json')['files']['shadow.sv']
    source=BASE/'stage_static_cp_host_full_static_v1/sources/tb_query_fault.sv'
    original=source.read_text();marker='$display("ITER2_CONTINUOUS_PREP_PASS");$finish;'
    assert original.count(marker)==1
    tb=original.replace(marker,'$display("ITER2_CONTINUOUS_PREP_PASS");stage_static_cp_shadow.finish_and_check;$finish;')
    assert tb.replace('stage_static_cp_shadow.finish_and_check;','')==original
    out=ROOT/'hardware/variants/stage_static_cp_shadow_protocol_v4';assert not out.exists();out.mkdir()
    (out/'shadow.sv').write_text(render(parent.read_text()));(out/'tb_query_fault.sv').write_text(tb)
    report=dict(status='cp_export_contract_checker_prepared_not_simulated',
                files={n:sha(out/n) for n in ['shadow.sv','tb_query_fault.sv']},
                source_tb_sha256=sha(source),parent_clock_shadow_sha256=sha(parent),
                generator_sha256=sha(__file__),clock_lead_ps=1,input_and_expected_transport_ns=200,
                unconditional_outputs=345,qualified_outputs={'cp_m_data':'known/equal cp_m_valid=1, regardless ready'},
                all_345_original_comparison_blocks_exact=True,pre_clock_cp_transfer_checks=True,
                active_payload_and_metadata_require_known=True,
                old_strict_pin_failure_sha256=sha(failed),clock_controls_sha256=sha(clock),
                source_freeze_sha256={str(cf):sha(cf),str(ff):sha(ff)},
                all_pin_strict_equivalence=False,full_system_functional_netlist_validated=False,
                scope='CP export protocol observation only for32-bit data outside valid0. Valid control strict and binary; all valid data including ready0 and transfer edge checked; no wildcard X matching. All other345 output comparisons exact. Needs independent controls and new full run; previous strict all-pin failure retained.')
    (out/'manifest.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    receipt=ROOT/'results/stage_static_cp_shadow_protocol_v4_preparation_20261030.json';assert not receipt.exists()
    receipt.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('CP_PROTOCOL_CHECKER_V4_PREPARED_345_COMPARISON_BLOCKS_EXACT')


if __name__=='__main__':main()
