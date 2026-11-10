from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
LANES=[('q', [('base',64,0),('design',64,64),('connections',32,128),('nodes',32,160),('nets',32,192),('revision',32,224)]),('g',[('offsets_base',64,0),('edges_base',64,64),('attrs_base',64,128),('nodes',32,192),('edges',32,224)]),('d',[('base',64,0),('nodes',32,64)]),('t',[('rows_base',64,0),('columns_base',64,64),('rows',32,128),('columns',32,160)]),('owner',[('primary',64,0),('pool',64,64),('allocator',64,128),('nodes',32,192),('capacity',32,224)]),('cs',[('history',64,0),('prices',64,64),('nets',64,128),('design_id',64,192),('nodes',32,256),('net_count',32,288),('version',32,320)])]
def make():
 p=ROOT/'hardware/variants/label_restore_join_v1/build_tb.py';sp=importlib.util.spec_from_file_location('label_builder',p);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);s=mod.make()
 s=s.replace('module tb_candidate_offer;', 'module tb_candidate_offer;\nwire cf_busy,cf_fault,cf_rsp_valid;wire[31:0]cf_rsp_cookie;',1)
 s=s.replace('k_rsp_ready=0,k_rcfg_done=0;','k_rsp_ready=0;wire k_rcfg_done;')
 s=s.replace('.abort(lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=32\'he0010001))', '.abort(cf_fault||(cf_rsp_valid&&cf_rsp_cookie!=32\'hf0010001)||lr_fault||(lr_rsp_valid&&lr_rsp_cookie!=32\'he0010001))')
 extra=''
 for lane,(prefix,fields)in enumerate(LANES):
  old='assign '+prefix+'_cfg_ready=!rc_block&&raw_'+prefix+'_cfg_ready;';assert old in s;s=s.replace(old,'assign '+prefix+'_cfg_ready=!cf_busy&&!rc_block&&raw_'+prefix+'_cfg_ready;')
  old='.'+prefix+'_cfg_valid(('+prefix+'_cfg_valid&&!rc_block))';assert old in s;s=s.replace(old,'.'+prefix+'_cfg_valid(((cf_busy?cf_valid['+str(lane)+']:'+prefix+'_cfg_valid)&&!rc_block))')
  extra+='.'+prefix+'_cfg_rsp_ready(cf_busy?cf_reply_ready['+str(lane)+']:'+prefix+'_cfg_rsp_ready),'
  for field,width,offset in fields:
   n=prefix+'_cfg_'+field
   extra+='.'+n+'(cf_busy?cf_payload['+str(lane*384+offset)+'+:'+str(width)+']:'+n+'),'
 s=s.replace('.cs_cfg_ready(raw_cs_cfg_ready),.*);','.cs_cfg_ready(raw_cs_cfg_ready),'+extra+'.*);')
 s=s.replace('route_commit_host_adapter #',(Path(__file__).parent/'controller.inc').read_text()+'\nroute_commit_host_adapter #',1)
 a=s.index('task configure_all;');b=s.index('task install_checkpoint;',a);s=s[:a]+s[b:]
 a=s.index(' restore_epoch=k_new_query;restore_version=k_new_version;cs_cfg_version=k_new_version;')
 b=s.index(' wait(k_labels_valid);',a)
 s=s[:a]+''' restore_epoch=k_new_query;restore_version=k_new_version;
 rc_req_valid=1;expand_valid=1;seed_valid=1;
 wait(!k_rcfg_valid);
'''+s[b:]
 s=s.replace('install_checkpoint;', 'install_checkpoint;install_config_snapshot;')
 # The replacement above also touches the task declaration; restore its name.
 s=s.replace('task install_checkpoint;install_config_snapshot;','task install_checkpoint;')
 task='''task install_config_snapshot;begin
 @(negedge clk);cf_load_valid=1;do @(posedge clk);while(!cf_load_ready);@(negedge clk);cf_load_valid=0;
 wait(cf_load_rsp_valid);@(negedge clk);if(cf_load_status)$fatal(1,"resident config install");
 $fdisplay(trace,"CL %0d %0d %0d",cycles,cf_saved_checkpoint,cf_load_status);
 cf_load_rsp_ready=1;@(negedge clk);cf_load_rsp_ready=0;
end endtask
'''
 s=s.replace('task install_checkpoint;',task+'task install_checkpoint;',1)
 s=s.replace('LABEL_RESTORE_JOIN_PASS','CONFIG_RESTORE_JOIN_PASS')
 s=s.replace('initial begin\n trace=$fopen',(Path(__file__).parent/'observer.inc').read_text()+'\ninitial begin\n trace=$fopen',1)
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_config_restore_join.sv').write_text(make())
