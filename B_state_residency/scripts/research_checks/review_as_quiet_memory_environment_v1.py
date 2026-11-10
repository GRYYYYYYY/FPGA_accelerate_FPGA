"""Check fixture/control-model compatibility, without claiming data/file equivalence."""
from pathlib import Path
import json,hashlib,tarfile
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');S=B/'stage_static_cp_shadow_system_v6/sources';P=B/'ka_reader_quiet_persistence_formal_v1'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def j(p):return json.loads(p.read_text())
h=(P/'harness.sv').read_text();tb=(S/'tb_query_fault.sv').read_text();mem=(S/'axi_file_memory.sv').read_text()
inst=tb.split('axi_file_memory #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.TAG("snapshot")) authority_memory(',1)[1].split(';',1)[0]
for s in ['.clk(clk)','.rst(k_cold_rst)','.arlen(as_m_arlen)','.arvalid(as_m_arvalid)','.arready(as_m_arready)','.rvalid(as_m_rvalid)','.rlast(as_m_rlast)','.rready(as_m_rready)',".inject_b(1'b0)",'.inject_r(as_inject)']:assert s in inst
assert '.hold_r(' not in inst
assert 'READ_DELAY=0' in mem and "if(hold_r===1'b1)" in mem
assert 'axi_file_memory_control #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.READ_DELAY(0)) memory(.clk(clk),.rst(rst)' in h
assert '(* anyseq *) reg hold_r;' in h
for name in ['m_rdata','m_rid','m_rresp','m_bid','m_bresp']:
 line=next(l for l in h.splitlines() if l.rstrip().endswith(' '+name+';'));assert '(* anyseq *)' in line
assert h.count('assume(')==1 and 'initial assume(rst);' in h
# Memory payload/status outputs are deliberately unconnected: the authority sees arbitrary values.
mapping=h.split(')) memory(',1)[1].split(';',1)[0]
for name in ['rdata','rid','rresp','bid','bresp']:assert '.'+name+'(' not in mapping
pr=j(P/'preparation.json')
for e in pr['configuration']['source_bindings'].values():assert sha(Path(e['source']))==e['sha256']
# The local memory differs from the reviewed source-derived control only by observed write flags.
parent=B/'ka_memory_control_equivalence_v3/memory_control.sv'
current=(P/'memory_control.sv').read_text();original=parent.read_text()
assert current.replace(' output wire obs_wp,obs_wend,\n','').replace('assign obs_wp=wp;assign obs_wend=wend;\n','')==original
reports=[R/'results/ka_reader_quiet_persistence_formal_v1_review_20261101.json',R/'results/ka_memory_control_equivalence_v3_review_20261031.json',R/'results/ka_dual_bank_memory_pending_formal_v2_review_20261101.json']
for p in reports:assert p.exists()
cap=B/'ka_as_quiet_memory_environment_evidence_v1';cap.mkdir();files={'reviewer.py':Path(__file__),'harness.sv':P/'harness.sv','memory_control.sv':P/'memory_control.sv','source_memory.sv':S/'axi_file_memory.sv','source_tb.sv':S/'tb_query_fault.sv','preparation.json':P/'preparation.json'}
for p in reports:files['reports/'+p.name]=p
with tarfile.open(cap/'evidence.tar','w') as t:
 for n,p in files.items():t.add(p,arcname=n,recursive=False)
with tarfile.open(cap/'evidence.tar') as t:t.extractall(cap/'restored',filter='data')
for n,p in files.items():assert sha(p)==sha(cap/'restored'/n)
d={'status':'current_fixture_quiet_memory_control_environment_compatibility_reviewed','findings':['Actual authority memory and authority share clk/k_cold_rst, matching formal common reset.','Actual READ_ONLY1/MAX_BEATS1/default READ_DELAY0 match local control parameters.','Actual unconnected hold_r is Z and hold occurs only for ===1; arbitrary formal hold_r includes the actual no-hold trace. This is a two-state embedding, not a general XZ proof.','Actual injected RRESP and memory data/ID values are included in arbitrary local response fields. No data/status assumptions were introduced.','Source-derived memory control is identical apart from two read-only observation aliases; previously reviewed control miter remains required.'],'scope':'Control-trace compatibility for this legal, nonfatal fixture environment. No file/address/data or fatal-stop equivalence; no arbitrary external AXI/environment claim.','remaining':['Finish configured-contract and quiet-to-ready integration audit.','No full shadow acceptance or stalled coverage waiver follows from this review.'],'archive_sha256':sha(cap/'evidence.tar'),'file_sha256':{n:sha(p) for n,p in files.items()},'full_system_functional_netlist_validated':False,'physical_gate_open':False}
out=R/'results/ka_as_quiet_memory_environment_review_20261101.json';assert not out.exists();out.write_text(json.dumps(d,indent=2)+'\n');print(d['status'],d['archive_sha256'])
