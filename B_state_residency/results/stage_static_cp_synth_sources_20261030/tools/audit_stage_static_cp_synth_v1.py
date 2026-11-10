"""Audit matched isolated static stage OOC; retain unqualified timing and loop evidence."""
from pathlib import Path
from collections import Counter
import json,re,sys
from stage_static_cp_synth_common_v1 import (ROOT,TARGET,REFERENCE,VARIANT,BIN,sha,read,
    identity,evidence,runtime_environment)
from audit_restore_seed_diagnostics import audit as audit_diagnostics
p=Path(sys.argv[1]).resolve();assert p==TARGET
m=read(p/'manifest.json');assert m['status']=='observed' and m['stage']=='complete' and m['exit_code']==0
assert not m.get('active_process') and identity(m['runner_pid'])!=str(m['runner_start_ticks'])
rm,ra,fm,fa,expected=evidence();ref=REFERENCE
assert m['reference']==str(ref) and m['reference_audit_sha256']==sha(ref/'source_bound_audit.json')
assert m['stage_static_evidence']==expected
assert {entry['source']:entry['sha256'] for entry in m['bound'].values()}==expected
for name,entry in m['bound'].items():assert sha(entry['source'])==entry['sha256']==sha(p/'bound'/name)
assert m['rtl']==rm['rtl'] and m['parameters']==rm['parameters'] and m['part']==rm['part']
fixed={'route_commit_controller.sv','route_commit_host_adapter.sv'}
assert set(m['production_changes'])==fixed
prepare='prepare_stage_static_cp_synth_v1.py'
assert set(m['sources'])==set(rm['sources'])
for name,digest in m['sources'].items():
    assert sha(p/'sources'/name)==digest,name
    if name in fixed:
        assert digest==sha(VARIANT/'fixed'/name)==fm['sources'][name]['sha256']
        assert m['production_changes'][name]==dict(original_sha256=rm['sources'][name],candidate_sha256=digest)
    else:assert digest==rm['sources'][name]
for name in m['rtl']:assert sha(p/'sources'/name)==sha(Path('/tmp/B_state_residency_offer_20261025/stage_static_cp_system_v1/sources')/name)
assert (p/'synth.tcl').read_text()==(ref/'synth.tcl').read_text().replace(str(ref),str(p))
assert (p/'clock.xdc').read_bytes()==(ref/'clock.xdc').read_bytes()
assert sha(p/'synth.tcl')==m['tcl_sha256'] and sha(p/'clock.xdc')==m['xdc_sha256']
reads=re.findall(r'^read_verilog -sv \{([^}]+)\}$',(p/'synth.tcl').read_text(),re.M)
assert reads==[str(p/'sources'/name) for name in m['rtl']]
assert m['runtime']==runtime_environment()[1]
assert m['runner_sha256']==sha(ROOT/'scripts/run_stage_static_cp_synth_v1.py')
assert [c['stage'] for c in m['commands']]==['version','synthesis']
expected_commands=[[str(BIN),'-version'],[str(BIN),'-mode','batch','-source',str(p/'synth.tcl'),'-log',str(p/'vivado.log'),'-journal',str(p/'vivado.jou')]]
for c,argv,filename in zip(m['commands'],expected_commands,['version.stdout.log','stdout.log']):
    assert c['argv']==argv and c['exit_code']==0 and sha(p/filename)==c['stdout_sha256']
    if c['start_ticks'] is not None:assert identity(c['pid'])!=str(c['start_ticks'])
assert 'Vivado v2022.2' in (p/'version.stdout.log').read_text() and m['command']==expected_commands[1]
assert m['memory_admission']['stable_seconds']>=60
assert m['memory_admission']['current_bytes']*4<=m['memory_admission']['limit_bytes']*3
im=read(p/'results/methodology_v1/manifest.json')
assert im['status']=='observed' and im['exit_code']==0 and not im.get('active_process')
assert im['runner_sha256']==sha(ROOT/'scripts/inspect_stage_static_cp_synth_v1.py')
assert im['runtime']==m['runtime'] and im['memory_admission']['stable_seconds']>=60
assert im['memory_admission']['current_bytes']*4<=im['memory_admission']['limit_bytes']*3
assert identity(im['runner_pid'])!=str(im['runner_start_ticks'])
assert sha(p/'runner.py')==m['runner_sha256']
assert (p/'clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
assert all(not Path(n).name.startswith('tb_')and Path(n).name!='axi_file_memory.sv'for n in m['rtl'])
assert len(m['rtl'])==133 and len(set(m['rtl']))==133
log=(p/'vivado.log').read_text()
assert 'VIVADO_VERSION 2022.2'in log and 'RESTORE_SEED_OOC_DONE'in log and 'synth_design completed successfully'in log
assert not re.search(r'^ERROR:',log,re.M),'Vivado command errors'
critical=[line for line in log.splitlines()if line.startswith('CRITICAL WARNING:')]
# Reviewed failure evidence, not a waiver: preserve the loop diagnostics and
# reject the design below. Unknown critical warnings still require inspection.
assert all(line.startswith('CRITICAL WARNING: [Synth 8-295] found timing loop.')for line in critical), 'Unreviewed critical warning'
top=log.split("synthesizing module 'query_residency_system'",1)[1].split('INFO:',1)[0]
params={n:int(v)for n,v in re.findall(r'Parameter (\w+) bound to:\s*(\d+)',top)}
assert params==m['parameters']
enabled=params['ENABLE_RESTORE_SEED_BYPASS'];assert enabled in [0,1]
assert re.findall(r'Parameter ENABLE_RESTORE_SEED_BYPASS bound to:\s*(\d+)',log)==[str(enabled)]*3
assert 'Parameter MAX_RECORDS bound to: 1024'in log
facts={}
for line in(p/'facts.txt').read_text().splitlines():
    values=line.split();assert len(values)%2==0
    facts.update({values[i]:int(values[i+1])for i in range(0,len(values),2)})
assert facts['latches']==facts['blackboxes']==facts['file_agents']==facts['directory_observers']==0
assert facts['port_bits']>0 and facts['bypass_port']==1
assert (facts['bypass_endpoints']>0)==bool(enabled)
report=(p/'utilization.rpt').read_text()
assert 'Vivado v.2022.2'in report and 'Synthesized'in report and m['part']in report
def num(label):
    match=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d,.]+)',report,re.M)
    assert match,label
    return float(match[1].replace(',',''))
util={k:num(v)for k,v in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs'),('URAM','URAM')]}
assert util['latches']==0 and util['LUT']>0 and util['FF']>0
clocks=(p/'clocks.rpt').read_text();assert re.search(r'^core_clk\s+10\.000\b',clocks,re.M)
timing=(p/'timing_synth.rpt').read_text();assert 'Design Timing Summary'in timing and 'core_clk'in timing
# Store the original report excerpt without converting pre-placement estimates
# or unconstrained IO paths into a board-frequency claim.
summary=timing.split('Design Timing Summary',1)[1].split('Clock Summary',1)[0].strip()
# Artifact integrity is separate from electrical/design acceptance. Vivado can
# finish successfully after automatically cutting combinational timing loops.
# Preserve every final-log occurrence (including repeated/renamed cones).
loop_warnings=[line for line in log.splitlines()if line.startswith('WARNING: [Synth 8-326]')]
checks=(p/'check_timing.rpt').read_text()
check_counts={name:int(count)for name,count in re.findall(r'^\d+\. checking (\w+) \((\d+)\)',checks,re.M)}
assert 'loops'in check_counts and 'no_clock'in check_counts
assert not critical or check_counts['loops']>0,'critical loop not reflected in timing checks'
wns_match=re.search(r'^\s*(-?\d+\.\d+)\s+(-?\d+\.\d+)\s+\d+\s+\d+',summary,re.M)
assert wns_match,'missing timing summary values'
for n in ['synth.dcp','synth.v']:assert(p/n).stat().st_size>1000
net=(p/'synth.v').read_text()
for name in ['query_residency_system','label_restore_controller','warm_restore_receipt_join']:
    assert re.search(r'\bmodule\s+'+name+r'\b',net),name
diagnostics=audit_diagnostics(p)
assert diagnostics['design_acceptance']==('rejected_combinational_loops'if check_counts['loops']else'unresolved')
walks=json.loads((p/'loop_walks.json').read_text())
assert walks['check_timing_sha256']==sha(p/'check_timing.rpt')and walks['reported_loops']==check_counts['loops']
artifacts=['manifest.json','runner.py','synth.tcl','clock.xdc','vivado.log','vivado.jou','stdout.log',
           'utilization.rpt','timing_synth.rpt','check_timing.rpt','facts.txt','clocks.rpt','synth.dcp','synth.v',
           'loop_walks.json','diagnostic_audit.json']
artifacts.append('version.stdout.log')
assert not re.search(r'\bmodule\s+config_restore_controller_observer\b',net)
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),
    audit_kind='source and synthesis artifact integrity, not design acceptance',
    design_acceptance='rejected_combinational_loops'if check_counts['loops']else'unresolved',timing_qualified=False,
    check_timing_counts=check_counts,preplacement_wns_ns=float(wns_match[1]),
    timing_loop_warnings=loop_warnings,
    critical_warnings=critical,
    diagnostic_manifest_sha256=diagnostics['manifest_sha256'],
    methodology_counts=diagnostics['methodology_counts'],
    drc_loop_cell_counts=[len(v['CELLS'])for v in diagnostics['loop_elements'].values()],
    timing_limitations=['pre-placement OOC estimate; IO timing not specified',
        'methodology and physical implementation remain required']+
        (['synthesis inserted automatic timing-loop exceptions; reported slack cannot establish timing validity']if loop_warnings else []),
    production_changes=m['production_changes'],stage_static_evidence=m['stage_static_evidence'],
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),parameters=params,utilization=util,facts=facts,
    warnings=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),
    synthesis_timing_summary=summary,clock_period_ns=10,
    artifact_sha256={n:sha(p/n)for n in artifacts},scope=m['scope'])
result.update(runtime=m['runtime'],inspector_runner_sha256=im['runner_sha256'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('STAGE_STATIC_CP_SYNTH_AUDITED',p.name,util,facts)
