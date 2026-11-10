"""Audit terminal read-only DCP diagnostics; explicitly retain design rejection."""
from pathlib import Path
from collections import Counter
import json,re,subprocess,sys
from run_checkpoint_authority import sha

def audit(p):
    p=Path(p).resolve();d=p/'results'/'methodology_v1'
    m=json.loads((d/'manifest.json').read_text())
    assert m['status']=='observed'and m['exit_code']==0
    for n,h in m['input_sha256'].items():assert sha(p/n)==h,n
    for n,h in m['artifacts'].items():assert sha(d/n)==h,n
    assert sha(d/'runner.py')==m['runner_sha256']and sha(d/'inspect.tcl')==m['tcl_sha256']
    log=(d/'vivado.log').read_text()
    assert 'RESTORE_SEED_DIAGNOSTICS_DONE'in log and 'VIVADO_VERSION 2022.2'in log
    assert not re.search(r'^ERROR:',log,re.M)
    helper=Path(__file__).with_name('read_tcl_list_records.tcl')
    def records(name):
        out=subprocess.run(['tclsh',str(helper),str(d/name)],check=True,capture_output=True,text=True)
        return [[bytes.fromhex(x).decode()for x in l.split('\t')]for l in out.stdout.splitlines()]
    def objects(name):
        out=[]
        for r in records(name):
            if r[0]=='OBJECT':
                assert len(r)==2;out.append({'object':r[1],'properties':{}})
            else:
                assert r[0]=='PROPERTY'and len(r)==3 and out
                assert r[1]not in out[-1]['properties']
                out[-1]['properties'][r[1]]=r[2]
        return out
    methods=objects('methodology_objects.tcllist');loops=objects('loop_objects.tcllist')
    for v in methods+loops:
        assert v['properties']['IS_WAIVED']=='0'
    method_counts=dict(sorted(Counter(v['properties']['CHECK']for v in methods).items()))
    summary={rule:int(count)for rule,count in re.findall(r'^\|\s*(\S+)\s*\|[^\n]+?\|\s*(\d+)\s*\|\s*$',(d/'methodology.rpt').read_text(),re.M)}
    assert method_counts==summary,(method_counts,summary)
    elements={};current=None
    for r in records('loop_elements.tcllist'):
        if r[0]=='VIOLATION':assert len(r)==2;current=r[1];elements[current]={}
        else:
            assert current and r[0]in ['CELLS','NETS','PINS']
            elements[current][r[0]]=r[1:]
    assert set(elements)=={v['object']for v in loops}
    for v in loops:
        assert v['properties']['CHECK']=='LUTLP-1'
        count=re.search(r'^(\d+) LUT cells form a combinatorial loop',v['properties']['DESCRIPTION'])
        assert count
        cells=elements[v['object']]['CELLS']
        assert len(cells)==len(set(cells))==int(count[1])
    paths=objects('timing_path_objects.tcllist')
    assert paths and all(v['properties']['GROUP']=='core_clk'for v in paths)
    xdc=(d/'effective.xdc').read_text()
    assert 'create_clock -period 10.000 -name core_clk [get_ports clk]'in xdc
    # Exported user constraints do not contain Vivado's internal loop cuts;
    # lack of a textual false path must not be interpreted as no timing cuts.
    assert not re.search(r'^(set_false_path|create_waiver|.*ALLOW_COMBINATORIAL_LOOPS)',xdc,re.M)
    result=dict(status='passed',audit_kind='diagnostic provenance and literal observations',
        design_acceptance='rejected_combinational_loops'if loops else'unresolved',timing_qualified=False,
        manifest_sha256=sha(d/'manifest.json'),auditor_sha256=sha(Path(__file__)),parser_sha256=sha(helper),
        methodology_counts=method_counts,loop_violations=loops,loop_elements=elements,timing_paths=paths,
        effective_xdc_sha256=sha(d/'effective.xdc'),
        scope='No waivers applied. DRC groups and check_timing loop counts are distinct report units. Missing OOC IO timing remains unspecified; automatic synthesis loop cuts may not be exported in effective XDC. Timing is pre-placement only.')
    (p/'diagnostic_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    return result

if __name__=='__main__':
    r=audit(sys.argv[1]);print('DIAGNOSTICS_AUDITED',r['design_acceptance'],r['methodology_counts'],[len(v['CELLS'])for v in r['loop_elements'].values()])
