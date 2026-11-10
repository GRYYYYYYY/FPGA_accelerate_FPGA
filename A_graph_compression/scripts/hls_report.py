#!/usr/bin/env python3
"""Collect completed classic-HLS evidence without treating estimates as measurements."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import struct
import sys
import xml.etree.ElementTree as ET

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'adapters'))
from import_vivado import sha256
from real_experiment import write_new


def main(argv=None):
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--project',type=Path,default=ROOT/'build/hls_graph_expand_20261022_v2')
    p.add_argument('--matched-project',type=Path,default=ROOT/'build/hls_graph_expand_20261022_v3')
    p.add_argument('--fixtures',type=Path,default=ROOT/'data/derived/hls_fixtures_20261022_v2')
    p.add_argument('--output',type=Path,required=True)
    args=p.parse_args(argv)
    fixture_manifest=args.fixtures/'manifest.json'
    fixtures=json.loads(fixture_manifest.read_text())
    for name,digest in fixtures['files'].items():
        if sha256(args.fixtures/name)!=digest:raise ValueError('Fixture changed: '+name)
    for name,digest in fixtures['code_sha256'].items():
        if sha256(ROOT/name)!=digest:raise ValueError('Test/kernel source changed: '+name)
    reports={}
    for label,project in [('functional',args.project),('matched',args.matched_project)]:
        csim=project/'solution/csim/report/graph_expand_csim.log'
        synth=project/'solution/syn/report/graph_expand_csynth.xml'
        cosim=project/'solution/sim/report/graph_expand_cosim.rpt'
        trans=project/'solution/sim/report/verilog/result.transaction.rpt'
        if 'GRAPH_EXPAND_PASS' not in csim.read_text():raise ValueError('Missing C simulation pass')
        if not re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()):raise ValueError('Missing RTL simulation pass')
        xml=ET.parse(synth).getroot()
        clock=float(xml.findtext('UserAssignments/TargetClockPeriod'))
        reports[label]={'project':str(project),'c_simulation_pass':True,'rtl_simulation_pass':True,
                        'hls_target_clock_ns':clock,
                        'hls_estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
                        'hls_estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
                        'transaction_cycles':[int(x) for x in re.findall(r'transaction\s+\d+:\s+(\d+)',trans.read_text())],
                        'evidence':{str(f.relative_to(ROOT)):sha256(f) for f in [csim,synth,cosim,trans]}}
    lines=(args.fixtures/'matched.txt').read_text().splitlines()
    cycles=reports['matched']['transaction_cycles']
    if len(lines)!=len(cycles):raise ValueError('Transaction/fixture count differs')
    batches={}
    for line,latency in zip(lines,cycles):
        image,config,stimulus=map(Path,line.split())
        data=stimulus.read_bytes();requests,capacity,records,failed=struct.unpack_from('<4I',data)
        name=stimulus.name.removesuffix('.matched.bin')
        batches[name]={'requests':requests,'records':records,'expected_error_statuses':failed,
                       'cycles':latency,'simulated_batch_ms':latency*reports['matched']['hls_target_clock_ns']/1e6,
                       'request_ids_sha256':__import__('hashlib').sha256(data[16:16+4*requests]).hexdigest(),
                       'image_sha256':sha256(image)}
    ratios={}
    for baseline,candidate in [('csr','traversal'),('csr','intent'),('heldout_csr','heldout_compact')]:
        a,b=batches[baseline],batches[candidate]
        for k in ['requests','records','expected_error_statuses','request_ids_sha256']:
            if a[k]!=b[k]:raise ValueError('Mismatched work: '+k)
        ratios[candidate+'_over_'+baseline]=b['cycles']/a['cycles']
    export=args.project/'solution/impl/report/verilog/graph_expand_export.rpt'
    content=export.read_text()
    # A synthesis-only report exists before route completion. Do not accept it.
    if 'Post-Implementation' not in content or 'CP achieved post-implementation:' not in content:
        raise ValueError('Implementation report is not complete')
    implementation={'report':str(export.relative_to(ROOT)),'sha256':sha256(export),'content':content}
    runs=args.project/'solution/impl/verilog/project.runs/impl_1'
    timing=runs/'bd_0_wrapper_timing_summary_routed.rpt'
    drc=runs/'bd_0_wrapper_drc_routed.rpt'
    route=args.project/'solution/impl/verilog/report/graph_expand_status_routed.rpt'
    timing_text=timing.read_text()
    timing_match=re.search(r'WNS\(ns\).*\n\s*[- ]+\n\s*([0-9.\-]+)\s+([0-9.\-]+)\s+\d+\s+\d+\s+([0-9.\-]+)\s+([0-9.\-]+)',timing_text)
    if not timing_match:raise ValueError('Cannot parse final timing summary')
    implementation['timing_ns']=dict(zip(['WNS','TNS','WHS','THS'],map(float,timing_match.groups())))
    implementation['unconstrained_input_ports']=int(re.search(r'checking no_input_delay \((\d+)\)',timing_text)[1])
    implementation['unconstrained_output_ports']=int(re.search(r'checking no_output_delay \((\d+)\)',timing_text)[1])
    implementation['drc_violations']=int(re.search(r'Violations found:\s*(\d+)',drc.read_text())[1])
    implementation['route_status']=route.read_text()
    implementation['post_route_resources']={k:int(v) for k,v in re.findall(r'^(LUT|FF|DSP|BRAM|URAM|SRL|CLB):\s+(\d+)',content,re.M)}
    evidence={str(p.relative_to(ROOT)):sha256(p) for p in
              (args.project/'solution/impl/verilog/report').glob('*.rpt')}
    evidence.update({str(p.relative_to(ROOT)):sha256(p) for p in
                     [timing,drc,runs/'bd_0_wrapper_routed.dcp',args.project/'solution/impl/export.zip',
                      ROOT/'results/hls_synth_20261022_v2.log',ROOT/'results/hls_cosim_20261022_v2.log',
                      ROOT/'results/hls_impl_20261022_v2.log',ROOT/'results/hls_synth_20261022_v3.log',
                      ROOT/'results/hls_cosim_20261022_v3.log',ROOT/'results/hls_ii_diagnosis_20261022_v1.json']})
    result={'status':'completed_decoder_stage','created_utc':datetime.now(timezone.utc).isoformat(),
            'scope':'Same mode-selectable adjacency kernel, not an end-to-end FPGA router or a memory-platform benchmark',
            'hls':reports,'matched_batches':batches,'compact_over_csr_cycle_ratios':ratios,
            'implementation':implementation,'implementation_reports':evidence,
            'fixture_manifest':{'path':str(fixture_manifest.relative_to(ROOT)),'sha256':sha256(fixture_manifest)},
            'limitations':['VU13P graph stimuli on generic U280 decoder; U280 netlist graph is a separate dataset.',
                 'Only selected feature-stratified batches use RTL; complete sampled node sets use C simulation.',
                 'AXI co-simulation memory model is not calibrated to DDR/HBM; cycle ratios are within that model only.',
                 'Resource results cover one shared CSR/compact core, not separately optimized hardware baselines.',
                 'Automatic loop II constraints were not all met; data-dependent top latency is not statically bounded.',
                 'Standalone OOC implementation does not constitute complete board timing/IO signoff.',
                 'No board visible to XRT; no measured board bandwidth, power or application speedup.']}
    write_new(args.output,result)
    print(json.dumps({'output':str(args.output),'matched_batches':batches,'ratios':ratios},indent=2))
    return 0


if __name__=='__main__':raise SystemExit(main())
