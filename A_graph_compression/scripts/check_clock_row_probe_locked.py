#!/usr/bin/env python3
"""Audit the fixed clock probe in a fully Vivado-routed surrounding design."""
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from netlist import read_snapshot
from packed_graph import PackedGraph
from check_netlist_quality import route_status,drc_status,timing_status
from real_experiment import write_new
from check_clock_row_mapping import digest


def main():
    input_path=ROOT/'results/clock_row_probe_input_20261023_v1.json';request=json.loads(input_path.read_text())
    for name,value in request['files'].items():
        if digest(ROOT/name)!=value:raise ValueError('Probe input changed')
    baseline=ROOT/'data/netlist/routeracc_cost_u280_20261022_v1'
    isolated=ROOT/'data/netlist/clock_row_route_probe_20261023_v1'
    full=ROOT/'data/netlist/clock_row_route_probe_full_20261023_v2'
    before=read_snapshot(baseline/'snapshot.tsv');after=read_snapshot(full/'snapshot.tsv')
    selected={line.split('\t')[1] for line in (ROOT/'data/derived/region_all_nets_cap8_20261022_v1/candidate_routes.tsv').read_text().splitlines() if line.startswith('net\t')}
    failures=[]
    if before['cells']!=after['cells']:failures.append('Cell placement/reference changed')
    if set(before['nets'])!=set(after['nets']):raise ValueError('Net domain changed')
    def sorted_value(v):return sorted(v,key=lambda x:json.dumps(x,sort_keys=True)) if isinstance(v,list) else v
    for name,old in before['nets'].items():
        new=after['nets'][name]
        for key in ('type','segments','site_pins','leaf_pins'):
            if sorted_value(old[key])!=sorted_value(new[key]):failures.append('Connectivity changed: '+name+'/'+key)
        if name not in selected:
            for key in ('nodes','pips','status','fixed'):
                if sorted_value(old[key])!=sorted_value(new[key]):failures.append('Protected net changed: '+name+'/'+key)
    manifest_path=ROOT/'data/derived/native_site_csr_inputs_20261023_v1/manifest.json';manifest=json.loads(manifest_path.read_text())
    image_path=Path(manifest['image'])
    if digest(image_path)!=manifest['files'][str(image_path)]:raise ValueError('Image changed')
    image=PackedGraph(image_path)
    expected_pips=[image.text(image.tiles[e[2]][0])+'/'+image.text(e[3]) for e in request['numeric_edges']]
    actual=after['nets'][request['net']]
    if set(actual['nodes'])!=set(request['nodes']) or set(actual['pips'])!=set(expected_pips) or actual['status']!='ROUTED':
        failures.append('Fixed probe path/readback differs')
    configs={};used={}
    for line in (isolated/'configuration.tsv').read_text().splitlines():
        f=line.split('\t')
        if f[0]=='config' and not f[3].endswith(('.DEFAULT','.VALUES')):configs.setdefault(f[1],{})[f[2]+'/'+f[3]]=f[4]
        if f[0]=='site_pin':used.setdefault(f[1],{})[f[2]]=f[3]=='1'
    changes={key:{'baseline':configs['baseline'][key],'unrouted':configs['unrouted'][key],'applied':value}
             for key,value in configs['applied'].items() if value!=configs['baseline'][key]}
    def quality(folder):return {'route':route_status(folder/'route_status.rpt'),'drc':drc_status(ROOT/'results/netlist_baseline_drc_20261022.rpt' if folder==baseline else folder/'drc.rpt'),'timing':timing_status(folder/'timing_summary.rpt')}
    b=quality(baseline);c=quality(full)
    if c['route']['routable nets']!=c['route']['fully routed nets'] or c['route']['nets with routing errors']:
        failures.append('Not all routable nets are cleanly routed')
    new_drc={k:v for k,v in c['drc']['issues'].items() if k not in b['drc']['issues'] or v['count']>b['drc']['issues'][k]['count']}
    if new_drc:failures.append('New/increased DRC issues')
    full_configs={}
    for line in (full/'configuration.tsv').read_text().splitlines():
        f=line.split('\t')
        if f[0]=='config' and not f[3].endswith(('.DEFAULT','.VALUES')):full_configs[f[2]+'/'+f[3]]=f[4]
    def pins(path):
        records={};complete=None
        for line in path.read_text().splitlines():
            f=line.split('\t')
            if f[0]=='cell':
                if len(f)!=8 or f[1] in records:raise ValueError('Invalid pin record')
                records[f[1]]=f[2:]
            elif f[0]=='complete':complete=int(f[1])
            else:raise ValueError('Unexpected mapping record')
        if complete!=len(records):raise ValueError('Incomplete pin mapping')
        return records
    baseline_pins=pins(full/'lut_pins_baseline.tsv');isolated_pins=pins(full/'lut_pins_isolated.tsv');routed_pins=pins(full/'lut_pins_routed.tsv')
    if baseline_pins!=isolated_pins:failures.append('Isolated LUT mapping/state differs from baseline')
    if set(baseline_pins)!=set(routed_pins):failures.append('LUT domain changed')
    else:
        for name,old in baseline_pins.items():
            new=routed_pins[name]
            if old[:-1]!=new[:-1] or sorted(new[-1].split())!=sorted(old[-2].split()):failures.append('LUT mapping/INIT/lock differs: '+name)
    report={'locked_lut_cells':len(baseline_pins),'status':'full_context_probe_readback_and_drc_passed' if not failures else 'probe_validation_failed',
        'net':request['net'],'expected_pips':expected_pips,'pseudo_instances':request['pseudo_pips'],'sites':request['sites'],
        'failures':failures,'protected_net_groups':len(before['nets'])-len(selected),'cells':len(before['cells']),
        'configuration_changes_in_isolated_stage':changes,'isolated_site_pin_usage':used,
        'full_context_configuration':full_configs,'full_context_configuration_changed_from_isolated':{k:v for k,v in full_configs.items() if configs['applied'].get(k)!=v},'baseline_quality':b,'full_probe_quality':c,'new_drc':new_drc,
        'limitations':['Surrounding 1061 signal nets were rerouted by Vivado; this is a configuration probe, not the compression router workload.',
            'Two pseudo instances share this path; this does not certify a family rule, complete constant/inversion semantics or dynamic ownership.',
            'IS_USED is not an availability or implicit intra-site ownership oracle.']}
    paths=[input_path,Path(__file__),manifest_path,image_path,isolated/'configuration.tsv',
           full/'configuration.tsv',ROOT/'adapters/capture_clock_row_full_config_20261023_v2.tcl',ROOT/'adapters/probe_clock_row_route_20261023_v1.tcl',ROOT/'adapters/complete_clock_row_probe_20261023_v2.tcl']
    for folder in (baseline,full):paths.extend(folder/name for name in ('snapshot.tsv','route_status.rpt','timing_summary.rpt','routed.dcp'))
    paths.extend(full/name for name in ('lut_pins_baseline.tsv','lut_pins_isolated.tsv','lut_pins_routed.tsv'))
    paths.extend([ROOT/'results/netlist_baseline_drc_20261022.rpt',full/'drc.rpt'])
    report['files']={str(p):digest(p) for p in paths}
    write_new(full/'verification.json',report);print(json.dumps({k:report[k] for k in ('status','failures','configuration_changes_in_isolated_stage','new_drc')}))


if __name__=='__main__':main()
