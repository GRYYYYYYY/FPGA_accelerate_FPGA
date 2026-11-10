"""Deterministic source sanitization of file side effects; compare read control only."""
from pathlib import Path
import re,json,hashlib
R=Path(__file__).resolve().parents[2];B=Path('/tmp/B_state_residency_offer_20261025');p=B/'ka_memory_control_equivalence_v1';assert not p.exists();src=B/'stage_static_cp_shadow_system_v6/sources/axi_file_memory.sv';original=src.read_text();s=original;changes=[]
def remove(start,end,label):
 global s
 i=s.index(start);j=s.index(end,i)+len(end);changes.append({'kind':label,'removed':s[i:j]});s=s[:i]+s[j:]
remove(' task decode(', '\n endtask','address decode task; only file selection and range fatal')
remove(' initial begin','\n end\n','file opening/plusargs initial process')
# Balance parentheses and strings; record every replaced call exactly.
pattern=re.compile(r'\$(fatal|fdisplay|fflush|fwrite|fseek|fread)\s*\(|\bdecode\s*\(')
while True:
 m=pattern.search(s)
 if not m:break
 start=m.start();i=m.end();depth=1;quoted=False;escaped=False
 while depth:
  c=s[i];i+=1
  if quoted:
   if escaped:escaped=False
   elif c=='\\':escaped=True
   elif c=='"':quoted=False
  elif c=='"':quoted=True
  elif c=='(':depth+=1
  elif c==')':depth-=1
 name=m.group(1) if m.group(1) else 'decode';value=name in ['fseek','fread'];end=i
 if not value:
  while s[end].isspace():end+=1
  assert s[end]==';';end+=1
 replacement='0' if value else 'begin end'
 changes.append({'kind':name,'removed':s[start:end],'replacement':replacement});s=s[:start]+replacement+s[end:]
assert not re.search(r'\$(?:fatal|fdisplay|fflush|fwrite|fseek|fread|fopen|value\$plusargs)',s)
# Expose read control without changing its drivers.
observations={'rp':1,'rng':32,'rdpos':32,'rdlen':32,'delay_r':32}
s=s.replace('module axi_file_memory #(','module axi_file_memory_control #(',1)
needle=' input wire clk,rst,';assert needle in s
ports=','.join('output wire'+('['+str(w-1)+':0]' if w>1 else '')+' obs_'+n for n,w in observations.items())
s=s.replace(needle,' '+ports+',\n'+needle,1)
s=s.replace('endmodule','\n'+''.join('assign obs_'+n+'='+n+';\n' for n in observations)+'endmodule')
reference=(B/'ka_axi_read_pending_control_v2/harness.sv').read_text().split('reg past_valid=0;')[0]
reference=reference.replace('module ka_axi_read_pending_control(input wire clk);','module axi_read_control_reference(input wire clk,rst,arvalid,rready,hold_r,output wire arready,output reg rvalid,rlast,'+ports+');')
reference=reference.replace('(* anyseq *) reg rst, arvalid, rready, hold_r;\n','').replace('reg rp=0, rvalid, rlast, read_pending;','reg rp=0, read_pending;').replace('wire arready;\n','')
reference+='\n'+''.join('assign obs_'+n+'='+n+';\n' for n in observations)+'endmodule\n'
wrapper='''module ka_memory_control_equivalence(input wire clk);
(* anyseq *) reg rst, arvalid, rready, hold_r;
wire a_ready,a_valid,a_last,b_ready,b_valid,b_last;
'''
for n,w in observations.items():wrapper+='wire '+('['+str(w-1)+':0] ' if w>1 else '')+'a_'+n+',b_'+n+';\n'
common='.clk(clk),.rst(rst),.arvalid(arvalid),.rready(rready),.hold_r(hold_r)'
wrapper+='axi_read_control_reference ref_dut('+common+',.arready(b_ready),.rvalid(b_valid),.rlast(b_last),'+','.join('.obs_'+n+'(b_'+n+')' for n in observations)+');\n'
wrapper+='axi_file_memory_control #(.ADDR_BITS(64),.READ_ONLY(1),.MAX_BEATS(1),.READ_DELAY(0)) source_dut('+common+",.arlen(8'd0),.arsize(3'd6),.arburst(2'd1),.arid(4'd0),.araddr(64'd0),.arready(a_ready),.rvalid(a_valid),.rlast(a_last),.inject_r(1'b0),.inject_b(1'b0),.awvalid(1'b0),.wvalid(1'b0),.bready(1'b0),"+','.join('.obs_'+n+'(a_'+n+')' for n in observations)+');\n'
wrapper+='reg past_valid=0;\ninitial assume(rst);\nalways @(posedge clk)begin\n past_valid<=1;\n if(past_valid)begin\n assert(a_ready==b_ready);\n assert(a_valid==b_valid);\n assert(a_last==b_last);\n'+''.join(' assert(a_'+n+'==b_'+n+');\n' for n in observations)+' end\n cover(past_valid && !rst && a_valid && rready);\nend\nendmodule\n'
p.mkdir();(p/'memory_control.sv').write_text(s);(p/'reference.sv').write_text(reference);(p/'harness.sv').write_text(wrapper)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
receipt={'status':'prepared_source_sanitized_read_control_equivalence_only','source_sha256':{str(src):sha(src),str(B/'ka_axi_read_pending_control_v2/harness.sv'):sha(B/'ka_axi_read_pending_control_v2/harness.sv'),str(p/'memory_control.sv'):sha(p/'memory_control.sv'),str(p/'reference.sv'):sha(p/'reference.sv')},'harness_sha256':sha(p/'harness.sv'),'transformations':changes,'observations':observations,'limits':['Removed file side effects and fatal stops: control comparison applies to continuing legal fixture traces, not file validity or data/status equivalence.','Source retained read branch and original read control assignments; writes disabled by READ_ONLY1/awvalid0/wvalid0.','Not dual-bank/shared-reset integration or full-system acceptance.'],'full_system_functional_netlist_validated':False,'physical_gate_open':False};(p/'projection.json').write_text(json.dumps(receipt,indent=2)+'\n');print(p)
