"""Static observer/source checks and current gate rejection, never RTL execution."""
from pathlib import Path
import ast
import hashlib
import json
import re
from host_edit_system_common_v1 import ROOT,BASE,sha,read,load,restored


def main():
    builder=ROOT/'hardware/variants/config_native_publication_system_v1/build.py'
    b=load('native_system_static_preflight',builder)
    baseline=BASE/'query_host_edit_system_v1';rm,ra,files=restored(baseline)
    ctrl=b.CANDIDATE/'baseline/config_restore_controller.sv';tb=baseline/'sources/tb_query_fault.sv'
    assert sha(tb)==rm['sources']['tb_query_fault.sv']['sha256']
    assert sha(ctrl)==sha(baseline/'sources/config_restore_controller.sv')
    original=tb.read_text();controller=ctrl.read_text()
    parsed=b.ports(controller);generated=b.instrument(original,controller);model=b.reference_source(controller)
    body=controller.split('\n);',1)[1];body=re.sub(r'\bfunction\b.*?\bendfunction\b','',body,flags=re.S)
    registers={}
    for match in re.finditer(r'\breg\s*(\[[0-9]+:[0-9]+\])?\s*([^;]+);',body):
        width=1 if not match[1] else int(match[1][1:].split(':')[0])-int(match[1].split(':')[1][:-1])+1
        for name in match[2].split(','):
            name=name.strip();assert re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*',name);registers[name]=width
    assert set(registers)==set(b.STATE)|{'error_reply'}
    assert sum(registers[name] for name in b.STATE)==4810
    assert 'always @*begin error_reply=0;' in controller
    def wiring(text):
        for direction,width,name in parsed:
            if direction=='output':expected='np_'+name
            elif name=='load_payload':expected=b.DUT+'.load_stage?np_active_payload:'+b.DUT+'.load_payload'
            else:expected=b.DUT+'.'+name
            assert text.count('.'+name+'('+expected+')')==1,('observer port',name)
        state='{'+','.join(b.DUT+'.'+name for name in b.STATE)+'}'
        reference='{'+','.join('np_reference.'+name for name in b.STATE)+'}'
        assert state+'!=='+reference in text
        actual='{'+','.join(b.DUT+'.'+name for d,w,name in parsed if d=='output')+'}'
        reference='{'+','.join('np_'+name for d,w,name in parsed if d=='output')+'}'
        assert actual+'!=='+reference in text
    wiring(generated)
    rejected=[]
    invalid=[('missing_module',original.replace(b.DECL,''),controller),
             ('duplicate_finish',original+'\n'+b.FINISH,controller),
             ('double_observer',generated,controller),
             ('counter_namespace_collision',original+'\ninteger np_cycles;',controller),
             ('wrong_output_width',original,controller.replace('output wire[2303:0]staged_payload,active_payload,','output wire[2302:0]staged_payload,active_payload,',1)),
             ('unsupported_default_port',original,controller.replace('input wire clk,','input wire clk=1,',1))]
    for name,text,source in invalid:
        try:b.instrument(text,source)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    for name,text in [
        ('output_drives_actual_dut',generated.replace('.publish_ready(np_publish_ready)', '.publish_ready('+b.DUT+'.publish_ready)',1)),
        ('observer_uses_candidate_stage_payload',generated.replace('.load_payload('+b.DUT+'.load_stage?np_active_payload:'+b.DUT+'.load_payload)', '.load_payload('+b.DUT+'.load_payload)',1)),
        ('state_logical_inequality_hides_xz',generated.replace('}!=={np_reference.state','}!={np_reference.state',1)),
        ('output_logical_inequality_hides_xz',generated.replace('}!=={np_publish_ready','}!={np_publish_ready',1)),
    ]:
        try:wiring(text)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    for name,text in [('double_module_source',controller+'\n'+controller),('already_renamed_model',model)]:
        try:b.reference_source(text)
        except AssertionError:rejected.append(name)
        else:raise AssertionError(name)
    try:b.sources(b.REFERENCE)
    except AssertionError as error:assert str(error)=='Wait for five candidate unit modes actual restore/freeze'
    else:raise AssertionError('Missing unit acceptance was not rejected')
    target=BASE/'config_native_publication_system_v1';assert not target.exists()
    toolfiles=[ROOT/'scripts'/name for name in b.TOOLS]+[builder]
    for file in toolfiles+[Path(__file__).resolve()]:ast.parse(file.read_text())
    out=ROOT/'results/config_native_publication_system_tools_preparation_20261030.json';assert not out.exists()
    bound=files+[tb,ctrl,Path(__file__).resolve()]
    report=dict(status='native_publication_full_system_tools_prepared_not_executed',
        tools={str(file):sha(file) for file in toolfiles},preflight_bound={str(file):sha(file) for file in bound},
        malformed_source_and_observer_rejections=rejected,ports=parsed,state_register_widths=registers,
        output_ports=25,input_ports=26,state_bits=4810,output_bits=7238,
        generated_observer_tb_sha256=hashlib.sha256(generated.encode()).hexdigest(),
        original_controller_model_sha256=hashlib.sha256(model.encode()).hexdigest(),
        actual_early_gate='Missing accepted/restored five-unit report rejected before CP reference root access or target creation.',
        observer_feedback='Own reference active_payload for stage; real actual host payload for non-stage. Outputs never drive DUT.',
        generated_source_written=False,new_solver_started=False,
        scope='Static complete-port/registered-state coverage, reversible verification-only insertion, original source module-rename only,12 corrupted source/observer examples and actual missing-unit gate. No SV compile, candidate full-system behavior, comparator runtime validation, timing or physical result.')
    assert len(rejected)==12
    out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('NATIVE_SYSTEM_TOOLS_PREFLIGHT',len(toolfiles),'tools',len(parsed),'ports',len(rejected),'rejections; NO RTL RUN')


if __name__=='__main__':main()
