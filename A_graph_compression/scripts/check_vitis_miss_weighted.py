#!/usr/bin/env python3
"""Audit matched weighted RTL requests, golden results and unchanged synthesized RTL."""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest,require,validate_case_log
ROOT=Path(__file__).resolve().parents[1]

def audit(bundle):
    plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text())
    for path,sha in plan['files'].items():require(digest(path)==sha,'Frozen dependency changed: '+path)
    fixture=json.loads(Path(plan['fixture_plan']).read_text());expected=fixture['cases']
    files={str(plan_path):digest(plan_path),str(Path(__file__).resolve()):digest(__file__)};results={}
    for label,entry in plan['runs'].items():
        work=bundle/label;log=work/'cosim.log';receipt_path=work/'receipt.json';receipt=json.loads(receipt_path.read_text());text=log.read_text()
        require(receipt['exit_code']==0 and digest(log)==receipt['log_sha256'],'Cosim receipt failed')
        require('VITIS_STRATIFIED_COSIM_COMPLETE' in text and 'ERROR:' not in text,'Cosim did not complete')
        cases=validate_case_log(text,Path(entry['manifest']),2)
        require(len(cases)==len(expected),'Incomplete cases')
        old=Path(entry['original'])/'solution/syn/verilog';new=Path(entry['project'])/'solution/syn/verilog'
        originals={p.name:digest(p) for p in old.glob('*.v')};copies={p.name:digest(p) for p in new.glob('*.v')}
        require(originals and originals==copies,'Synthesized RTL changed')
        report=Path(entry['project'])/'solution/sim/report/graph_accel_cosim.rpt'
        transactions=report.parent/'verilog/result.transaction.rpt'
        require(re.search(r'Verilog\s*\|\s*Pass',report.read_text()),'RTL report not passing')
        pairs=[(int(i),int(c)) for i,c in re.findall(r'^transaction\s+(\d+):\s+(\d+)',transactions.read_text(),re.M)]
        require([i for i,c in pairs]==list(range(len(expected))) and all(c>0 for i,c in pairs),'Transactions incomplete')
        for case,sample,(_,cycles) in zip(cases,expected,pairs):
            require(Path(case['case']).stem==sample['label'] and case['requests']==len(sample['nodes']) and case['records']==sample['sample_edges'] and case['failed']==0,'Sample identity/count differs')
            case.update(label=sample['label'],cycles=cycles)
        results[label]=cases
        for p in [log,receipt_path,report,transactions,work/'copied_project.json']+list(new.glob('*.v')):files[str(p)]=digest(p)
    comparisons=[]
    for csr,compact,candidate in zip(results['csr'],results['compact'],results['tile_cache']):
        require(all(csr[k]==compact[k]==candidate[k] for k in ['label','requests','records','failed']),'Unmatched cases')
        require(compact['case']==candidate['case'],'Candidate golden input differs')
        comparisons.append({'label':csr['label'],'csr_cycles':csr['cycles'],'compact_cycles':compact['cycles'],'tile_cache_cycles':candidate['cycles'],
                            'tile_cache_over_csr':candidate['cycles']/csr['cycles'],
                            'tile_cache_reduction_from_compact':1-candidate['cycles']/compact['cycles']})
    return {'status':'matched_known_miss_weighted_rtl_verified','files':files,'runs':results,'comparisons':comparisons,'limitations':fixture['limitations']+['HLS AXI simulation only; no physical DDR/HBM or host launch measurement.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=audit(a.bundle.resolve())
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'comparisons':report['comparisons']},indent=2))
if __name__=='__main__':main()
