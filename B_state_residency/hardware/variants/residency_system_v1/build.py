"""Extract checked hardware connections from the audited join, excluding stimulus/file agents."""
from pathlib import Path
import importlib.util,re,json
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent
PARAM={'LANES':16,'REQ_BITS':2432,'RSP_BITS':256}
SOURCES={
'candidate_recursive_engine':ROOT/'hardware/variants/transaction_fence_join_v1/backend/candidate_recursive_engine.sv',
'route_commit_host_adapter':ROOT/'hardware/variants/recovery_join_v1/route_commit_host_adapter.sv',
'recovery_coordinator':ROOT/'hardware/variants/recovery_coordinator_v1/recovery_coordinator.sv',
'config_restore_controller':ROOT/'hardware/variants/config_restore_v1/config_restore_controller.sv',
'label_restore_controller':ROOT/'hardware/variants/label_restore_v1/label_restore_controller.sv',
'axi_drain_watch':ROOT/'hardware/variants/route_commit_join_drain_v2/axi_drain_watch.sv',
 'transaction_fence':ROOT/'hardware/variants/transaction_fence_static_v2/transaction_fence.sv'}

def load(path,name):
 sp=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(sp);sp.loader.exec_module(m);return m

def closing(s,start):
 assert s[start]=='(';n=1;i=start+1
 while n:
  n+=(s[i]=='(')-(s[i]==')');i+=1
 return i

def ports(path):
 s=re.sub(r'//[^\n]*','',path.read_text());a=s.index('module ');i=s.index('(',a)
 if '#'in s[a:i]:i=s.index('(',closing(s,i))
 block=s[i+1:closing(s,i)-1];out={};direction=None;width=1
 for tok in block.split(','):
  tok=tok.strip();m=re.match(r'(input|output|inout)\s+(?:(?:wire|reg|logic)\s*)?(?:\[([^:]+):0\]\s*)?(\w+)\s*$',tok)
  if m:
   direction=m[1];width=1 if m[2] is None else eval(m[2],{'__builtins__':{}},PARAM)+1;name=m[3]
  else:assert re.fullmatch(r'\w+',tok),tok;name=tok
  out[name]=(direction,width)
 return out

def ids(expr):
 expr=re.sub(r"\d+'[sS]?[bBoOdDhH][0-9a-fA-F_xXzZ]+",'',expr)
 return set(re.findall(r'\b[A-Za-z_]\w*\b',expr))

def extract(s):
 declarations={}
 for m in re.finditer(r'\b(?:wire|reg)\s*(?:\[(\d+):0\]\s*)?([^;]+);',s):
  width=int(m[1])+1 if m[1] else 1
  for item in m[2].split(','):
   name=item.strip().split('=')[0].strip()
   if not re.fullmatch(r'\w+',name):continue
   if name in declarations:assert declarations[name]==width,(name,width,declarations[name])
   declarations[name]=width
 instances=[];ranges=[]
 for module,path in SOURCES.items():
  pp=ports(path)
  for hit in re.finditer(r'\b'+module+r'\s*(?:#\([^;]*?\))?\s*(\w+)\s*\(',s):
   name=hit[1];start=hit.end()-1;end=closing(s,start);assert s[end]==';'
   head=s[hit.start():start+1];block=s[start+1:end-1];pos=0;bindings={}
   while pos<len(block):
    m=re.match(r'\s*\.(\w+)\(',block[pos:])
    if not m:break
    pstart=pos+m.end()-1;pend=closing(block,pstart);bindings[m[1]]=block[pstart+1:pend-1].strip();pos=pend
    if pos<len(block)and block[pos]==',':pos+=1
   rest=block[pos:].strip();assert rest in ['', '.*'],rest
   if rest=='.*':
    for n in pp:bindings.setdefault(n,n)
   assert set(bindings)==set(pp),(module,set(pp)-set(bindings),set(bindings)-set(pp))
   instances.append(dict(module=module,name=name,head=head,bindings=bindings,ports=pp));ranges.append((hit.start(),end+1))
 assert len(instances)==13,len(instances)
 assigns=[]
 for m in re.finditer(r'\bassign\s+([^;]+);',s):
  lhs,rhs=m[1].split('=',1);lname=re.match(r'\w+',lhs.strip())[0]
  # Packed host ABI and route/descriptor assembly stay in the external driver.
  if lname in ['f_sv','f_sp','f_srr','f_route_payload','cf_input'] or 'f_srp[' in rhs or 'f_sr['in rhs or 'f_srv['in rhs:continue
  assigns.append((lhs.strip(),rhs.strip()));ranges.append((m.start(),m.end()))
 # Continuous aliases declared as wire initializers are real hardware, too.
 assigns += [('rst','k_cold_rst||k_target_reset'),('lr_start_valid','k_labels_valid'),('lr_rsp_ready','!k_labels_valid')]
 return declarations,instances,assigns,ranges

def make():
 base=load(ROOT/'hardware/variants/transaction_fence_join_v1/build_tb.py','fjoin');s=base.make();decl,inst,assigns,ranges=extract(s)
 new_inputs={
  'recover_cookie':32,'recover_checkpoint':32,'recover_version':32,'recover_design':64,'recover_query':2,'recover_price':4,
  'snapshot_design':64,'snapshot_checkpoint':32,'snapshot_cookie':32,'snapshot_count':32,'snapshot_nodes':32,'snapshot_probe':32,'lr_s_cookie':32,
  'test_route_abort':1,'test_route_version_flip':1}
 decl.update(new_inputs)
 snapshot=[n for n in new_inputs if n.startswith('snapshot_')]
 for n in snapshot:decl[n+'_held']=decl[n]
 for x in inst:
  b=x['bindings'];name=x['name']
  if name=='route_join':
   b['abort']='ENABLE_TEST_INJECTION?test_route_abort:1\'b0';b['active_version']="query_version^((ENABLE_TEST_INJECTION&&test_route_version_flip)?32'd1:32'd0)"
  elif name=='recovery_ctl':
   for n in ['cookie','checkpoint','version','design','query','price']:b['recover_'+n]='recover_'+n
   b['abort']=b['abort'].replace("lr_rsp_cookie!=32'he0010001",'lr_rsp_cookie!=snapshot_cookie_held')
  elif name=='label_restore':
   for n,suffix in [('expected_design','design'),('expected_checkpoint','checkpoint'),('start_cookie','cookie'),('start_count','count'),('start_nodes','nodes'),('start_probe','probe')]:b[n]='snapshot_'+suffix+'_held'
   b['s_cookie']='lr_s_cookie'
 # Derive drivers and consumed nets from explicit pin directions and continuous assignments.
 driven=set();used=set();outwidth={}
 for x in inst:
  for p,expr in x['bindings'].items():
   direction,width=x['ports'][p];nets=ids(expr);used|=nets
   if direction=='output':
    assert not expr or re.fullmatch(r'\w+(?:\[[^\]]+\])?',expr),expr
    driven|=nets
    if expr and '['not in expr:
     assert decl.get(expr,width)==width,(expr,decl.get(expr),width);decl[expr]=width
 for lhs,rhs in assigns:used|=ids(lhs)|ids(rhs);driven|=ids(lhs)
 used|=set(snapshot)|{n+'_held'for n in snapshot};driven|={n+'_held'for n in snapshot}
 # These tokens are elaboration constants, not runtime ports.
 used-={'ENABLE_TEST_INJECTION'}
 missing=used-set(decl);assert not missing,missing
 inputs=used-driven
 # Export native core result/AXI/status signals and public control responses.
 core=next(x for x in inst if x['name']=='dut')
 outputs={expr for p,expr in core['bindings'].items() if core['ports'][p][0]=='output' and re.fullmatch(r'\w+',expr) and not expr.startswith(('fd_','b_'))}
 outputs|={'f_sr','f_srv','f_srp','rc_req_ready','rc_rsp_valid','rc_rsp_status','rc_rsp_cookie','rc_rsp_nodes','rc_rsp_acked','rc_slots','rc_fault','rc_busy','rc_block','k_rec_ready','k_rsp_valid','k_rsp_status','k_rsp_cookie','k_corrected','k_count','k_full','k_fault','k_busy','k_permit','k_target_reset','k_saved_design','k_saved_checkpoint','lr_s_ready','lr_rsp_status','lr_written','lr_verified','lr_fault','cf_fault','f_fault','f_phase','f_normal_retired','f_recovery_owned','f_all_drained','f_backend_idle','rst'}
 outputs|={n for n in driven if n.startswith('k_a_')}
 assert outputs<=driven,outputs-driven
 assert not inputs&outputs
 interface={n:{'direction':'input'if n in inputs else 'output','width':decl[n]}for n in sorted(inputs|outputs)}
 # Fail rather than accidentally exporting a testbench variable as a hardware input.
 forbid={'cycles','armed','injected_abort','injected_drift','k_normal_retired','bench_rst','rc_req_slot','rc_req_sink','rc_req_sequence','k_checkpoint','k_cfg_version'}
 assert not inputs&forbid,inputs&forbid
 def wire(n,direction=None):return (direction+' 'if direction else '')+'wire '+('['+str(decl[n]-1)+':0] 'if decl[n]>1 else '')+n
 body=['`timescale 1ns/1ps','// Generated structural hardware. No file agents, CPU oracle or search stimulus.','module residency_system #(parameter integer SLOTS=32,FRAMES=16384,INDEX_BITS=14,HASH_BITS=15,ENABLE_TEST_INJECTION=0)(',',\n'.join(wire(n,interface[n]['direction'])for n in interface),');']
 for n in sorted(used-set(interface)-{n+'_held'for n in snapshot}):body.append(wire(n)+';')
 for n in snapshot:body.append('reg ['+str(decl[n]-1)+':0] '+n+'_held;')
 body += ['always @(posedge clk)begin',' if(k_cold_rst)begin']+[f'  {n}_held<=0;'for n in snapshot]+[' end else if(k_rec_valid&&k_rec_ready)begin']+[f'  {n}_held<={n};'for n in snapshot]+[' end','end']
 for lhs,rhs in assigns:body.append('assign '+lhs+'='+rhs+';')
 for x in inst:body.append(x['head']+','.join('.'+p+'('+v+')'for p,v in x['bindings'].items())+');')
 body.append('endmodule')
 return '\n'.join(body)+'\n',interface,dict(declarations=decl,internal=sorted(used-set(interface)),instances=[x['name']for x in inst],input_names=sorted(inputs),output_names=sorted(outputs))

if __name__=='__main__':
 text,interface,meta=make();(HERE/'residency_system.sv').write_text(text);(HERE/'interface.json').write_text(json.dumps(interface,indent=2)+'\n');(HERE/'extraction.json').write_text(json.dumps(meta,indent=2)+'\n');print('SYSTEM_PORTS',len(interface),'inputs',len(meta['input_names']),'outputs',len(meta['output_names']))

def bench(kind):
 paths={'normal':'transaction_fence_normal_v1','dependent':'transaction_fence_normal_dependent_v1','fault':'transaction_fence_join_v1'}
 parent=load(ROOT/'hardware/variants'/paths[kind]/'build_tb.py','source_'+kind);s=parent.make();_,_,_,ranges=extract(s)
 # Remove only structural statements actually moved, never clocks, scoreboards or agents.
 for a,b in sorted(ranges,reverse=True):s=s[:a]+s[b:]
 for name in ['rst','lr_start_valid','lr_rsp_ready']:
  s=re.sub(r'\b'+name+r'=([^;,:]+)',name,s,count=1)
 text,interface,meta=make()
 for name in meta['instances']:s=re.sub(r'\b'+name+r'\.', 'system.'+name+'.',s)
 # All internal observations remain read-only hierarchical probes in the TB.
 # Drop wire initializer drivers of moved aliases and supply their observed values.
 aliases=[]
 for n in meta['internal']:
  if n.endswith('_held'):continue
  aliases.append('assign '+n+'=system.'+n+';')
 # Public outputs connect through ports, not hierarchical aliases.
 binds={n:n for n in interface}
 binds.update(recover_cookie="32'hc0010001",recover_checkpoint="32'd17",recover_version="32'd4",recover_design='design_id',recover_query="2'd2",recover_price="4'd4",snapshot_design='design_id',snapshot_checkpoint="32'd17",snapshot_cookie="32'he0010001",snapshot_count="32'd328",snapshot_nodes="32'd9089009",snapshot_probe="32'd150697",lr_s_cookie="32'he0010001",test_route_abort='injected_abort',test_route_version_flip='injected_drift')
 if kind=='fault':
  # After the command handshake the host reuses all snapshot descriptor wires.
  # The target must use its captured descriptor throughout reset/recovery.
  vals={'design':(64,"64'h123456789abcdef0"),'checkpoint':(32,"32'd17"),'cookie':(32,"32'he0010001"),'count':(32,"32'd328"),'nodes':(32,"32'd9089009"),'probe':(32,"32'd150697")}
  extra=''
  for n,(w,v)in vals.items():
   extra+=f'reg [{w-1}:0]snapshot_test_{n}={v};\n';binds['snapshot_'+n]='snapshot_test_'+n
  extra+='initial begin wait(k_rec_valid&&k_rec_ready);@(posedge clk);@(negedge clk);\n'
  for n in vals:extra+=f'snapshot_test_{n}=~snapshot_test_{n};\n'
  extra+='end\nalways @(posedge clk)if(k_labels_valid)begin\n'
  for n,(w,v)in vals.items():extra+=f'if(snapshot_test_{n}==={v}||system.snapshot_{n}_held!=={v})$fatal(1,"snapshot capture {n}");\n'
  extra+='end\n'
  s=s.replace('initial begin\n trace=$fopen',extra+'\ninitial begin\n trace=$fopen',1)
 top='residency_system #(.SLOTS(SLOTS),.FRAMES(FRAMES),.INDEX_BITS(INDEX_BITS),.HASH_BITS(HASH_BITS),.ENABLE_TEST_INJECTION(1))system('+','.join('.'+n+'('+v+')'for n,v in binds.items())+');\n'
 if kind=='normal':top=top.replace('.ENABLE_TEST_INJECTION(1)', '.ENABLE_TEST_INJECTION(0)')
 s=s.replace('initial begin\n trace=$fopen',top+'\n'+'\n'.join(aliases)+'\ninitial begin\n trace=$fopen',1)
 assert s.count('residency_system #')==1
 return s
