#!/usr/bin/env python3
"""Independently audit tile-cache RTL outputs and, when ready, matched baseline cycles."""
import argparse
import json
from pathlib import Path
import re
from check_vitis_kernel import digest, require, validate_case_log

ROOT=Path(__file__).resolve().parents[1]


def audit(bundle, baseline=None):
    plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text())
    for path,sha in plan['files'].items():require(digest(path)==sha,'Frozen candidate changed: '+path)
    source=Path(plan['source']);project=Path(plan['project'])
    receipt=bundle/'receipt.json';log=bundle/'cosim.log';r=json.loads(receipt.read_text());text=log.read_text()
    require(r['exit_code']==0 and r['log_sha256']==digest(log),'Cosim receipt failed or changed')
    require('VITIS_STRATIFIED_COSIM_COMPLETE' in text and 'ERROR:' not in text,'Cosim failed')
    cases=validate_case_log(text,source/'rtl.txt',2)
    require(len(cases)==12,'Unexpected RTL case count')
    old=Path(plan['synthesized_project'])/'solution/syn/verilog';new=project/'solution/syn/verilog'
    originals={p.name:p for p in old.glob('*.v')};copies={p.name:p for p in new.glob('*.v')}
    require(originals and originals.keys()==copies.keys(),'RTL set changed')
    files={str(p):digest(p) for p in [plan_path,receipt,log,Path(__file__).resolve(),bundle/'copied_project.json']}
    for name in originals:
        require(digest(originals[name])==digest(copies[name]),'Copied RTL changed')
        files[str(copies[name])]=digest(copies[name])
    cosim=project/'solution/sim/report/graph_accel_cosim.rpt'
    trans=project/'solution/sim/report/verilog/result.transaction.rpt'
    require(re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()),'No passing RTL report')
    pairs=[(int(i),int(c)) for i,c in re.findall(r'^transaction\s+(\d+):\s+(\d+)',trans.read_text(),re.M)]
    require([i for i,c in pairs]==list(range(12)) and all(c>0 for i,c in pairs),'Invalid transactions')
    for case,(_,cycles) in zip(cases,pairs):case.update(label=Path(case['case']).stem,cycles=cycles)
    for p in [cosim,trans]:files[str(p)]=digest(p)
    report={'status':'tile_cache_rtl_golden_verified','files':files,'cases':cases,
            'limitations':['RTL AXI model only; no routed timing for this candidate and no board measurement.',
                           'Degree strata are diagnostic, not full-router access weights.']}
    if baseline is not None:
        base=json.loads(baseline.read_text())
        require(base['status']=='stratified_golden_and_unchanged_rtl_verified','Baseline audit not complete')
        for path,sha in base['files'].items():require(digest(path)==sha,'Baseline audit artifact changed')
        before=base['modes']['compact'];require(len(before)==len(cases),'Baseline cases differ')
        comparison=[]
        for b,a in zip(before,cases):
            require(all(b[k]==a[k] for k in ['case','requests','records','failed','label']),
                    'Candidate does not use identical baseline stimuli')
            comparison.append({'label':a['label'],'baseline_cycles':b['cycles'],'tile_cache_cycles':a['cycles'],
                               'tile_cache_over_baseline':a['cycles']/b['cycles'],
                               'reduction_fraction':1-a['cycles']/b['cycles']})
        report.update(status='tile_cache_matched_rtl_comparison_verified',comparisons=comparison)
        files[str(baseline)]=digest(baseline)
    return report


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True)
    p.add_argument('--output',type=Path,required=True);p.add_argument('--baseline',type=Path)
    a=p.parse_args();report=audit(a.bundle.resolve(),a.baseline)
    with a.output.open('x') as stream:json.dump(report,stream,indent=2);stream.write('\n')
    print(json.dumps({'status':report['status'],'cases':report['cases'],'comparisons':report.get('comparisons')}))


if __name__=='__main__':main()
