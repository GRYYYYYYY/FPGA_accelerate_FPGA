"""Resolve this fixture's conditional localparams and compare all top parameters.

Reject unsupported parameter expressions instead of guessing elaboration.
"""
import json
import re
from host_edit_system_common_v1 import ROOT, BASE, read, sha
from prepare_stage_static_cp_port_schema_v1 import balanced


def defines(argv):
    result=set()
    for i,arg in enumerate(argv):
        if arg in ['--define','-d']:
            value=argv[i+1]
            assert '=' not in value, 'Value macros require explicit support'
            result.add(value)
    return result


def conditional_lines(text, macros):
    stack=[];active=True;result=[]
    for line in text.splitlines():
        match=re.match(r'\s*`(ifdef|ifndef)\s+(\w+)\s*$',line)
        if match:
            decision=match[2] in macros
            if match[1]=='ifndef':decision=not decision
            stack.append((active,decision,False));active=active and decision
        elif re.match(r'\s*`else\s*$',line):
            outer,decision,seen=stack[-1];assert not seen
            stack[-1]=(outer,decision,True);active=outer and not decision
        elif re.match(r'\s*`endif\s*$',line):
            outer,_,_=stack.pop();active=outer
        elif re.match(r'\s*`elsif\b',line):raise ValueError('Unsupported elsif')
        elif active:result.append(line)
    assert not stack
    return '\n'.join(result)


def fixture_parameters(tb, source, macros):
    active=conditional_lines(tb,macros)
    values={}
    for declaration in re.findall(r'\blocalparam\s+([^;]+);',active):
        for item in declaration.split(','):
            match=re.fullmatch(r'\s*(?:integer\s+)?(\w+)\s*=\s*(\d+)\s*',item)
            if match:values[match[1]]=int(match[2])
    beginning=source.index('module query_residency_system')
    default_text,_=balanced(source,source.index('(',beginning))
    defaults={}
    for item in default_text.split(','):
        item=re.sub(r'\bparameter\b|\binteger\b','',item).strip()
        name,expression=map(str.strip,item.split('=',1));defaults[name]=expression
    assert len(defaults)==13
    start=active.index('query_residency_system #(')
    overrides,_=balanced(active,active.index('(',start))
    expressions=dict(re.findall(r'\.(\w+)\(([^()]+)\)',overrides))
    assert len(expressions)==12
    result={}
    for name,default in defaults.items():
        expr=expressions.get(name,default)
        if expr.isdigit():value=int(expr)
        elif expr in values:value=values[expr]
        elif name=='PATH_SLOT_BITS' and expr=='(PATH_SLOTS<=2?1:$clog2(PATH_SLOTS))':
            slots=result['PATH_SLOTS'];value=1 if slots<=2 else (slots-1).bit_length()
        else:raise ValueError('Unsupported parameter '+name+'='+expr)
        result[name]=value
    return result


def main():
    full=BASE/'stage_static_cp_system_v1';synth=BASE/'stage_static_cp_synth_v1'
    fm,sm=read(full/'manifest.json'),read(synth/'manifest.json')
    tb=full/'sources/tb_query_fault.sv';source=synth/'sources/query_residency_system.sv'
    compile=fm['cases']['pressure']['commands'][0]['argv'];macros=defines(compile)
    actual=fixture_parameters(tb.read_text(),source.read_text(),macros)
    differences={k:dict(fixture=v,synthesis=sm['parameters'][k]) for k,v in actual.items() if v!=sm['parameters'][k]}
    assert differences=={'SLOTS':dict(fixture=1,synthesis=32)}
    full_macros=macros-{'PRESSURE'}
    proposed=fixture_parameters(tb.read_text(),source.read_text(),full_macros)
    assert proposed==sm['parameters']
    report=dict(status='pressure_shadow_v1_rejected_parameter_mismatch',
                tb_sha256=sha(tb),top_source_sha256=sha(source),generator_sha256=sha(__file__),
                compile_defines=sorted(macros),fixture_parameters=actual,
                synthesis_parameters=sm['parameters'],differences=differences,
                full_capacity_proposed_defines=sorted(full_macros),
                full_capacity_proposed_parameters=proposed,
                full_capacity_behavioral_reference_executed=False,
                rejected_tools_preparation_sha256=sha(ROOT/'results/stage_static_cp_shadow_system_tools_preparation_20261030.json'),
                rejected_runner='run_stage_static_cp_shadow_system_v1.py',
                actual_shadow_job_created=(BASE/'stage_static_cp_shadow_system_v1').exists(),
                scope='Do not run shadow system v1: PRESSURE selects1 cache slot versus32 in OOC. Existing matched CP OOC comparison remains valid. Build and actually audit a full-capacity host reference before a new shadow runner; do not change frozen v1 tools or claim full gate validation.')
    assert not report['actual_shadow_job_created']
    out=ROOT/'results/stage_static_cp_shadow_parameter_rejection_20261030.json'
    assert not out.exists();out.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    print('PARAMETER_MISMATCH_CONFIRMED',differences,'full-capacity proposal matches13parameters')


if __name__=='__main__':main()
