"""Read-only physical main review; preserves all timing/DRC failures."""
from pathlib import Path
import collections,datetime,hashlib,json,re,sys,tarfile
R=Path(__file__).resolve().parents[2];sys.path.insert(0,str(R/'scripts'))
from stage_static_cp_physical_common_v6 import BASE,OUTPUT,read,sha,identity,audit_memory
from parse_state_timing_paths import parse_report
from audit_state_ooc_physical_v2 import utilization,timing_summary,route_status
from audit_state_route_recovery_v2 import commands

def table(path):
 text=path.read_text();rows=re.findall(r'^\|\s*([A-Z][A-Z0-9]*-\d+)\s*\|\s*([^|]+?)\s*\|\s*([^|]+?)\s*\|\s*(\d+)\s*\|',text,re.M)
 result={rule:dict(severity=severity,description=desc,count=int(n)) for rule,severity,desc,n in rows}
 details=collections.Counter(re.findall(r'^([A-Z][A-Z0-9]*-\d+)#\d+\s+(?:Critical Warning|Warning|Advisory|Error)\s*$',text,re.M))
 assert result and {k:v['count'] for k,v in result.items()}==dict(details)
 total=int(re.search(r'Violations found:\s*(\d+)',text)[1]);assert sum(details.values())==total
 return dict(total=total,rules=result)

def main():
 out=R/'results/stage_static_cp_physical_v6_main_review_20261104.json';assert not out.exists()
 p=OUTPUT;s=BASE/'stage_static_cp_physical_v6_supervision_v1';m,sm=read(p/'manifest.json'),read(s/'manifest.json');im=read(p/'inspection/manifest.json');a=read(p/'source_bound_audit.json')
 assert sm['status']=='terminal_audited_and_actual_restored_awaiting_main_review' and sm['stage']=='complete'
 assert [c['stage'] for c in sm['commands']]==['physical_run','independent_inspection','terminal_audit','restored_reaudit']
 for c in sm['commands']:
  assert c['exit_code']==0 and identity(c['pid'])!=str(c['start_ticks'])
  assert sha(s/(c['stage']+'.log'))==c['log_sha256']
 processes=[]
 for d,pid_key,tick_key in [(m,'runner_pid','runner_start_ticks'),(sm,'runner_pid','runner_start_ticks'),(im,'inspector_pid','inspector_start_ticks')]:
  assert not d.get('active_process') and identity(d[pid_key])!=str(d[tick_key])
  processes.append(dict(pid=d[pid_key],start_ticks=d[tick_key],current_start_ticks=identity(d[pid_key])))
 assert m['exit_code']==im['exit_code']==0 and all(c['exit_code']==0 for c in m['commands'])
 admission=[audit_memory(m),audit_memory(im)]
 receipt=Path(sm['terminal_report']);assert sha(receipt)==sm['terminal_report_sha256'];t=read(receipt)
 assert t['all_restored_files_byte_identical'] and t['physical_admitted']
 assert sha(t['archive'])==t['archive_sha256']==sm['archive_sha256']
 original=Path(t['original_preserved']);assert original!=p
 files=t['file_sha256'];seen=set()
 with tarfile.open(t['archive']) as tf:
  for item in tf:
   n=Path(item.name);assert item.isfile() and not n.is_absolute() and '..' not in n.parts and item.name in files and item.name not in seen
   seen.add(item.name);h=hashlib.sha256()
   with tf.extractfile(item) as f:
    for block in iter(lambda:f.read(1<<20),b''):h.update(block)
   assert h.hexdigest()==files[item.name]==sha(original/n)==sha(p/n)
 assert seen==set(files)
 assert (p/'source_bound_audit.json').read_bytes()==(original/'source_bound_audit.json').read_bytes()==(s/'expected_restored_audit.json').read_bytes()
 # Execute every original audit assertion up to its output-only guard; return the
 # computed object instead of touching any already-frozen audit. No flow rerun.
 auditor=R/'scripts/audit_stage_static_cp_physical_v6.py';src=auditor.read_text();marker="    assert not (p/'source_bound_audit.json').exists()"
 assert src.count(marker)==1 and "if __name__=='__main__'" not in src
 prefix=src.split(marker)[0];readonly=prefix+'    return result\n'
 namespace={'__name__':'readonly_physical_v6_main_review','__file__':str(auditor)};exec(compile(readonly,str(auditor),'exec'),namespace)
 previous=sys.argv;sys.argv=[str(auditor),str(p)]
 try:computed=namespace['main']()
 finally:sys.argv=previous
 assert computed==a
 assert sha(p/'source_bound_audit.json')==files['source_bound_audit.json']
 drc=table(p/'drc_routed.rpt');methods=table(p/'methodology_routed.rpt')
 assert drc==table(p/'inspection/drc.rpt') and methods==table(p/'inspection/methodology.rpt')
 assert drc['total']==86 and drc['rules']['NSTD-1']['count']==drc['rules']['UCIO-1']['count']==1
 assert (p/'drc_routed.rpt').read_text().count('Problem ports: cp_m_index[3].')==2
 diagnostics={}
 for name in ['stdout.log','vivado.log','inspection/stdout.log','inspection/vivado.log']:
  text=(p/name).read_text();lines=text.splitlines();assert not re.search(r'^ERROR:',text,re.M)
  diagnostics[name]=dict(sha256=sha(p/name),errors=0,critical_log_lines=[x for x in lines if x.startswith('CRITICAL WARNING:')],warning_counts=dict(collections.Counter(re.findall(r'^WARNING: \[([^]]+)\]',text,re.M))),warnings=[x for x in lines if x.startswith('WARNING:')])
 paths=parse_report((p/'timing_routed.rpt').read_text(),'core_clk');worst=min((x for x in paths if x['path_type']=='Setup'),key=lambda x:x['slack_ns'])
 assert worst['slack_ns']==a['timing_summaries']['routed']['WNS_ns']
 assert all(n['placement']=='routed' for x in paths for n in x['data_nets'])
 # Independently parse actually recovered reference reports, not just summary JSON.
 rr=R/'results/physical_cp_reference_actual_restore_20261104.json';recovery=read(rr);ref=Path(recovery['restored_root'])
 for n,h in recovery['file_sha256'].items():assert sha(ref/n)==h
 ra=read(ref/'source_bound_audit.json');assert ra==read(recovery['report'])['audit']
 assert sha(recovery['archive'])==recovery['archive_sha256']
 assert timing_summary(ref/'timing_routed.rpt')==ra['timing_summaries']['routed']
 assert utilization(ref/'utilization_routed.rpt')==ra['resources']['routed']
 assert route_status(ref/'route_status.rpt')==ra['route']
 assert commands(ref/'constraints_routed.xdc')==commands(p/'constraints_routed.xdc')
 refpaths=parse_report((ref/'timing_routed.rpt').read_text(),'core_clk');refworst=min((x for x in refpaths if x['path_type']=='Setup'),key=lambda x:x['slack_ns'])
 comparison=dict(reference_report=recovery['report'],reference_restore_sha256=sha(rr),resources={k:dict(reference=ra['resources']['routed'][k],candidate=a['resources']['routed'][k],delta=a['resources']['routed'][k]-ra['resources']['routed'][k]) for k in ['LUT','FF','BRAM','DSP','URAM']},
 timing={k:dict(reference=ra['timing_summaries']['routed'][k],candidate=a['timing_summaries']['routed'][k],delta=round(a['timing_summaries']['routed'][k]-ra['timing_summaries']['routed'][k],6)) for k in ['WNS_ns','TNS_ns','WHS_ns']},
 setup_failing_endpoints=dict(reference=ra['timing_summaries']['routed']['failing_endpoints']['setup'],candidate=a['timing_summaries']['routed']['failing_endpoints']['setup']),reference_drc=table(ref/'drc_routed.rpt'),
 reference_worst_path=refworst,limitations='Same tool/device/10ns OOC conditions and routed stage; different source, mapping, placement and endpoints. This is not a same-path causal experiment, Fmax or board performance measurement.')
 report=dict(status='physical_v6_terminal_main_reviewed_artifacts_valid_timing_and_drc_not_met',time_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),reviewer_sha256=sha(__file__),
 audit=a,physical_artifacts_validated=True,full_system_functional_netlist_validated=True,physical_gate_open=True,timing_qualified=False,board_acceptance=False,
 archive=t['archive'],archive_sha256=t['archive_sha256'],files=len(files),archive_original_restored_all_sha_identical=True,readonly_original_auditor_evidence_assertions_passed=True,
 readonly_auditor_prefix_sha256=hashlib.sha256(prefix.encode()).hexdigest(),original_and_restored_audits_byte_identical=True,terminal_processes=processes,memory_admission=admission,
 diagnostics=diagnostics,drc=drc,methodology=methods,reported_paths=paths,worst_setup_path=worst,comparison=comparison,
 interpretation=['Complete routing and reproducible reports accepted as physical evidence; setup fails and DRC remains nonzero.',
 'No Critical Warning lines in execution log is not a DRC clean result: NSTD-1 and UCIO-1 are Critical Warning entries in report_drc for cp_m_index[3]. No severity overrides or waivers applied.',
 'Worst reported setup path has 48 logic levels, 13.394ns data delay (3.479ns logic,9.915ns net). It crosses control/fault/ready logic to search request payload CE. Reported-path evidence does not identify every failing endpoint.',
 'Compared with CP, routed area and worst slack improve, but TNS is more negative and setup failing endpoints increase. Do not claim overall timing closure or end-to-end speedup.',
 'OOC input/output budgets and physical clock source/port placement remain unspecified; methodology and missing-delay counts retained.',
 'start/release counterexample remains open; isolated one-line candidate is untested and not part of this source revision.'],
 controls_rerun=False,full_shadow_rerun=False,implementation_rerun=False,production_rtl_modified=False,
 evidence_sha256={str(x):sha(x) for x in [receipt,s/'manifest.json',p/'manifest.json',p/'inspection/manifest.json',p/'source_bound_audit.json',rr,Path(recovery['report']),auditor,R/'results/stage_static_cp_physical_v6_preparation_review_20261104.json',R/'results/stage_static_cp_physical_v6_launch_review_20261104.json']})
 with out.open('x') as f:f.write(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print('PHYSICAL_V6_MAIN_REVIEWED',len(files),a['timing_summaries']['routed']['WNS_ns'],drc['total'])
if __name__=='__main__':main()
