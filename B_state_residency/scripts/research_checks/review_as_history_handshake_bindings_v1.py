"""Review actual DRAIN/response handshake bindings; not a whole-system proof."""
from pathlib import Path
import hashlib,json,itertools,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(n):return (S/n).read_text()
def instance(text,marker):return text.split(marker,1)[1].split(';',1)[0]
def port(text,name):
 start=text.index('.'+name+'(')+len(name)+2;depth=1;i=start
 while depth:
  if text[i]=='(':depth+=1
  elif text[i]==')':depth-=1
  i+=1
 return ''.join(text[start:i-1].split())
q=read('query_residency_system.sv');r=read('residency_system.sv');c=read('recovery_coordinator.sv')
a=instance(q,'checkpoint_authority_rotator authority(');k=instance(r,' recovery_ctl(')
expected_a={'clk':'clk','rst':'k_cold_rst','abort':"1'b0",'req_valid':'!ap_owned&&(k_a_valid||ap_offer)','req_ready':'ap_native_ready','rsp_valid':'ap_native_valid','rsp_ready':'ap_owned?ap_rsp_ready:k_a_rsp_ready','busy':'as_busy','fault':'as_fault','drained':'as_drained'}
expected_k={'clk':'clk','cold_rst':'k_cold_rst','backend_drained':'f_all_drained','normal_retired':'f_normal_retired&&as_retired&&(!wm_on||wm_services_retired)','a_valid':'k_a_valid','a_ready':'k_a_ready','a_rsp_valid':'k_a_rsp_valid','a_rsp_ready':'k_a_rsp_ready'}
for n,v in expected_a.items():assert port(a,n)==v
for n,v in expected_k.items():assert port(k,n)==v
assert '||as_fault||' in port(k,'abort')
required={
'query_residency_system.sv':['assign as_retired=!as_busy&&!as_core_cfg_valid;','assign k_a_rsp_valid=!ap_owned&&ap_native_valid;','assign k_a_ready=!ap_offer&&!ap_owned&&ap_native_ready;','wire ap_offer=ap_allow&&ap_valid;'],
'residency_system.sv':['assign f_all_drained=(!ENABLE_BASELINE||baseline_retired)&&as_drained&&label_drained&&owner_drained&&(&f_watch_idle)&&!(|f_watch_fault);'],
'recovery_coordinator.sv':['assign a_valid=!cold_rst&&state==AS;assign a_rsp_ready=!cold_rst&&state==AW;']}
for n,lines in required.items():
 for line in lines:assert line in read(n)
# Truth-table implication after expanding AND/OR context into arbitrary other terms.
drain_rows=0
for drained,busy,cfgrsp,fault,other_drained,other_retired,other_abort in itertools.product([False,True],repeat=7):
 backend=drained and other_drained;retired=(not busy and not cfgrsp) and other_retired;abort=fault or other_abort
 if backend and retired and not abort:assert not busy and drained and not fault;drain_rows+=1
# With AP-owned absent, the actual two muxes preserve both response handshake terms.
response_rows=0
for owned,valid,ready,ap_ready in itertools.product([False,True],repeat=4):
 if owned:continue
 kvalid=not owned and valid;native_ready=ap_ready if owned else ready
 assert (kvalid and ready)==(valid and native_ready);response_rows+=1
reports=[R/'results/ka_as_ready_history_composition_receipt_review_20261101.json',R/'results/ka_reader_quiet_persistence_formal_v1_review_20261101.json',R/'results/ka_as_no_ap_owned_formal_v1_review_20261031.json']
for p in reports:assert p.exists()
receipt=json.loads(reports[0].read_text());assert receipt['source_contract_integration_reviewed'] is False
# Recheck all receipt/archive-restoration entries, rather than trusting a status string.
for n,h in receipt['file_sha256'].items():
 original=R/n[5:] if n.startswith('repo/') else B/n
 restored=B/'ka_as_ready_history_receipt_evidence_v1/restored'/n
 assert sha(original)==h==sha(restored)
cap=B/'ka_as_history_handshake_bindings_evidence_v1';cap.mkdir()
files={'reviewer.py':Path(__file__)}
for n in required:files['sources/'+n]=S/n
for p in reports:files['reports/'+p.name]=p
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
report={'status':'actual_drain_and_response_handshake_source_bindings_reviewed_phase_contract_integration_pending','authority_ports':expected_a,'coordinator_ports':expected_k,'drain_satisfying_rows':drain_rows,'response_rows':response_rows,'findings':['Successful DRAIN retirement conditions imply authority !busy, drained and !fault in the same sampled cycle.','Coordinator and authority share clk/k_cold_rst; authority abort is constant zero, unlike aggregate coordinator abort.','If independently proven AP-owned is absent, AW valid/ready handshake is exactly authority response handshake.','Conditional proof retained trace contains AS steps6 and11; all receipt originals and restored files rehashed.'],'remaining':['Independently discharge phase-wide admin exclusion and AP-owned absence for the quiet-persistence contract, including DRAIN.','Bind configured guarantee and quiet-to-ready condition without circular reasoning.','Review memory/reset/environment compatibility for all component composition.'],'source_contract_integration_reviewed':False,'full_system_functional_netlist_validated':False,'physical_gate_open':False,'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(p) for n,p in files.items()}}
out=R/'results/ka_as_history_handshake_bindings_review_20261101.json';assert not out.exists();out.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'status':report['status'],'archive_sha256':report['archive_sha256'],'files':len(files)}))
