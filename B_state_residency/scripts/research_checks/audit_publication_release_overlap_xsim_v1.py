"""Independently verify four-state reproduction; preserve failed invariant verdict."""
from pathlib import Path
import json,hashlib,re,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_publication_release_overlap_xsim_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
m=j(p/'manifest.json');assert m['status']=='reproduction_observed'
for n,h in m['sources'].items():assert sha(p/n)==h
for c in m['commands']:assert c['exit_code']==0 and sha(p/(c['stage']+'.stdout.log'))==c['stdout_sha256']
S=B/'stage_static_cp_shadow_system_v6/sources'
for n in ['checkpoint_lease_guard.sv','checkpoint_publish_barrier.sv']:assert (p/n).read_bytes()==(S/n).read_bytes()
log=(p/'simulate.log').read_text();assert 'xsim v2022.2' in log
for marker in m['expected_markers']:assert log.count(marker)==1
assert 'SIMULTANEOUS_ACCEPT time=55000 start=1 release=1' in log
assert 'OWNERSHIP_SPLIT time=56000 publication=1 lease=0' in log
assert 'REPRODUCTION_OBSERVED time=66000 status=3 publication=1 lease=0' in log
assert 'Fatal:' not in log and 'ERROR:' not in log
vcd=(p/'activity.vcd').read_text();assert '1ps' in vcd
names={};vals={};rows={};time=0
for l in vcd.splitlines():
 z=l.split()
 if not z:continue
 if z[0]=='$var':names[z[3]]=z[4]
 elif l.startswith('#'):
  rows[time]=dict(vals);time=int(l[1:])
 elif l.startswith('b'):
  bits,code=l[1:].split()
  if code in names:vals[names[code]]=int(bits,2) if all(c in '01' for c in bits) else bits
 elif l[0] in '01xz' and l[1:] in names:vals[names[l[1:]]]=int(l[0]) if l[0] in '01' else l[0]
rows[time]=dict(vals)
assert set(names.values())==set(m['wave_objects'])
def at(t):return rows[max(k for k in rows if k<=t)]
before=at(54000);split=at(56000);halt=at(66000)
assert all(before[n]==1 for n in ['pc_owned','start_valid','start_ready','release_valid','release_ready']) and before['jp_owned']==0
assert split['pc_owned']==0 and split['jp_owned']==1
assert halt['pc_owned']==0 and halt['jp_owned']==1 and halt['jp_done']==1 and halt['jp_status']==3
formal=R/'results/ka_publication_release_overlap_unit_v1_review_20261031.json';assert j(formal)['status']=='original_two_module_publication_start_and_lease_release_overlap_counterexample_preserved'
docs=[R/'hardware/variants/checkpoint_system_v1/CONTRACT.md',R/'hardware/variants/checkpoint_commit_v1/CONTRACT.md',R/'hardware/CONNECTION_CHECKPOINT_DESIGN.md']
tb=(S/'tb_query_fault.sv').read_text();task=tb.split('task iter2_publish_g2;',1)[1].split('end endtask',1)[0]
assert task.index('jp_start=1;')<task.index('wait(!jp_owned);')<task.index('pc_release_valid=1;')
cap=B/'ka_publication_release_overlap_xsim_evidence_v1';cap.mkdir();files={}
for f in p.rglob('*'):
 if f.is_file():files[str(f.relative_to(B))]=f
for f in [Path(__file__),R/'scripts/research_checks/run_publication_release_overlap_xsim_v1.py',R/'hardware/variants/ka_publication_release_overlap_xsim_v1/tb.sv',formal]+docs:files['repo/'+str(f.relative_to(R))]=f
files['bound_sources/tb_query_fault.sv']=S/'tb_query_fault.sv'
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,f in files.items():t.add(f,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,f in files.items():assert sha(f)==sha(cap/'restored'/n)
report={'status':'original_two_module_start_release_overlap_four_state_xsim_reproduced_preserved','backend':'XSim 2022.2 behavioral','top':'tb','observed_ns':{'simultaneous_accept':55,'ownership_split':56,'halt_status3':66},'test_observation_verdict':'expected_interface_overlap_reproduced','functional_invariant_verdict':'publication_owned_implies_lease_owned_failed_in_unit_context','formal_review_sha256':sha(formal),'vcd_objects':sorted(names.values()),'vcd_observations':{'before':before,'split':split,'halt':halt},'reviewed_contract_sha256':{str(f.relative_to(R)):sha(f) for f in docs},'contract_search_scope':'These reviewed contracts require finishing reply before releasing existing publication; no explicit prohibition of simultaneous idle-state publication start and lease release was found in these documents. Not an exhaustive claim about all caller contracts.','existing_tb_scope':'iter2_publish_g2 waits for !jp_owned before raising pc_release_valid; this serial scenario does not cover same-cycle new start/release.','mcp_preflight':'Two existing sessions report out of stack space; neither reused/stopped; local XSim 2022.2 fallback.','skill':'AMD Ross vivado-simulate-rtl with xsim/activity references; commands limited to available 2022.2 features.','scope':'Full original two modules and deterministic quiet interface inputs; four-state RTL reproduces initialized formal unit witness. Full query reachability/caller legality remain pending; no production change or functional gate acceptance.','archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(f) for n,f in files.items()},'reviewer_sha256':sha(Path(__file__)),'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_publication_release_overlap_xsim_v1_review_20261031.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
