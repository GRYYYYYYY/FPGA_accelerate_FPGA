#!/usr/bin/env python3
"""Independently check frozen sources, full Csim, sampled RTL, and exported XO ABI."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

ROOT=Path(__file__).resolve().parents[1]

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
    return h.hexdigest()

def require(condition,message):
    if not condition:raise ValueError(message)

def validate_case_log(text,manifest,copies):
    expected=[]
    for line in Path(manifest).read_text().splitlines():
        image,config,case=map(Path,line.split())
        with case.open('rb') as f:n,capacity,records,failed=struct.unpack('<4I',f.read(16))
        expected.append((str(case),str(n),str(records),str(failed)))
    observed=re.findall(r'^CASE_PASS (\S+) requests=(\d+) records=(\d+) failed=(\d+)$',text,re.M)
    require(observed==expected*copies,'Missing, extra, reordered or mismatched test cases')
    require(re.findall(r'^GRAPH_EXPAND_PASS cases=(\d+)$',text,re.M)==[str(len(expected))]*copies,'Test completion count differs')
    return [{'case':p,'requests':int(n),'records':int(r),'failed':int(f)} for p,n,r,f in expected]

def validate_abi(xml):
    root=ET.fromstring(xml)
    kernels=list(root.iter('kernel'))
    require(len(kernels)==1 and kernels[0].get('name')=='graph_accel','Unexpected XO kernel')
    kernel=kernels[0];args=kernel.findall('./args/arg')
    names=['image','config','requests','output','result','counts','request_count','output_capacity_words']
    ports={p.get('name'):p.attrib for p in kernel.findall('./ports/port')}
    require(len(args)==8,'Wrong argument count')
    offsets=[]
    for i,(arg,name) in enumerate(zip(args,names)):
        require(arg.get('name')==name and int(arg.get('id'))==i,'Argument order changed')
        require(int(arg.get('addressQualifier'))==(1 if i<6 else 0),'Wrong pointer/scalar ABI')
        size=int(arg.get('size'),0);offset=int(arg.get('offset'),0)
        require(size==(8 if i<6 else 4) and offset>=16 and offset%4==0,'Wrong register size/alignment')
        require(not offsets or offsets[-1][1]<=offset,'Overlapping control registers');offsets.append((offset,offset+size))
        port=ports.get(arg.get('port'));require(port is not None,'Missing argument port')
        require(port.get('mode')==('master' if i<6 else 'slave'),'Wrong AXI port direction')
    return {'arguments':[a.attrib for a in args],'ports':list(ports.values()),'kernel':kernel.attrib}

def validate_packaged_rtl(archive,directory):
    rtl={Path(name).name:name for name in archive.namelist() if '/hdl/verilog/' in name and name.endswith('.v')}
    sources={p.name:p for p in Path(directory).glob('*.v')}
    require(rtl and set(rtl)==set(sources),'XO/synthesized RTL file set differs')
    for name,path in sources.items():
        require(archive.read(rtl[name])==path.read_bytes(),'XO RTL differs from validated project: '+name)
    return {str(p):digest(p) for p in sources.values()}

def audit(bundle):
    bundle=Path(bundle).resolve();plan_path=bundle/'plan.json';plan=json.loads(plan_path.read_text())
    pipeline_path=bundle/'pipeline.json';pipeline=json.loads(pipeline_path.read_text())
    require(pipeline['status']=='complete' and sorted(pipeline['completed_modes'])==['compact','csr'],'Pipeline not complete')
    require(pipeline['plan_sha256']==digest(plan_path),'Plan changed')
    bound={**plan['files'],**plan['generated'],**pipeline['files']}
    for path,value in bound.items():require(digest(path)==value,'Frozen dependency changed: '+path)
    prior_path=ROOT/'results/hls_region_check_20261023_v1.json';prior=json.loads(prior_path.read_text())
    original=ROOT/'data/derived/hls_region_fixtures_20261023_v1';mp=original/'manifest.json';manifest=json.loads(mp.read_text())
    require(digest(mp)==prior['source_bundle_manifest_sha256'],'Original fixture manifest changed')
    for name,value in manifest['files'].items():require(digest(original/name)==value,'Original fixture changed: '+name)
    for item in manifest['image_files'].values():require(digest(item['path'])==item['sha256'],'Original image changed')
    artifacts={str(plan_path):digest(plan_path),str(pipeline_path):digest(pipeline_path),str(Path(__file__).resolve()):digest(__file__)}
    modes={}
    stamp=bundle.name.removeprefix('vitis_graph_kernel_')
    for mode in ['csr','compact']:
        directory=bundle/mode;old=original/mode
        source=(old/'graph_expand.cpp').read_text()
        interfaces=[s for s in source.splitlines() if s.startswith('#pragma HLS INTERFACE ')]
        require(len(interfaces)==15,'Original interfaces changed')
        expected='\n'.join(s for s in source.splitlines() if not s.startswith('#pragma HLS INTERFACE '))+'\n'
        expected=expected.replace('#include "graph_expand.hpp"','#include "graph_body.hpp"').replace('void graph_expand(','void graph_expand_body(')
        require((directory/'graph_body.cpp').read_text()==expected,'Decode algorithm differs')
        require((directory/'graph_body.hpp').read_text()==(old/'graph_expand.hpp').read_text().replace('void graph_expand(','void graph_expand_body('),'Body interface differs')
        require((directory/'test_graph_expand.cpp').read_text()==(old/'test_graph_expand.cpp').read_text().replace('#include "graph_expand.hpp"','#include "graph_accel.hpp"'),'Golden comparison weakened')
        state_path=bundle/(mode+'.state.json');state=json.loads(state_path.read_text())
        require(state['status']=='complete' and [s['stage'] for s in state['steps']]==['synth','cosim','export'],'Missing stage')
        for step in state['steps']:
            log=directory/(step['stage']+'.log');receipt=directory/(step['stage']+'.receipt.json');content=log.read_text()
            require(step==json.loads(receipt.read_text()) and step['exit_code']==0 and step['completion_marker'],'Bad stage receipt')
            require(digest(log)==step['log_sha256'] and 'ERROR:' not in content and 'VITIS_GRAPH_'+step['stage'].upper()+'_COMPLETE' in content,'Stage log failed or changed')
            for p in [log,receipt]:artifacts[str(p)]=digest(p)
        full=validate_case_log((directory/'synth.log').read_text(),directory/'full.txt',1)
        rtl=validate_case_log((directory/'cosim.log').read_text(),directory/'rtl.txt',2)
        normal=[r for r in full if Path(r['case']).name.startswith('full_')]
        require((sum(r['requests'] for r in normal),sum(r['records'] for r in normal))==(274732,1100754),'Full coverage differs')
        solution=ROOT/'build'/f'vitis_graph_{mode}_{stamp}'/'solution'
        synth=solution/'syn/report/graph_accel_csynth.xml';cosim=solution/'sim/report/graph_accel_cosim.rpt'
        trans=solution/'sim/report/verilog/result.transaction.rpt';xo=directory/'graph_accel.xo'
        require(re.search(r'Verilog\s*\|\s*Pass',cosim.read_text()),'RTL report not passing')
        cycles=[int(n) for n in re.findall(r'transaction\s+\d+:\s+(\d+)',trans.read_text())]
        require(len(cycles)==len(rtl) and all(c>0 for c in cycles),'Missing RTL transactions')
        for entry,cycle in zip(rtl,cycles):entry['cycles']=cycle
        xml=ET.parse(synth).getroot()
        require(float(xml.findtext('UserAssignments/TargetClockPeriod'))==5 and xml.findtext('UserAssignments/Part')=='xcu280-fsvh2892-2L-e','Unexpected part/clock')
        with zipfile.ZipFile(xo) as archive:
            names=[n for n in archive.namelist() if n.endswith('/kernel.xml') or n=='kernel.xml']
            require(len(names)==1 and archive.testzip() is None,'Invalid XO archive')
            abi=validate_abi(archive.read(names[0]))
            artifacts.update(validate_packaged_rtl(archive,solution/'syn/verilog'))
        for p in [state_path,synth,cosim,trans,xo]:artifacts[str(p)]=digest(p)
        modes[mode]={'full_csim':full,'rtl_sample':rtl,'xo':str(xo),'xo_abi':abi,
            'estimated_resources':{e.tag:int(e.text) for e in xml.find('AreaEstimates/Resources')},
            'estimated_clock_ns':float(xml.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')),
            'synthesis_loop_constraint_warning':'All loop constraints were NOT satisfied' in (directory/'synth.log').read_text()}
    require(modes['csr']['xo_abi']==modes['compact']['xo_abi'],'Representations have different external ABI')
    return {'status':'verified_vitis_xo_not_platform_linked','created_utc':datetime.now(timezone.utc).isoformat(),
        'bundle':str(bundle),'plan_sha256':digest(plan_path),'modes':modes,'artifacts':artifacts,
        'limitations':['RTL covers three batches; complete graph coverage is C simulation only.',
            'XO is not a platform-linked xclbin; no board DDR/HBM/power result or routed timing for this wrapper.',
            'Adjacency provider only; no complete router offload.']}

def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    report=audit(a.bundle)
    with a.output.open('x') as f:json.dump(report,f,indent=2);f.write('\n')
    print(json.dumps({'status':report['status'],'output':str(a.output)}))

if __name__=='__main__':main()
