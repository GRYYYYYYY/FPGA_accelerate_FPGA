"""Compose native backend exclusion and zero-depth capture retirement."""
from pathlib import Path
import importlib.util,re

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
BASE=Path('/tmp/B_state_residency_offer_20261025/route_block_system_crc_pressure_v1')
def load(name):
    spec=importlib.util.spec_from_file_location(name,HERE.parent/name/'build.py')
    b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b);return b
backend=load('recovery_backend_loops_v2')
capture=load('capture_retirement_loops_v1')
NAMES=backend.NAMES+[capture.NAME]
def sources(fixed):
    result=backend.sources(fixed)
    assert not(set(result)&set(capture.sources(fixed)))
    result.update(capture.sources(fixed))
    for n,s in result.items():
        origin=(HERE.parent/('capture_retirement_loops_v1'if n==capture.NAME else 'recovery_backend_loops_v2')/('fixed'if fixed else 'baseline')/n)
        assert origin.read_text()==s,n
    return result
def monitored_tb(original):
    s=backend.monitored_tb(original)
    core='system.inner.backend.dut.core.'
    old=capture.sources(False)[capture.NAME]
    expr=re.findall(r' assign retired_idle=(.*?);',old,re.S)
    assert len(expr)==1
    qualified=re.sub(r'\b[A-Za-z_]\w*\b',lambda m:core+m[0],expr[0])
    decl=' integer capture_idle_checks=0,capture_nonzero_cycles=0,capture_reply_cycles=0;\n wire capture_original_idle='+qualified+';\n'
    s=backend.replace_once(s,'module tb_candidate_offer;','module tb_candidate_offer;\n'+decl)
    monitor='''
 always @(posedge clk)if(!k_cold_rst)begin
  if((COREcapture_depth==0&&COREe_result_valid)!==1'b0)
   $fatal(1,"zero-depth capture produced a result");
  if(COREretired_idle!==capture_original_idle)
   $fatal(1,"capture retirement predicate changed");
  capture_idle_checks=capture_idle_checks+1;
  if(COREcapture_depth!=0)capture_nonzero_cycles=capture_nonzero_cycles+1;
  if(COREe_result_valid)capture_reply_cycles=capture_reply_cycles+1;
 end
'''.replace('CORE',core)
    s=backend.replace_once(s,'\nendmodule',monitor+'\nendmodule')
    marker=' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
    check=''' if(capture_idle_checks==0||capture_nonzero_cycles==0||capture_reply_cycles==0)
  $fatal(1,"capture retirement coverage missing");
 $display("CAPTURE_RETIREMENT_PASS cycles=%0d nonzero=%0d replies=%0d",capture_idle_checks,capture_nonzero_cycles,capture_reply_cycles);
'''
    return backend.replace_once(s,marker,check+marker)
if __name__=='__main__':
    for mode in ['baseline','fixed']:
        d=HERE/mode;d.mkdir()
        for n,s in sources(mode=='fixed').items():
            q=d/n;q.parent.mkdir(parents=True,exist_ok=True);q.write_text(s)
    (HERE/'tb_query_fault.sv').write_text(monitored_tb((BASE/'sources/tb_query_fault.sv').read_text()))
    print('NATIVE_RETIREMENT_PREPARED_NOT_VALIDATED')
