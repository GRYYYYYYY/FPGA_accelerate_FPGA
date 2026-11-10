#!/usr/bin/env python3
"""Audit the completed bounded netlist-routing and hardware-decoder stage."""
import argparse
from datetime import datetime,timezone
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from canonical_graph import validate
from import_vivado import read_export,sha256
from netlist import read_snapshot
from netlist_routing import validate_routes
from real_experiment import write_new
from check_netlist_readback import check
from check_netlist_quality import compare_quality,drc_status,route_status,timing_status


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv);paths=[]
    def load(path):
        path=ROOT/path;paths.append(path);return json.loads(path.read_text())
    capture=load('data/raw/netlist_u280_20261022_v1/capture.json')
    for entry in capture['files'].values():
        if sha256(ROOT/entry['path'])!=entry['sha256']:raise ValueError('Capture changed: '+entry['path'])
    primary=load('data/derived/netlist_all_nets_20261022_v1/report.json')
    control=load('data/derived/netlist_all_nets_exp22_20261022_v1/report.json')
    capped=load('data/derived/netlist_all_nets_cap8_20261022_v1/report.json')
    cmodel=load('data/derived/netlist_cmodel_cap8_20261022_v1/report.json')
    hardware=load('results/hls_u280_check_20261022_v1.json')
    queries=load('data/derived/netlist_all_nets_cap8_20261022_v1/queries.json')
    graph=read_export(ROOT/'data/raw/netlist_u280_20261022_v1/reference_domain.tsv');validate(graph)
    before=read_snapshot(ROOT/'data/netlist/routeracc_cost_u280_20261022_v1/snapshot.tsv')
    reference=None;route_checks={}
    for label,directory in [('csr','netlist_all_nets_cap8_20261022_v1'),('templates','netlist_all_nets_cap8_20261022_v1'),
                            ('cmodel_csr','netlist_cmodel_cap8_20261022_v1'),('cmodel_compact','netlist_cmodel_cap8_20261022_v1')]:
        stem=label.removeprefix('cmodel_');r=load('data/derived/'+directory+'/'+stem+'_routes.json')
        route_checks[label]=validate_routes(graph,before,queries,r)
        if not route_checks[label]['all_nets_routed_without_conflicts']:raise ValueError('Incomplete/illegal routing')
        normalized={k:v for k,v in r.items() if k!='wall_ms'}
        if reference is None:reference=normalized
        elif reference!=normalized:raise ValueError('Routing traces/trees/occupancy differ')
    applied=ROOT/'data/netlist/all_nets_cap8_applied_20261022_v1'
    after=read_snapshot(applied/'snapshot.tsv')
    readback=check(before,after,reference['routes'])
    def quality(directory,drc):
        return {'route':route_status(directory/'route_status.rpt'),'drc':drc_status(drc),
                'timing':timing_status(directory/'timing_summary.rpt')}
    old_dir=ROOT/'data/netlist/routeracc_cost_u280_20261022_v1'
    old_quality=quality(old_dir,ROOT/'results/netlist_baseline_drc_20261022.rpt')
    new_quality=quality(applied,applied/'drc.rpt')
    quality_check=compare_quality(old_quality,new_quality)
    if not quality_check['quality_gates_pass']:raise ValueError('Readback quality gates failed')
    if primary['checks']['csr']['all_nets_routed_without_conflicts'] or control['checks']['csr']['all_nets_routed_without_conflicts']:
        raise ValueError('Recorded negative controls unexpectedly changed')
    if not hardware['both_internal_timing_met'] or not hardware['both_fully_routed']:
        raise ValueError('Hardware implementation gates failed')
    regression=ROOT/'results/regression_20261022_cap8_v1.log'
    if 'Ran 58 tests' not in regression.read_text() or not regression.read_text().rstrip().endswith('OK'):
        raise ValueError('Required current regression not complete')
    paths += [p for p in applied.iterdir() if p.is_file()]
    paths += [ROOT/'results/netlist_baseline_drc_20261022.rpt',regression,
              ROOT/'data/derived/hls_u280_fixtures_20261022_v1/manifest.json']
    report={'status':'bounded_netlist_and_decoder_stage_complete','created_utc':datetime.now(timezone.utc).isoformat(),
        'full_goal_complete':False,'graph_summary':capture['summaries'],
        'selection':{'nets':len(queries),'sinks':sum(len(q['sinks']) for q in queries)},
        'controls':{'original20_conflicts':len(primary['checks']['csr']['conflicts']),
                    'original22_conflicts':len(control['checks']['csr']['conflicts']),
                    'cap8_settings':capped['route_settings'],'cap8_iterations':capped['iterations']},
        'route_checks':route_checks,'readback':readback,'quality':{'baseline':old_quality,'candidate':new_quality,'comparison':quality_check},
        'packed_file_bytes':{k:v['file_bytes'] for k,v in capped['layouts'].items()},
        'decoded_cache':capped['cache'],'python_route_ms_diagnostic':capped['route_wall_ms'],
        'cmodel_execution_kinds':{k:v['execution_kind'] for k,v in cmodel['results'].items()},
        'hardware_report':'results/hls_u280_check_20261022_v1.json',
        'hardware_cycle_ratios':hardware['compact_over_csr_cycle_ratios'],
        'artifacts':{str(p.relative_to(ROOT)):sha256(p) for p in paths},
        'remaining':['Independent search domain: current graph is conditioned on reference routes.',
                     'Statistically controlled runtime/cache comparison and larger/independent workload validation.',
                     'Real U280 platform/board DDR-HBM, external IO timing, power and end-to-end measurements.'],
        'limitations':['All selected signal nets rerouted; clocks/constants/OOC external nets remain protected baseline resources.',
                       'C-model means native CPU execution of HLS C++, not FPGA/XRT runtime.',
                       'HLS timing is standalone OOC with generated AXI memory simulation, not board performance.',
                       'Single Python run uses additional decoded-row cache; no CPU speedup claim from that comparison.',
                       'No positive hardware acceleration claim; both original and follow-up negative controls retained.']}
    write_new(args.output,report)
    print(json.dumps({'output':str(args.output),'status':report['status'],'selection':report['selection'],
                      'quality':quality_check,'hardware_cycle_ratios':report['hardware_cycle_ratios']},indent=2));return 0


if __name__=='__main__':raise SystemExit(main())
