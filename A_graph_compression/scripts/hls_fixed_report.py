#!/usr/bin/env python3
"""Compare completed separate fixed-mode implementations under matched stimuli."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'adapters'),str(ROOT/'src')]
from import_vivado import sha256
from real_experiment import write_new
from check_netlist_quality import drc_status,route_status,timing_status


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--kind',choices=['fixed','u280','region'],default='fixed')
    p.add_argument('--output',type=Path,required=True);args=p.parse_args(argv)
    prefix='hls_'+args.kind
    stamp='20261023_v1' if args.kind=='region' else '20261022_v1'
    bundle=ROOT/'data/derived'/({'fixed':'hls_fixed_modes_20261022_v1',
        'u280':'hls_u280_fixtures_20261022_v1','region':'hls_region_fixtures_20261023_v1'}[args.kind])
    manifest=json.loads((bundle/'manifest.json').read_text())
    for name,digest in manifest['files'].items():
        if sha256(bundle/name)!=digest:raise ValueError('Frozen bundle changed: '+name)
    results={};artifacts={};batches={}
    for variant in ['csr','compact']:
        state_path=ROOT/'results'/(prefix+'_'+variant+'_'+stamp+'.json')
        state=json.loads(state_path.read_text())
        if state['status']!=('complete' if args.kind=='region' else 'completed'):raise ValueError('Fixed '+variant+' is not complete')
        project=ROOT/'build'/(prefix+'_'+variant+'_'+stamp)
        solution=project/'solution'
        synth=solution/'syn/report/graph_expand_csynth.xml'
        cosim=solution/'sim/report/graph_expand_cosim.rpt'
        if not re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()):raise ValueError('RTL failed')
        xml=ET.parse(synth).getroot()
        export=solution/'impl/report/verilog/graph_expand_export.rpt'
        export_text=export.read_text()
        if 'Post-Implementation' not in export_text:raise ValueError('No routed resource report')
        runs=solution/'impl/verilog/project.runs/impl_1'
        timing=runs/'bd_0_wrapper_timing_summary_routed.rpt'
        drc=runs/'bd_0_wrapper_drc_routed.rpt'
        status=solution/'impl/verilog/report/graph_expand_status_routed.rpt'
        results[variant]={'hls_estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
            'axi_data_port_bits':{port.findtext('name'):int(port.findtext('Bits'))
                for port in xml.findall('InterfaceSummary/RtlPorts')
                if port.findtext('name','').endswith(('RDATA','WDATA'))},
            'hls_target_clock_ns':float(xml.findtext('UserAssignments/TargetClockPeriod')),
            'post_route_resources':{k:int(v) for k,v in re.findall(r'^(LUT|FF|DSP|BRAM|URAM|SRL|CLB):\s+(\d+)',export_text,re.M)},
            'timing':timing_status(timing),'drc':drc_status(drc),'route_status':route_status(status)}
        if args.kind=='region':
            synth_step=next(s for s in state['steps'] if s['stage']=='synth')
            log_text=(ROOT/synth_step['log']).read_text()
            observed={}
            for path,requests,records,failed in re.findall(r'CASE_PASS\s+(\S+)\s+requests=(\d+)\s+records=(\d+)\s+failed=(\d+)',log_text):
                label=Path(path).stem
                if label in observed:raise ValueError('Duplicate Csim case '+label)
                observed[label]=(int(requests),int(records),int(failed))
            full={k:v for k,v in manifest['cases'][variant].items() if k.startswith('full_')}
            for label,case in full.items():
                expected=(case['requests'],case['records'],case['failed'])
                if observed.get(label)!=expected:raise ValueError('Incomplete/mismatched full Csim '+label)
            if 'GRAPH_EXPAND_PASS cases='+str(len((bundle/variant/'full.txt').read_text().splitlines())) not in log_text:
                raise ValueError('Full Csim completion count missing')
            results[variant]['complete_csim']={'verified_batches':len(full),
                'node_requests':sum(v['requests'] for v in full.values()),
                'edge_records':sum(v['records'] for v in full.values()),
                'expected_unknown_requests':sum(v['failed'] for v in full.values()),
                'input_capacity_bytes':manifest['image_depth_words']*4}
        trans=solution/'sim/report/verilog/result.transaction.rpt'
        cycles=[int(x) for x in re.findall(r'transaction\s+\d+:\s+(\d+)',trans.read_text())]
        stimuli=(bundle/variant/'rtl.txt').read_text().splitlines()
        if len(cycles)!=len(stimuli):raise ValueError('Fixture/RTL batch count differs')
        for line,latency in zip(stimuli,cycles):
            image,config,case=map(Path,line.split());data=case.read_bytes()
            requests,capacity,records,failed=struct.unpack_from('<4I',data)
            name=case.name.removesuffix('.matched.bin')
            batches[variant+'/'+name]={'requests':requests,'records':records,'expected_status_failures':failed,
                'cycles':latency,'simulated_batch_ms':latency*results[variant]['hls_target_clock_ns']/1e6,
                'request_ids_sha256':hashlib.sha256(data[16:16+requests*4]).hexdigest()}
            for f in [image,config,case]:artifacts[str(f.relative_to(ROOT))]=sha256(f)
        paths=[state_path,synth,cosim,trans,export,timing,drc,status,runs/'bd_0_wrapper_routed.dcp']
        paths += [ROOT/step['log'] for step in state['steps']]
        for f in paths:artifacts[str(f.relative_to(ROOT))]=sha256(f)
    ratios={}
    if results['csr']['axi_data_port_bits']!=results['compact']['axi_data_port_bits']:
        raise ValueError('Memory-interface data widths differ between fixed variants')
    comparisons=([('csr/csr','compact/traversal'),('csr/csr','compact/intent'),('csr/heldout_csr','compact/heldout_compact')]
                 if args.kind=='fixed' else [('csr/matched.bin','compact/matched.bin')])
    for baseline,candidate in comparisons:
        a,b=batches[baseline],batches[candidate]
        for key in ['requests','records','expected_status_failures','request_ids_sha256']:
            if a[key]!=b[key]:raise ValueError('Unmatched workload '+key)
        ratios[candidate+'_over_'+baseline]=b['cycles']/a['cycles']
    timing_pass=all(r['timing']['constrained_internal_timing_met'] for r in results.values())
    route_pass=all(r['route_status']['fully routed nets']==r['route_status']['routable nets'] and not r['route_status']['nets with routing errors'] for r in results.values())
    report={'created_utc':datetime.now(timezone.utc).isoformat(),'status':args.kind+'_modes_complete',
        'fixed_implementations':results,'batches':batches,'compact_over_csr_cycle_ratios':ratios,
        'both_internal_timing_met':timing_pass,'both_fully_routed':route_pass,
        'source_bundle_manifest_sha256':sha256(bundle/'manifest.json'),'artifacts':artifacts,
        'limitations':['Constant-mode specialization only; not independently tuned high-throughput architectures.',
            'Same graph data and request IDs; RTL uses feature-stratified subsets, complete sampled rows use Csim.',
            'AXI simulation model and OOC internal timing; external IO and real DDR/HBM performance are unverified.',
            'Separate shared baseline remains preserved; these results do not establish whole-router acceleration.']}
    write_new(args.output,report)
    print(json.dumps({'output':str(args.output),'results':results,'ratios':ratios},indent=2))
    return 0 if timing_pass and route_pass else 1


if __name__=='__main__':raise SystemExit(main())
