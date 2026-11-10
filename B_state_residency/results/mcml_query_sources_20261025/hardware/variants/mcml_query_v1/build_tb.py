"""Same closed-loop natural TB, MCML identities/sizes and EARLY drain counts."""
from pathlib import Path
import re
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/natural_stages_v1/tb_natural_stages.sv').read_text()
 values={9089009:14991410,40469536:66907822,145424192:239862592,145424256:239862656,36804480:61102400,11540864:14388416,36356040:59965644,161878144:267631288,290848288:479725120,36356096:59965696,36357120:59966720,65185:41486,150697:41981,16506:89391,2717:28747,27960:70980,180326:224819,308:282}
 # Numeric literals occur both with and without sized decimal prefixes.
 for a,b in values.items():s=re.sub(r'(?<![0-9])'+str(a)+r'(?![0-9])',str(b),s)
 for a,b in [('poll_i!=73','poll_i!=82'),('expand_i!=72','expand_i!=81'),('candidate_i!=271','candidate_i!=326'),('commits!=171','commits!=178'),('offers!=171','offers!=178'),('physical_expands!=72','physical_expands!=81'),('metadata_calls!=271','metadata_calls!=326')]:assert a in s;s=s.replace(a,b)
 for a,b in [('expand_xmin=38;expand_xmax=46;expand_ymin=283;expand_ymax=295','expand_xmin=26;expand_xmax=33;expand_ymin=40;expand_ymax=52'),('out_config[351:320]!=38','out_config[351:320]!=26'),('out_config[383:352]!=46','out_config[383:352]!=33'),('out_config[415:384]!=283','out_config[415:384]!=40'),('out_config[447:416]!=295','out_config[447:416]!=52')]:assert a in s;s=s.replace(a,b)
 decl='integer parent_trace,parent_reads=0,parent_writes=0;\n'
 s=s.replace('module tb_candidate_offer;','module tb_candidate_offer;\n'+decl,1)
 check='''`ifdef PARENT_CACHE
 if(parent_reads!=59)$fatal(1,"cached parent reads=%0d",parent_reads);
`else
 if(parent_reads!=178)$fatal(1,"baseline parent reads=%0d",parent_reads);
`endif
 if(parent_writes!=178)$fatal(1,"prev writes=%0d",parent_writes);
'''
 s=s.replace(' if(poll_i!=82',check+' if(poll_i!=82',1)
 observer='''initial begin parent_trace=$fopen("parent_trace.txt","w");if(!parent_trace)$fatal(1,"parent trace open");end
always @(posedge clk)if(!rst)begin
 if(dut.pl_valid&&dut.pl_ready)begin
  if(dut.pl_write)parent_writes<=parent_writes+1;else parent_reads<=parent_reads+1;
  $fdisplay(parent_trace,"N %0d %0d %0d %0d %0d %08h",cycles,dut.held_parent,out_node,dut.pl_node,dut.pl_write,dut.pl_value);$fflush(parent_trace);
 end
end
'''
 return s[:-len('endmodule\n')]+observer+'endmodule\n'
if __name__=='__main__':Path(__file__).with_name('tb_mcml_query.sv').write_text(make())
