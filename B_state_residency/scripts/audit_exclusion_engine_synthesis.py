"""Verify no-loop structural recovery and bind the tested edge-engine netlist."""
from pathlib import Path
from collections import Counter
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    out=ROOT/'results/exclusion_edge_engine_v4_synthesis_20261024'
    sim=ROOT/'results/exclusion_edge_engine_v4_20261024'
    gate=read(sim/'source_bound_audit.json');assert gate['status']=='passed' and gate['manifest_sha256']==sha(sim/'manifest.json')
    assert sha(out/'simulation_audit.json')==sha(sim/'source_bound_audit.json')
    sm=read(sim/'manifest.json')
    for name,spec in sm['sources'].items():assert sha(out/'sources'/name)==spec['sha256']==sha(sim/'sources'/name)
    script=ROOT/'hardware/scripts/synthesize_exclusion_engine_v4.tcl';assert sha(script)==sha(out/script.name)
    assert 'ALLOW_COMBINATORIAL_LOOPS' not in script.read_text()+(out/'research_clock.xdc').read_text()
    receipt=read(out/'completion_receipt.json');assert receipt['exit_code']==0
    log=receipt['output'];assert 'Synth Design complete, checksum: dee28a76' in log and 'EDGE_ENGINE_SYNTH_DONE' in log
    assert not re.search(r'^(ERROR:|CRITICAL WARNING:)',log,re.M)
    assert '0 Critical Warnings and 0 Errors encountered.' in log
    drc=(out/'combinational_loops.rpt').read_text();assert re.search(r'Violations found:\s*0\b',drc)
    timing=(out/'check_timing.rpt').read_text()
    for label in ['no_clock','unconstrained_internal_endpoints','loops','latch_loops']:
        assert f'checking {label} (0)' in timing
    assert 'checking no_input_delay (419)' in timing and 'checking no_output_delay (228)' in timing
    rpt=(out/'utilization.rpt').read_text()
    def number(label):return int(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*(\d+)\s*\|',rpt,re.M)[1])
    resources={k:number(k) for k in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs']}
    assert resources=={'CLB LUTs*':1172,'CLB Registers':2190,'Register as Latch':0,'Block RAM Tile':0,'URAM':0,'DSPs':0}
    bad=ROOT/'results/exclusion_edge_engine_v3_synthesis_20261024'
    bad_gate=read(bad/'simulation_audit.json');assert bad_gate['manifest_sha256']==sha(ROOT/'results/exclusion_edge_engine_v3_20261024/manifest.json')
    bad_drc=(bad/'combinational_loops.rpt').read_text()
    assert re.search(r'Violations found:\s*1\b',bad_drc) and '7 LUT cells form a combinatorial loop' in bad_drc and 'calls/complete' in bad_drc
    bad_receipt=read(bad/'completion_receipt.json');assert bad_receipt['exit_code']==0 and '1 Critical Warnings and 0 Errors encountered.' in bad_receipt['output']
    for name in [n for n in sm['sources'] if n.startswith(('hls32/','adapter/')) and n.endswith(('.v','.sv'))]+['engine/exclusion_edge_controller.sv','engine/exclusion_edge_engine.sv']:
        assert sha(bad/'sources'/name)==sha(out/'sources'/name)
    (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
    artifacts={str(p.relative_to(out)):sha(p) for p in sorted(out.rglob('*')) if p.is_file() and p.name not in ['final_audit.json','audit.stdout.log']}
    warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))
    result={'status':'passed','resources':resources,'combinational_loop_violations':0,
        'negative_loop_violations':1,'negative_report_sha256':sha(bad/'combinational_loops.rpt'),
        'negative_receipt_sha256':sha(bad/'completion_receipt.json'),'elapsed_s':receipt['elapsed_seconds'],
        'warnings':dict(warnings),'io_without_delay':{'input':419,'output':228},
        'artifacts':artifacts,'auditor_sha256':sha(Path(__file__)),
        'scope':'HLS state-reset exclusion + controller + collector + label bridge OOC synthesis. Excludes native storage endpoint, automatic pager, routed timing, platform and board proof.'}
    (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n')
    (bad/'structural_failure_audit.json').write_text(json.dumps({'status':'failed_structural_gate','tool_exit_code':bad_receipt['exit_code'],'loop_violations':1,'report_sha256':sha(bad/'combinational_loops.rpt'),'recovery_final_audit_sha256':sha(out/'final_audit.json')},indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ['status','resources','combinational_loop_violations','negative_loop_violations','elapsed_s','warnings','io_without_delay']},indent=2))
if __name__=='__main__':main()
