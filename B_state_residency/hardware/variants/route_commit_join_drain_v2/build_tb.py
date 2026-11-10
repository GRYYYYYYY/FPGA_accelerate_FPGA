from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/route_commit_join_v1/tb_route_join.sv').read_text()
 s=s.replace(".active(p_active),.admit", ".active(p_active),.backend_drained(label_drained&&owner_drained),.admit").replace('.admit(!busy&&','.admit(!fault&&!busy&&')
 monitors='wire label_drained,owner_drained,label_watch_fault,owner_watch_fault;\n'
 for prefix,tag in [('p_m','label'),('owner_m','owner')]:
  connections=','.join('.'+field+'('+prefix+'_'+field+')'for field in ['arvalid','arready','arlen','rvalid','rready','rlast','awvalid','awready','awlen','wvalid','wready','wlast','bvalid','bready'])
  monitors+='axi_drain_watch '+tag+'_watch(.clk(clk),.rst(rst),'+connections+',.drained('+tag+'_drained),.fault('+tag+'_watch_fault));\n'
 s=s.replace('route_commit_host_adapter #',monitors+'route_commit_host_adapter #',1)
 s=s.replace(' if(rc_block)begin',' if(label_watch_fault||owner_watch_fault)$fatal(1,"physical AXI watch fault");\n if(rc_rsp_valid&&!(label_drained&&owner_drained))$fatal(1,"completion before AXI drain");\n if(rc_block)begin')
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_route_join_drain.sv').write_text(make())
