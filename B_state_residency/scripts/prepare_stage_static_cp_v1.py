"""Isolate stage write factoring on CP, preserving the observed failure baseline."""
import ast
import json
from host_edit_system_common_v1 import ROOT,BASE,sha,read,restored,verify_freeze


def main():
    failure=ROOT/'results/stage_export_functional_mismatch_20261030.json'
    assert read(failure)['functional_acceptance'] is False
    verify_freeze(ROOT/'results/stage_export_functional_mismatch_sources_20261030')
    reference=BASE/'checkpoint_edit_synth_v1'
    m,a,_=restored(reference)
    original=reference/'sources/route_commit_controller.sv'
    assert sha(original)==m['sources']['route_commit_controller.sv']
    old=original.read_text();text=old
    token='parameter integer PATH_SLOTS=2,'
    assert text.count(token)==1
    text=text.replace(token,'parameter integer STATIC_STAGE_WRITES=0,PATH_SLOTS=2,',1)
    start=text.index('      for(a=0;a<PATH_SLOTS;a=a+1)begin\n       cp_stage')
    end=text.index('      cp_state<=CP_VERIFY;',start)
    capture=text[start:end];assert capture.count('cp_stage[')==8
    text=text[:start]+'      if(STATIC_STAGE_WRITES==0)begin\n'+capture+'      end\n'+text[end:]
    write='cp_stage[cp_pos]<=cp_s_data;';assert text.count(write)==1
    text=text.replace(write,'if(STATIC_STAGE_WRITES==0)'+write,1)
    prior=ROOT/'hardware/variants/route_stage_write_v1/build.py'
    strings=[n.value for n in ast.walk(ast.parse(prior.read_text())) if isinstance(n,ast.Constant)
             and isinstance(n.value,str) and 'reg sw_capture,sw_import;' in n.value]
    assert len(strings)==1 and 'endgenerate' in strings[0]
    extra=strings[0].replace('FACTORED_STAGE_WRITES','STATIC_STAGE_WRITES')
    assert 'FACTORED_PATH_WRITES' not in extra and text.count('endmodule')==1
    text=text.replace('endmodule',extra+'endmodule',1)
    out=ROOT/'hardware/variants/stage_static_cp_v1';assert not out.exists();out.mkdir()
    (out/'baseline.sv').write_text(old);(out/'fixed.sv').write_text(text)
    (out/'CONTRACT.md').write_text('''# Isolated CP stage write experiment

Default STATIC_STAGE_WRITES=0 retains the old writer. Enabled mode uses the
previous nested capture/import control tree with static per-word processes.
No path, route-label, or native-publication changes are included. No new reset
initialization, state or cycle is added. CRC, cancellation, drift, stream index,
last-word validation and publication remain unchanged.

This is a structural diagnostic candidate, not a selected fix. Compare original
and enabled RTL and functional netlists under the unchanged import/reset/export
probe. A passing narrow probe does not replace checkpoint unit, full-system,
four-state, parameter, or matched timing validation.
''')
    bound={str(p):sha(p) for p in [original,prior,failure]}
    (out/'manifest.json').write_text(json.dumps(dict(status='prepared_not_validated',bound=bound,
        reference=str(reference),reference_audit_sha256=sha(reference/'source_bound_audit.json'),
        baseline_sha256=sha(out/'baseline.sv'),fixed_sha256=sha(out/'fixed.sv'),
        generator_sha256=sha(__file__),only_stage_factoring=True,default_enabled=False,
        behavioral_equivalence_proven=False,timing_qualified=False),indent=2,sort_keys=True)+'\n')
    print('ISOLATED_STATIC_STAGE_CP_PREPARED')


if __name__=='__main__':main()
