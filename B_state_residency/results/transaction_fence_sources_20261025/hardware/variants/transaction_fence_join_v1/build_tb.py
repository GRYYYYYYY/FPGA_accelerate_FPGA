from pathlib import Path
import importlib.util,re,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent;W=2432;R=256
def module(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m
def metadata():
 h=(ROOT/'hardware/variants/candidate_recursive_v1/candidate_recursive_engine.sv').read_text().split(')(\n',1)[1].split('\n);',1)[0];info={};direction=None;width=1
 for tok in h.replace('\n',' ').split(','):
  tok=tok.strip();m=re.fullmatch(r'(input|output)\s+(?:wire|reg)\s*(?:\[(\d+):0\]\s*)?(\w+)',tok)
  if m:direction=m[1];width=int(m[2])+1 if m[2]else 1;name=m[3]
  else:
   assert re.fullmatch(r'\w+',tok),tok;name=tok
  info[name]=(direction,width)
 return info
def layout():
 c=module(ROOT/'hardware/variants/config_restore_join_v1/build_tb.py','config_layout');lanes=[]
 for p,fs in c.LANES:lanes.append(dict(v=p+'_cfg_valid',r=p+'_cfg_ready',q=[(p+'_cfg_'+f,w)for f,w,o in fs],rv=p+'_cfg_rsp_valid',rr=p+'_cfg_rsp_ready',a=[(p+'_cfg_status',3)]))
 for v,r,q,rv,rr,a in [
 ('host_ctrl_valid','host_ctrl_ready',['host_ctrl_op','host_ctrl_query','host_ctrl_price','host_ctrl_version'],'host_ctrl_rsp_valid','host_ctrl_rsp_ready',['host_ctrl_status']),
 ('host_design_req_valid','host_design_req_ready',['host_design_req_op','host_design_req_cookie','host_design_req_owner','host_design_req_node','host_design_req_arg'],'host_design_rsp_valid','host_design_rsp_ready',['host_design_rsp_status','host_design_rsp_cookie','host_design_rsp_flags','host_design_rsp_count','host_design_rsp_mask']),
 ('host_io_valid','host_io_ready',['host_io_write','host_io_node','host_io_value','host_io_field'],'host_io_rsp_valid','host_io_rsp_ready',['host_io_status','host_io_present','host_io_payload']),
 ('host_owner_req_valid','host_owner_req_ready',['host_owner_req_op','host_owner_req_cookie','host_owner_req_node','host_owner_req_net'],'host_owner_rsp_valid','host_owner_rsp_ready',['host_owner_rsp_status','host_owner_rsp_cookie','host_owner_rsp_count','host_owner_rsp_occupancy','host_owner_rsp_will_overuse']),
 ('cc_req_valid','cc_req_ready',['cc_req_words','cc_req_cookie','cc_req_version','cc_req_design_id','cc_req_query','cc_req_price'],'cc_rsp_valid','cc_rsp_ready',['cc_rsp_words','cc_rsp_cookie','cc_rsp_version','cc_rsp_design_id','cc_rsp_query','cc_rsp_status','cc_rsp_price']),
 ('expand_valid','expand_ready',['expand_connection','expand_cookie','expand_parent','expand_prune','expand_has_laguna','expand_sink','expand_net','expand_sequence','expand_flags','expand_xmin','expand_xmax','expand_ymin','expand_ymax','expand_version'],'result_valid','result_ready',['result_status','result_cookie','result_count','result_expanded_count','result_raw_count','result_mask','result_hit','result_early']),
 ('seed_valid','seed_ready',['seed_op','seed_key','seed_id','seed_cookie','seed_version'],'seed_rsp_valid','seed_rsp_ready',['seed_rsp_status','seed_rsp_cookie','seed_rsp_size','seed_rsp_key','seed_rsp_id']),
 ('cs_req_valid','cs_req_ready',['cs_req_host','cs_req_op','cs_req_cookie','cs_req_index','cs_req_value','cs_req_version','cs_req_query','cs_req_price'],'cs_rsp_valid','cs_rsp_ready',['cs_rsp_status','cs_rsp_cookie','cs_rsp_index','cs_rsp_version','cs_rsp_op','cs_rsp_host','cs_rsp_query','cs_rsp_price','cs_rsp_data'])]:
  info=metadata();lanes.append(dict(v=v,r=r,q=[(n,info[n][1])for n in q],rv=rv,rr=rr,a=[(n,info[n][1])for n in a]))
 lanes+=[dict(v='k_cfg_valid',r='k_cfg_ready',q=[('fa_authoritative',1),('fa_design',64),('fa_checkpoint',32),('fa_version',32),('fa_query',2),('fa_price',4)],rv='k_cfg_rsp_valid',rr='k_cfg_rsp_ready',a=[('k_cfg_status',1)]),dict(v='cf_load_valid',r='cf_load_ready',q=[('fc_payload',2304),('fc_design',64),('fc_checkpoint',32),('fc_authoritative',1)],rv='cf_load_rsp_valid',rr='cf_load_rsp_ready',a=[('cf_load_status',1)])]
 return lanes
def pins(text,instance):
 a=text.index(instance+'(')+len(instance)+1;pos=a;out={}
 while True:
  m=re.match(r'\s*\.(\w+)\(',text[pos:])
  if not m:break
  name=m[1];start=pos+m.end();i=start;depth=1
  while depth:
   if text[i]=='(':depth+=1
   if text[i]==')':depth-=1
   i+=1
  out[name]=text[start:i-1];pos=i
  if text[pos]==',':pos+=1
  else:break
 return out,a-len(instance)-1,pos+2

def make():
 parent=module(ROOT/'hardware/variants/config_restore_join_v1/build_tb.py','config_builder');s=parent.make().replace('assign recover_open=k_permit;', 'assign recover_open=k_permit&&!f_recovery_owned&&!k_rec_valid;');lanes=layout();info=metadata();decl='wire f_normal_retired,f_recovery_owned,f_fault;wire[3:0]f_phase;wire f_all_drained,f_backend_idle;\n'
 # Remove only old continuous assignments to front handshake/reply pins; fabric owns them now.
 fronts={x[k]for x in lanes for k in ['r','rv']}
 for name in fronts:s=re.sub(r'assign '+name+r'=[^;]*;','',s)
 # Native backend declarations and request decoding.
 reqsrc={'fa_authoritative':"1'b1",'fa_design':'design_id','fa_checkpoint':'k_checkpoint','fa_version':'k_cfg_version','fa_query':'k_cfg_query','fa_price':'k_cfg_price','fc_payload':'cf_input','fc_design':'k_saved_design','fc_checkpoint':'k_saved_checkpoint','fc_authoritative':"1'b1"}
 controlled={};wiring=''
 for i,x in enumerate(lanes):
  for name in [x['v'],x['r'],x['rv'],x['rr']]:decl+='wire fd_'+name+';\n';controlled[name]='fd_'+name
  for name,width in x['q']+x['a']:decl+='wire ['+str(width-1)+':0]fd_'+name+';\n';controlled[name]='fd_'+name
  wiring+=f'assign f_sv[{i}]={x["v"]};assign {x["r"]}=f_sr[{i}];assign {x["rv"]}=f_srv[{i}];assign f_srr[{i}]={x["rr"]};\n'
  off=0
  for name,width in x['q']:
   wiring+=f'assign f_sp[{i*W+off}+:{width}]={reqsrc.get(name,name)};assign fd_{name}=f_dp[{i*W+off}+:{width}];\n';off+=width
  if off<W:wiring+=f'assign f_sp[{i*W+off}+:{W-off}]=0;\n'
  off=0
  for name,width in x['a']:
   wiring+=f'assign f_drp[{i*R+off}+:{width}]=fd_{name};assign {name}=f_srp[{i*R+off}+:{width}];\n';off+=width
  if off<R:wiring+=f'assign f_drp[{i*R+off}+:{R-off}]=0;\n'
  wiring+=f'assign fd_{x["v"]}=f_dv[{i}];assign f_dr[{i}]=fd_{x["r"]};assign f_drv[{i}]=fd_{x["rv"]};assign fd_{x["rr"]}=f_drr[{i}];\n'
 # No old assignments drive other front reply/data fields; those originally came from instances.
 # Route host label/owner services remain behind the saved-path route adapter.
 rp,ra,rb=pins(s,'route_join');assert rp
 for lane,prefix in [(8,'l'),(9,'o')]:
  x=lanes[lane]
  names=([('valid',x['v']),('ready',x['r']),('write','host_io_write'),('node','host_io_node'),('value','host_io_value'),('field','host_io_field'),('rsp_valid',x['rv']),('rsp_ready',x['rr']),('status','host_io_status'),('present','host_io_present'),('payload','host_io_payload')]if lane==8 else [('valid',x['v']),('ready',x['r']),('op','host_owner_req_op'),('node','host_owner_req_node'),('net','host_owner_req_net'),('cookie','host_owner_req_cookie'),('rsp_valid',x['rv']),('rsp_ready',x['rr']),('status','host_owner_rsp_status'),('rsp_cookie','host_owner_rsp_cookie'),('count','host_owner_rsp_count'),('occupancy','host_owner_rsp_occupancy'),('will_overuse','host_owner_rsp_will_overuse')])
  for field,name in names:rp['h_'+prefix+'_'+field]='fd_'+name
 rp.update(admit='!fault&&!busy',backend_drained='f_all_drained',req_valid='f_broute_valid',req_ready='f_broute_ready',rsp_valid='f_broute_rsp_valid',rsp_ready='f_broute_rsp_ready')
 for field,off,width in [('op',0,1),('slot',1,1),('cookie',2,32),('source',34,32),('sink',66,32),('net',98,32),('sequence',130,32)]:rp['req_'+field]=f'f_broute_payload[{off}+:{width}]'
 s=s[:ra]+'route_join('+','.join('.'+k+'('+v+')'for k,v in rp.items())+');'+s[rb:]
 s=re.sub(r'assign rc_req_ready=[^;]*;','',s)
 # Native engine: all 14 service interfaces are fabric backend signals, except adapter-owned label/owner.
 a=s.index('candidate_recursive_engine #');b=s.index('\n',a);line=s[a:b];prefix=line[:line.index('dut(')]
 overrides={k:v for k,v in controlled.items()if k in info and k not in {n for x in lanes[8:10]for n in [x['v'],x['r'],x['rv'],x['rr']]+[z for z,w in x['q']+x['a']]}}
 overrides['retired_idle']='f_backend_idle'
 for k,v in [('host_io_valid','b_l_valid'),('host_io_ready','b_l_ready'),('host_io_write','b_l_write'),('host_io_node','b_l_node'),('host_io_value','b_l_value'),('host_io_field','b_l_field'),('host_io_rsp_valid','b_l_rsp_valid'),('host_io_rsp_ready','b_l_rsp_ready'),('host_io_status','b_l_status'),('host_io_present','b_l_present'),('host_io_payload','b_l_payload'),('host_owner_req_valid','b_o_valid'),('host_owner_req_ready','b_o_ready'),('host_owner_req_op','b_o_op'),('host_owner_req_node','b_o_node'),('host_owner_req_net','b_o_net'),('host_owner_req_cookie','b_o_cookie'),('host_owner_rsp_valid','b_o_rsp_valid'),('host_owner_rsp_ready','b_o_rsp_ready'),('host_owner_rsp_status','b_o_status'),('host_owner_rsp_cookie','b_o_rsp_cookie'),('host_owner_rsp_count','b_o_count'),('host_owner_rsp_occupancy','b_o_occupancy'),('host_owner_rsp_will_overuse','b_o_will_overuse')]:overrides[k]=v
 s=s[:a]+prefix+'dut('+','.join('.'+k+'('+v+')'for k,v in overrides.items())+',.*);'+s[b:]
 # Native administrative services no longer connect directly to unbuffered frontend requests.
 for instance,lane,remap in [('recovery_ctl',14,{'cfg_valid':'v','cfg_ready':'r','cfg_rsp_valid':'rv','cfg_rsp_ready':'rr','cfg_status':'k_cfg_status','cfg_authoritative':'fa_authoritative','cfg_design':'fa_design','cfg_checkpoint':'fa_checkpoint','cfg_version':'fa_version','cfg_query':'fa_query','cfg_price':'fa_price'}),('config_restore',15,{'load_valid':'v','load_ready':'r','load_rsp_valid':'rv','load_rsp_ready':'rr','load_status':'cf_load_status','load_authoritative':'fc_authoritative','load_payload':'fc_payload','load_design':'fc_design','load_checkpoint':'fc_checkpoint'})]:
  pp,a,b=pins(s,instance)
  for port,key in remap.items():pp[port]='fd_'+(lanes[lane][key]if key in ['v','r','rv','rr']else key)
  if instance=='recovery_ctl':
   pp.update(recover_valid='f_brecover_valid',recover_ready='f_brecover_ready',rsp_valid='f_brecover_rsp_valid',rsp_ready='f_brecover_rsp_ready')
   pp['abort']='f_fault||'+pp['abort']
   for port,off,width in [('o_status',0,4),('o_rsp_cookie',4,32),('o_count',36,32),('o_occupancy',68,32)]:pp[port]=f'f_cbrp[{9*R+off}+:{width}]'
  s=s[:a]+instance+'('+','.join('.'+k+'('+v+')'for k,v in pp.items())+');'+s[b:]
 # Callback request packing and reply routing, with all old per-TB mux assignments removed.
 for name in ['cf_ready','cf_replies','cf_status','lr_c_ready','lr_l_ready','lr_l_rsp_valid','k_o_ready','k_o_rsp_valid']:
  s=re.sub(r'assign '+name+r'=[^;]*;','',s)
 callbacks='assign f_cbv={6\'d0,k_o_valid,lr_l_valid,1\'b0,lr_c_valid,cf_valid};\n'
 callbacks+='assign cf_ready=f_cbr[5:0];assign cf_replies=f_cbrv[5:0];\n'
 for i in range(6):callbacks+=f'assign f_cbp[{i*W}+:{384}]=cf_payload[{i*384}+:384];assign f_cbp[{i*W+384}+:{W-384}]=0;assign cf_status[{i*3}+:3]=f_cbrp[{i*R}+:3];assign f_cbrr[{i}]=cf_reply_ready[{i}];\n'
 cb_fields={6:[('lr_c_op',2),('lr_c_query',2),('lr_c_price',4),('lr_c_version',32)],8:[('lr_l_write',1),('lr_l_node',32),('lr_l_value',32),('lr_l_field',3)],9:[('k_o_op',3),('k_o_cookie',32),('k_o_node',32),('k_o_net',32)]}
 for i in range(6,16):
  off=0
  for name,width in cb_fields.get(i,[]):callbacks+=f'assign f_cbp[{i*W+off}+:{width}]={name};\n';off+=width
  callbacks+=f'assign f_cbp[{i*W+off}+:{W-off}]=0;\n'
  callbacks+=f'assign f_cbrr[{i}]='+({6:'lr_c_rsp_ready',8:'lr_l_rsp_ready',9:'k_o_rsp_ready'}.get(i,"1'b0"))+';\n'
 callbacks+='assign lr_c_ready=f_cbr[6];assign lr_l_ready=f_cbr[8];assign lr_l_rsp_valid=f_cbrv[8];assign k_o_ready=f_cbr[9];assign k_o_rsp_valid=f_cbrv[9];\n'
 pp,a,b=pins(s,'label_restore');pp.update(c_rsp_valid='f_cbrv[6]',c_status=f'f_cbrp[{6*R}+:4]',l_status=f'f_cbrp[{8*R}+:4]',l_present=f'f_cbrp[{8*R+4}]',l_payload=f'f_cbrp[{8*R+5}+:160]');s=s[:a]+'label_restore('+','.join('.'+k+'('+v+')'for k,v in pp.items())+');'+s[b:]
 # All seven transport observers are tied to target reset; ownership FSM survives it.
 watches='wire[4:0]f_watch_idle,f_watch_fault;\n'
 for i,p in enumerate(['g','d','t','cs','q']):
  writes=p in ['d','cs'];args={'clk':'clk','rst':'rst','arvalid':p+'_m_arvalid','arready':p+'_m_arready','arlen':p+'_m_arlen','rvalid':p+'_m_rvalid','rready':p+'_m_rready','rlast':p+'_m_rlast'}
  for x in ['awvalid','awready','awlen','wvalid','wready','wlast','bvalid','bready']:args[x]=p+'_m_'+x if writes else ("8'd0"if x=='awlen'else"1'b0")
  args.update(drained=f'f_watch_idle[{i}]',fault=f'f_watch_fault[{i}]');watches+='axi_drain_watch f_watch_'+p+'('+','.join('.'+k+'('+v+')'for k,v in args.items())+');\n'
 watches+='assign f_all_drained=label_drained&&owner_drained&&(&f_watch_idle)&&!(|f_watch_fault);\n'
 # Buffered normal requests are already counted by the fabric. Admin itself is not normal work.
 s=s.replace('.normal_retired(k_normal_retired)', '.normal_retired(f_normal_retired)').replace('.backend_drained(label_drained&&owner_drained)', '.backend_drained(f_all_drained)')
 s=s.replace('prior_drained<=label_drained&&owner_drained;', 'prior_drained<=f_all_drained;').replace('if(!prior_drained||!k_normal_retired)', 'if(!prior_drained||!f_normal_retired)')
 # Native observer fields must refer to backend data rather than fenced frontend replies.
 s=s.replace('cycles,host_owner_rsp_status,host_owner_rsp_count,host_owner_rsp_occupancy',f'cycles,f_cbrp[{9*R}+:4],f_cbrp[{9*R+36}+:32],f_cbrp[{9*R+68}+:32]')
 s=s.replace('cycles,host_io_status,host_io_present,host_io_payload',f'cycles,f_cbrp[{8*R}+:4],f_cbrp[{8*R+4}],f_cbrp[{8*R+5}+:160]').replace('cycles,host_io_payload',f'cycles,f_cbrp[{8*R+5}+:160]').replace('cycles,label_restore.row[191:160],host_io_payload',f'cycles,label_restore.row[191:160],f_cbrp[{8*R+5}+:160]')
 # Initial host boot also honors independent handshakes (normal channels serialize).
 a=s.index(' @(negedge clk);q_cfg_valid=1;',s.index('initial begin\n trace=$fopen'));b=s.index(' control(0);',a)
 boot=''
 for x in lanes[:6]:boot+=f' @(negedge clk);{x["v"]}=1;do @(posedge clk);while(!{x["r"]});@(negedge clk);{x["v"]}=0;wait({x["rv"]});@(negedge clk);if({x["a"][0][0]})$fatal(1,"boot config");{x["rr"]}=1;@(negedge clk);{x["rr"]}=0;\n'
 s=s[:a]+boot+s[b:]
 # Replace old callback observers that used raw engine READY before the fabric buffered requests.
 s=s.replace('cf_valid[cx]&&cf_ready[cx]', 'cf_valid[cx]&&cf_ready[cx]')
 all_on='q_cfg_valid=1;g_cfg_valid=1;d_cfg_valid=1;t_cfg_valid=1;owner_cfg_valid=1;cs_cfg_valid=1;host_ctrl_valid=1;host_io_valid=1;host_owner_req_valid=1;host_design_req_valid=1;cc_req_valid=1;cs_req_valid=1;k_cfg_valid=1;cf_load_valid=1;'
 all_off=all_on.replace('=1;','=0;')
 s=s.replace('rc_req_valid=1;expand_valid=1;seed_valid=1;', 'rc_req_valid=1;expand_valid=1;seed_valid=1;'+all_on)
 s=s.replace('rc_req_valid=0;expand_valid=0;seed_valid=0;', '$fdisplay(trace,"FG %0d %0d",cycles,f_conflict_cycles);rc_req_valid=0;expand_valid=0;seed_valid=0;'+all_off)
 s=s.replace('CONFIG_RESTORE_JOIN_PASS','TRANSACTION_FENCE_JOIN_PASS')
 s=s.replace('version=%0d cycles=%0d",fault_case', 'version=%0d cycles=%0d contend=%0d",fault_case').replace('restore_epoch,restore_version,cycles);$finish;', 'restore_epoch,restore_version,cycles,f_conflict_cycles);$finish;')
 # Forward declarations prevent VRFC's use-before-declaration checks in generated instances.
 s=s.replace('module tb_candidate_offer;', 'module tb_candidate_offer;\n'+decl+(HERE/'fabric.inc').read_text(),1)
 s=s.replace('initial begin\n trace=$fopen',wiring+callbacks+watches+(HERE/'fabric_instance.inc').read_text()+'\ninitial begin\n trace=$fopen',1)
 s=s.replace('initial begin\n trace=$fopen',(HERE/'observer.inc').read_text()+'\ninitial begin\n trace=$fopen',1)
 return s
if __name__=='__main__':
 (HERE/'tb_transaction_fence_join.sv').write_text(make());(HERE/'layout.json').write_text(json.dumps(layout(),indent=2)+'\n')
