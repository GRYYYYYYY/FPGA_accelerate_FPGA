#!/usr/bin/env python3
"""Independent audit of the new naming-only compact HLS candidate, not RTL PASS."""
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET
from check_vitis_kernel import digest, require

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
BUNDLE=BASE/'collision_safe_batch_hls_v1'
REPORT=ROOT/'results/collision_safe_compact_hls_audit_20261030_v1.json'


def instances(text):
    return [(m[1],m[2],dict(re.findall(r'\.(\w+)\(([^()]*)\)',m[3])),m.start())
            for m in re.finditer(r'^(\w+)\s+(grp_\w+)\((.*?)\n\);',text,re.M|re.S)]


def main():
    require(not REPORT.exists(),'Refuse overwrite')
    state=json.loads((BUNDLE/'state.json').read_text())
    require(state['status']=='synthesized_pending_independent_audit','New HLS is not complete')
    require(state['completed']==['full44_cpu_mode_0','full44_cpu_mode_1'],'CPU stages missing')
    plan=json.loads((BUNDLE/'plan.json').read_text())
    require((plan['ports'],plan['transactions_per_mode'],plan['c_modes'],plan['hls_mode'])==(44,4,[0,1],1),'Changed scope')
    files=dict(plan['files'])
    for n,h in files.items():require(digest(n)==h,'Changed HLS input '+n)
    receipt=json.loads((BUNDLE/'hls.receipt.json').read_text())
    log=BUNDLE/'hls.log';text=log.read_text()
    require(receipt['exit_code']==0 and receipt['abort_reason'] is None and receipt['log_sha256']==digest(log),'HLS failed/changed')
    require(receipt['command'][:5]==['prlimit','--as=68719476736:68719476736','--stack=67108864:67108864','--core=0:0','--'],
            'Different finite HLS resource envelope')
    require(text.splitlines().count('COLLISION_SAFE_FULL_BATCH_CSYNTH_COMPLETE')==1 and 'ERROR:' not in text,'Missing actual success marker')
    conflicts=[line for line in text.splitlines() if 'RTL name' in line and 'due to conflict' in line]
    require(not conflicts,'Unresolved naming conflict')
    source=BUNDLE/'source';original=BASE/'compressed_batch_compact_cosim_setup/source'
    require({p.name for p in source.iterdir()}=={p.name for p in original.iterdir()},'Source set changed')
    changes=[]
    for p in source.iterdir():
        before=(original/p.name).read_text();after=p.read_text();restored=after
        for old,new in plan['renames'].items():restored=re.sub(r'\b'+new+r'\b',old,restored)
        require(restored==before,'Non-identifier change '+p.name)
        if after!=before:changes.append(p.name)
    require(set(changes)=={'search_route_tree.hpp','search_resident_snapshot.hpp','search_trace_records.hpp',
                          'search_batch_trace_top_v2.cpp','search_batch_top.cpp','search_net_top.cpp'},'Unexpected changed files')
    cpu_path=ROOT/'results/collision_safe_batch_full44_cpu_20261030_v1.json'
    cpu=json.loads(cpu_path.read_text())
    require(cpu['status']=='identifier_only_candidate_matches_all8_original_full44_C_snapshots','Wrong CPU evidence')
    require({(r['mode'],r['transaction']) for r in cpu['comparisons']}=={(m,t) for m in [0,1] for t in range(4)},'Incomplete C cases')
    for n,h in cpu['files'].items():require(digest(n)==h,'Changed full C evidence '+n)
    files.update(cpu['files'])
    solution=BUNDLE/'project/solution';rtl=solution/'syn/verilog';top='search_batch_trace_top_v2'
    xml=solution/'syn/report'/f'{top}_csynth.xml';x=ET.parse(xml).getroot()
    ua={p.tag:p.text for p in x.find('UserAssignments')}
    require(x.findtext('ReportVersion/Version')=='2022.2' and ua['TopModelName']==top and
            ua['Part']=='xcu280-fsvh2892-2L-e' and float(ua['TargetClockPeriod'])==5 and float(ua['ClockUncertainty'])==1.35,
            'Different tool/top/constraints')
    oldxml=BASE/'compressed_batch_compact_cosim_project/solution/syn/report'/f'{top}_csynth.xml'
    old=ET.parse(oldxml).getroot()
    def ports(tree):
        return {p.findtext('name'):{c.tag:c.text for c in p} for p in tree.findall('InterfaceSummary/RtlPorts')}
    require(ports(x)==ports(old) and len(ports(x))>100,'Native interface changed')
    inventory_path=ROOT/'results/hls_collided_port_inventory_20261030_v1.json'
    inventory=json.loads(inventory_path.read_text());require(len(inventory['connections'])==9,'Incomplete original collision inventory')
    for n,h in inventory['files'].items():require(digest(n)==h,'Changed collision evidence '+n)
    connections=[]
    for row in inventory['connections']:
        parent=rtl/Path(row['parent']).name
        expected_module=row['module'].replace(top+'_net',top+'_a_write_net_trace_record') if row['module']==top+'_net' else row['module']
        entries=[r for r in instances(parent.read_text()) if r[0]==expected_module]
        require(len(entries)==1,'Ambiguous/new callee mapping '+expected_module)
        module,instance,pins,offset=entries[0];port=row['port'][:-2]
        require(port in pins and row['port'] not in pins,'Port not restored '+row['port'])
        value=pins[port].strip()
        require(re.fullmatch(r'[A-Za-z_]\w*',value) is not None,'Constant/non-signal restored port '+port)
        require(re.search(r'^(?:input|wire|reg)\s+(?:signed\s+)?(?:\[[^\]]+\]\s*)?'+re.escape(value)+r'\s*;',parent.read_text(),re.M),
                'Restored connection has no actual signal declaration')
        child=rtl/(module+'.v')
        require(re.search(r'^input\s+(?:signed\s+)?\[(?:63|31):0\]\s+'+port+r'\s*;',child.read_text(),re.M),
                'Unexpected restored child input type')
        connections.append(dict(original=row,parent=str(parent),module=module,instance=instance,port=port,connection=value))
    require(len(connections)==9,'Incomplete restored connection set')
    for p in rtl.glob('*.v'):
        require(not re.search(r'\.(?:roots_x|query_x|net_x)\(',p.read_text()),'Old collided port remains')
    resources={p.tag:int(p.text) for p in x.find('AreaEstimates/Resources')}
    timing=x.findtext('PerformanceEstimates/SummaryOfTimingAnalysis/EstimatedClockPeriod')
    for directory in [rtl,solution/'syn/report']:
        for p in directory.rglob('*'):
            if p.is_file():files[str(p)]=digest(p)
    for p in [BUNDLE/'plan.json',BUNDLE/'state.json',BUNDLE/'hls.receipt.json',log,BUNDLE/'project/hls.app',
              cpu_path,inventory_path,oldxml,Path(__file__).resolve()]:files[str(p)]=digest(p)
    result=dict(status='collision_safe_native_compact_hls_all9_dynamic_connections_and_full44_C_verified_rtl_pending',
                files=files,changed_source_files=changes,restored_connections=connections,
                resources=resources,estimated_clock_period_ns=float(timing),native_interface_equal=True,
                graph_mode=1,ports=44,transactions=4,naming_conflicts=conflicts,rtl_accepted=False,
                limits=['All9 observed wrong constant connections now use real input signals; this is a structural check, not complete RTL functional equivalence.',
                        'HLS estimates are not routed resources, timing closure, throughput or board results.',
                        'New full-depth setup, nonzero pointer mapping,4 RTL transactions,original C postcheck and all full snapshots remain required.'])
    REPORT.write_text(json.dumps(result,indent=2)+'\n')
    print(result['status'],resources)


if __name__=='__main__':main()
