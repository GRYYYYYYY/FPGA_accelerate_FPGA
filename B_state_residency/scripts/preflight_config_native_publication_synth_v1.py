"""Static OOC provenance/runtime controls; no Vivado or experiment creation."""
from pathlib import Path
import ast
import contextlib
import io
import json
import os
import subprocess
from config_native_publication_synth_common_v1 import (ROOT,TARGET,REFERENCE,PREPARATION,TOOLS,
    sha,read,evidence,runtime_environment,validate_production_rtl,wait_preserving)


def main():
    assert not TARGET.exists() and not PREPARATION.exists()
    for name in TOOLS:
        p=ROOT/'scripts'/name
        if p.suffix=='.py':ast.parse(p.read_text())
    rtl=read(REFERENCE/'manifest.json')['rtl'];validate_production_rtl(rtl)
    rejected=[]
    for name,values in [
        ('missing_production_source',rtl[:-1]),
        ('duplicated_source',rtl[:-1]+[rtl[0]]),
        ('testbench_in_production',rtl[:-1]+['tb_query_fault.sv']),
        ('file_agent_in_production',rtl[:-1]+['axi_file_memory.sv']),
        ('observer_in_production',rtl[:-1]+['config_restore_controller_observer.sv']),
    ]:
        try:validate_production_rtl(values)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    class FakeChild:
        pid=2147483647
        calls=0
        def wait(self,timeout):
            self.calls+=1
            if self.calls<3:raise subprocess.TimeoutExpired('artificial control',timeout)
            return 0
    record=dict(status='running');saves=[];child=FakeChild();captured=io.StringIO()
    with contextlib.redirect_stdout(captured):
        code=wait_preserving(child,1,record,lambda:saves.append(dict(record)))
    assert code==0 and child.calls==3 and record['status']=='observation_timeout' and len(saves)==1
    assert record['observation_timeouts'][0]['pid']==child.pid
    assert 'OBSERVATION_TIMEOUT_CHILD_PRESERVED' in captured.getvalue()
    for name in ['run_config_native_publication_synth_v1.py','inspect_config_native_publication_synth_v1.py','config_native_publication_synth_common_v1.py']:
        text=(ROOT/'scripts'/name).read_text()
        assert not any(token in text for token in ['.kill(','.terminate(','.send_signal(','subprocess.run('])
    old=os.environ.get('LD_PRELOAD');env,runtime=runtime_environment()
    assert os.environ.get('LD_PRELOAD')==old and env['LD_PRELOAD']==runtime['LD_PRELOAD']
    tcl=(REFERENCE/'synth.tcl').read_text();new=tcl.replace(str(REFERENCE),str(TARGET))
    assert new.replace(str(TARGET),str(REFERENCE))==tcl and new.count('read_verilog -sv ')==133
    import re
    reads=re.findall(r'^read_verilog -sv \{([^}]+)\}$',new,re.M)
    assert reads==[str(TARGET/'sources'/name) for name in rtl]
    inspector=ROOT/'scripts/inspect_config_native_publication_synth_v1.py'
    old_inspector=ROOT/'scripts/inspect_restore_seed_synth.py'
    def tcl_section(path):
        text=path.read_text();return text[text.index("tcl='set_param"):text.index("(out/'inspect.tcl').write_text(tcl)")]
    assert tcl_section(inspector)==tcl_section(old_inspector)
    PREPARATION.write_text(json.dumps(dict(status='native_publication_synth_tools_prepared_not_executed',
        tools={str(ROOT/'scripts'/name):sha(ROOT/'scripts'/name) for name in TOOLS},
        preflight_script_sha256=sha(Path(__file__)),
        reused_parser_template_sha256=sha(ROOT/'scripts/audit_route_label_synth.py'),
        reused_diagnostic_tcl_template_sha256=sha(old_inspector),
        rejected_production_lists=rejected,artificial_timeout_control=dict(wait_calls=child.calls,
            eventual_exit_code=code,timeout_record=record,real_process_spawned=False),
        child_runtime=runtime,global_preload_unchanged=True,production_sources=133,
        reference_tcl_sha256=sha(REFERENCE/'synth.tcl'),clock_xdc_sha256=sha(REFERENCE/'clock.xdc'),
        new_experiment_directory_created=False,new_vivado_started=False,
        scope='Python parsing, source-list rejection, original diagnosticTcl equality, path-only OOC Tcl replacement and artificial non-killing timeout control. Existing original-library runtime acceptance verified. No candidate synthesis, DCP, loop/resource/WNS observation or design acceptance.'),indent=2,sort_keys=True)+'\n')
    rm,ra,fm,fa,proof=evidence()
    print('NATIVE_OOC_TOOLS_PREFLIGHT',len(TOOLS),'tools',len(proof),'source bindings',len(rejected),'rejected lists; NO VIVADO RUN')


if __name__=='__main__':main()
