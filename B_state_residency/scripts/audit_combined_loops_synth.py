"""Audit the five-source cumulative OOC against restored component evidence."""
from pathlib import Path
from collections import Counter
import json,re,sys
from run_checkpoint_authority import ROOT,sha
from audit_restore_seed_diagnostics import audit as audit_diagnostics

p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text())
assert m['status']=='observed'and m['exit_code']==0
ref=Path(m['reference']);rm=json.loads((ref/'manifest.json').read_text());ra=json.loads((ref/'source_bound_audit.json').read_text())
assert ra['status']=='passed'and ra['manifest_sha256']==sha(ref/'manifest.json')
assert m['reference_audit_sha256']==sha(ref/'source_bound_audit.json')
groups={'capture_loops_component_v1':['recursive/recursive_candidate_controller.sv','capture/expansion_capture.sv'],
        'rearm_loops_component_v2':['recovery_coordinator.sv','label_restore_controller.sv','residency_system.sv']}
expected_changes={n for names in groups.values()for n in names}
assert set(m['production_changes'])==expected_changes and set(m['component_receipts'])==set(groups)
assert set(m['sources'])==set(rm['sources'])|{'prepare_combined.py'}
assert m['parameters']==rm['parameters']and m['rtl']==rm['rtl']and m['part']==rm['part']
assert (p/'synth.tcl').read_text()==(ref/'synth.tcl').read_text().replace(str(ref),str(p))
assert (p/'clock.xdc').read_bytes()==(ref/'clock.xdc').read_bytes()
for component,names in groups.items():
    c=p.parent/component;cm=json.loads((c/'manifest.json').read_text());ca=json.loads((c/'source_bound_audit.json').read_text())
    assert ca['status']=='passed'and ca['manifest_sha256']==sha(c/'manifest.json')
    receipt=ROOT/'results'/f'{component}_restore_20261025.json';rr=json.loads(receipt.read_text())
    assert rr['status']=='passed'and rr['audit_byte_identical']and rr['audit_sha256']==sha(c/'source_bound_audit.json')
    assert m['component_receipts'][component]==dict(audit_sha256=sha(c/'source_bound_audit.json'),restore_receipt_sha256=sha(receipt))
    for n in names:
        basename=Path(n).name;base=c/'sources/baseline'/basename;fixed=c/'sources/fixed'/basename
        assert sha(base)==rm['sources'][n]==sha(ref/'sources'/n)
        assert sha(fixed)==cm['sources']['fixed/'+basename]['sha256']==m['sources'][n]
        assert m['production_changes'][n]==dict(component=component,original_sha256=sha(base),candidate_sha256=sha(fixed),path=str(fixed))
for n,h in m['sources'].items():
    assert sha(p/'sources'/n)==h,n
    if n not in expected_changes|{'prepare_combined.py'}:assert h==rm['sources'][n],n
assert sha(p/'sources/prepare_combined.py')==sha(ROOT/'scripts/prepare_combined_loops_synth.py')
assert sha(p/'synth.tcl')==m['tcl_sha256']and sha(p/'clock.xdc')==m['xdc_sha256']
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
    production_changes=m['production_changes'],component_receipts=m['component_receipts'],
    reference_audit_sha256=sha(ref/'source_bound_audit.json'),parameters=params,utilization=util,facts=facts,
    warnings=dict(Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))),
    synthesis_timing_summary=summary,clock_period_ns=10,
    artifact_sha256={n:sha(p/n)for n in artifacts},scope=m['scope'])
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
print('COMBINED_LOOPS_SYNTH_AUDITED',p.name,util,facts)
