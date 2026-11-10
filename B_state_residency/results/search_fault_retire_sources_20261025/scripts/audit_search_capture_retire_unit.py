"""Bind executed capture protocol assertions and independently count all outcomes."""
from pathlib import Path
import json,sys,importlib.util
from run_query_fault import ROOT,sha
def main():
    p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
    for n,v in m['sources'].items():assert sha(p/'sources'/n)==v['sha256']
    for n,h in m['artifacts'].items():assert sha(p/n)==h
    assert sha(p/'runner.py')==m['runner_sha256']
    b=ROOT/'hardware/variants/search_fault_retire_v1/build.py';sp=importlib.util.spec_from_file_location('retire_builder',b);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);built=mod.make()
    for n in ['children_frames.sv','expansion_capture.sv']:assert (p/'sources'/n).read_text()==built['capture/'+n]
    assert (p/'sources/tb_expansion_capture_unit.sv').read_bytes()==(ROOT/'hardware/variants/search_fault_retire_v1/tb_expansion_capture_unit.sv').read_bytes()
    log=(p/'simulate.log').read_text();assert 'Fatal:' not in log and '$finish called' in log
    events=[l.split() for l in log.splitlines()]
    assert [int(t[1]) for t in events if t and t[0]=='ERROR_RETIRED']==[30,50,40,60,70,80,90,100,120]
    assert [t[1:] for t in events if t and t[0]=='ITEM']==[['10','1'],['20','3'],['10','2']]
    assert [t[1:] for t in events if t and t[0]=='RESULT']==[['20','1'],['10','2']]
    assert 'SEARCH_CAPTURE_RETIRE_PASS normal_nested=1 failures=9' in log
    result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'audit_script_sha256':sha(Path(__file__)),
            'builder_sha256':sha(b),'scope':'Normal nested replay plus nine fault/cancel/overflow/bad-identity/held-reply scenarios. Error frame unwind does not replace physical producer retirement. Model evidence, not graph-data performance.',
            'error_completions':9,'normal_results':2,'normal_items':3}
    (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
