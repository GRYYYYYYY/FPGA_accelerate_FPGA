"""Audit the expected old-root logical retirement deadlock after AXI read drain."""
from pathlib import Path
import sys,json
from run_checkpoint_authority import sha
from verify_rtl_bundle import verify
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();fixed=Path(sys.argv[2]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
old=(p/'sources/query_residency_system.sv').read_text();new=(fixed/'sources/query_residency_system.sv').read_text()
needle="wire[15:0]host_mask={16{host_open}}|({16{boot_admin_open}}&16'hc17f);"
patch=needle+'''
// Accepted host requests retain a response route even if admission is canceled.
reg[15:0]host_reply_owned;
always @(posedge clk)begin
 if(rst||k_cold_rst)host_reply_owned<=0;
 else host_reply_owned<=(host_reply_owned|(f_sv&f_sr))&~(f_srv&f_srr);
end
wire[15:0]host_response_mask=host_mask|host_reply_owned;'''
assert old.count(needle)==1
expected=old.replace(needle,patch).replace('assign f_srv=b_f_srv&host_mask;', 'assign f_srv=b_f_srv&host_response_mask;').replace('host_mask[i]&&f_srr[i]', 'host_response_mask[i]&&f_srr[i]');assert expected==new
assert sha(p/'sources/tb_cold_boot.sv')==sha(fixed/'sources/tb_cold_boot.sv')
d=p/'full_read';log=(d/'simulate.log').read_text();assert log.count('Fatal:')==1 and 'Fatal: accepted bootstrap response failed to retire after AXI cancel'in log and 'COLD_BOOT_PASS'not in log
ts=[l.split()for l in(d/'natural_trace.txt').read_text().splitlines()];cut=[t for t in ts if t[0]=='AXI_CANCEL_CUT'];timeout=[t for t in ts if t[0]=='AXI_CANCEL_TIMEOUT'];assert len(cut)==len(timeout)==1 and not any(t[0]=='AXI_HOST_REPLY'for t in ts)
assert timeout[0][2:6]==['2','1','0','0'] and timeout[0][6]==timeout[0][7]
case=m['cases']['full_read'];bundle=Path(case['bundle']);mf=verify(bundle)
rr=[(0,bytes(3145728))];physical=replay(d/'label_axi.txt',rr,d/'labels.bin');assert physical['error_read_beats']==physical['error_write_replies']==0
ar=[int(l.split()[2])for l in(d/'label_axi.txt').read_text().splitlines()if l.startswith('A ')];reads,beats,writes,bs=map(int,cut[0][3:]);assert sum(ar[:reads-1])==beats and sum(ar[:reads])>beats and physical['read_beats']==sum(ar)
r={'status':'passed','meaning':'Expected pre-fix logical deadlock after physical AXI drain, not a successful recovery.','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'fixed_run':str(fixed),'fixed_manifest_sha256':sha(fixed/'manifest.json'),'testbench_sha256':sha(p/'sources/tb_cold_boot.sv'),'failure':'accepted bootstrap response failed to retire after AXI cancel','timeout_phase':2,'physical_label_axi':physical,'scope':'Same complete-system stimulus; sole production delta is accepted host response ownership and separate response mask.'}
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('expected physical-drain/logical-deadlock counterexample audited')
