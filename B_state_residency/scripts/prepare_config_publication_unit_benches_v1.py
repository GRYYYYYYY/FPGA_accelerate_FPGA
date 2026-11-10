"""Prepare observation-only unit TB copies, without producing candidate RTL."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT/'hardware/tests/config_native_publication_units_v1'

DECLARATIONS = '''
 integer pubcmp_file;
 string pubcmp_path;
'''
OBSERVATION = '''
 // Record each rising edge after NBA and before the original tick task's #1 checks.
 initial begin
  if(!$value$plusargs("publication_bank_trace=%s",pubcmp_path))$fatal(1,"publication bank trace path");
  pubcmp_file=$fopen(pubcmp_path,"w");if(!pubcmp_file)$fatal(1,"publication bank trace open");
 end
 always @(posedge clk)begin
  if(PUBCMP_NATIVE&&!rst&&dut.load_valid===1'b1&&dut.load_ready===1'b1&&dut.load_stage===1'b1)begin
   if(dut.load_payload!==dut.active_payload)$fatal(1,"publication native accepted-stage payload alias");
  end
  if(PUBCMP_NATIVE&&!rst&&dut.prepared===1'b1)begin
   if({dut.shadow_payload[2303:2272],dut.shadow_payload[2239:0]}!==
      {dut.descriptor[2303:2272],dut.descriptor[2239:0]})
    $fatal(1,"publication native prepared bank mismatch before NBA");
  end
  #0.1;
  if(PUBCMP_NATIVE&&!rst&&dut.prepared===1'b1)begin
   if({dut.shadow_payload[2303:2272],dut.shadow_payload[2239:0]}!==
      {dut.descriptor[2303:2272],dut.descriptor[2239:0]})
    $fatal(1,"publication native prepared bank mismatch after NBA");
  end
  $fdisplay(pubcmp_file,"BANK %0d %0t %h %h",cycles,$time,
   {dut.state,dut.configured,dut.stopped,dut.error_code,dut.elapsed,dut.current_version,dut.tx_version,
    dut.descriptor,dut.prepared,dut.shadow_payload,dut.shadow_design,dut.shadow_checkpoint},
   {publish_ready,discard_ready,staged_valid,staged_design,staged_checkpoint,staged_version,
    active_version,staged_payload,active_payload,load_ready,load_rsp_valid,load_status,start_ready,
    cfg_valid,cfg_payload,cfg_rsp_ready,rsp_valid,rsp_status,rsp_cookie,busy,fault,sent,retired,saved_design,saved_checkpoint});
  $fflush(pubcmp_file);
 end
'''


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def instrument(text, native, mode):
    assert 'pubcmp_' not in text and 'PUBCMP_' not in text
    name = 'tb_config_native_feedback_v1' if native else 'tb_config_publication_probe_v1'
    module = 'module '+name+';'
    assert text.count(module) == text.count('\nendmodule') == 1
    instance = 'config_restore_controller #(.MAX_CYCLES(256)) dut('
    assert text.count(instance) == 1
    declarations = DECLARATIONS + f' localparam integer PUBCMP_NATIVE={int(native)};\n'
    observed = text.replace(module,module+declarations).replace('\nendmodule',OBSERVATION+'\nendmodule')
    recovered = observed.replace(module+declarations,module).replace(OBSERVATION+'\nendmodule','\nendmodule')
    assert recovered == text
    assert mode in ['original','default','enabled'] and (native or mode!='enabled')
    if mode!='original':
        value = int(mode=='enabled')
        observed = observed.replace(instance,
            f'config_restore_controller #(.MAX_CYCLES(256),.NATIVE_FEEDBACK_PUBLICATION({value})) dut(')
    return observed, name


def main():
    report = ROOT/'results/config_publication_unit_benches_preparation_20261030.json'
    assert not TARGET.exists() and not report.exists()
    origins = {}
    for native, name, status in [
        (False,'config_publication_probe_preparation_20261030.json','testbench_prepared_not_compiled_or_simulated'),
        (True,'config_native_feedback_testbench_preparation_20261030.json','native_testbench_prepared_not_compiled_or_simulated'),
    ]:
        path=ROOT/'results'/name;p=json.loads(path.read_text());assert p['status']==status
        tb=Path(p['testbench']);assert sha(tb)==p['testbench_sha256']
        origins[native]=(tb,path)
    outputs={};prepared={}
    for native,modes in [(False,['original','default']),(True,['original','default','enabled'])]:
        original=origins[native][0].read_text()
        for mode in modes:
            text,top=instrument(original,native,mode);name=('native' if native else 'generic')+'_'+mode
            assert 'force ' not in OBSERVATION and 'release ' not in OBSERVATION
            prepared[name]=text
            outputs[name]=dict(top=top,source=str(origins[native][0]),source_sha256=sha(origins[native][0]),
                controller='original CP controller' if mode=='original' else 'future candidate controller',
                parameter=None if mode=='original' else int(mode=='enabled'),native_contract_observed=native)
    # No candidate source is imported, transformed, or written by this tool.
    TARGET.mkdir()
    for name,text in prepared.items():
        path=TARGET/(name+'.sv');path.write_text(text)
        outputs[name].update(testbench=str(path),testbench_sha256=sha(path))
    bound=[Path(__file__).resolve()]+[p for pair in origins.values() for p in pair]
    report.write_text(json.dumps(dict(status='five_observation_unit_benches_prepared_not_compiled_or_simulated',
        bound={str(p):sha(p) for p in bound},cases=outputs,
        exact_comparisons=[['generic_original','generic_default'],['native_original','native_default'],['native_original','native_enabled']],
        trace_contract='Every positive edge sampled100ps after NBA, before existing tick #1. Entire internal descriptor/shadow/control state and all declared output ports are recorded verbatim, including X/Z. Compare complete trace/event bytes and finish times.',
        native_contract='Actual accepted-stage payload aliases active payload; complete2272 non-version prepared bits match before and after NBA.',
        original_stimulus_unchanged=True,production_candidate_generated=False,new_solver_started=False,
        scope='Verification-only preparation. Candidate generation remains gated on actual restored original generic/native probes. No SV compile, simulation, full RTL equivalence, physical measurement or acceptance.'),indent=2,sort_keys=True)+'\n')
    print('CONFIG_PUBLICATION_UNIT_BENCHES_PREPARED',len(outputs),'NO_CANDIDATE_RTL')


if __name__=='__main__':
    main()
