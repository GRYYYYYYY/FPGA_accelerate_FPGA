from pathlib import Path
import importlib.util,sys,shutil,json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
def bound():
 path=ROOT/'hardware/variants/transaction_fence_join_v1/build_tb.py';sp=importlib.util.spec_from_file_location('layout_builder',path);mod=importlib.util.module_from_spec(sp);sp.loader.exec_module(mod);layout=mod.layout()
 q=[sum(w for n,w in x['q'])for x in layout];a=[sum(w for n,w in x['a'])for x in layout];allowed=[i for i in range(16)if (0x037f>>i)&1]
 text=(ROOT/'hardware/variants/transaction_fence_static_v2/transaction_fence.sv').read_text();header=text.split(')(\n',1)[1].split('\n);',1)[0]
 for symbol,value in [('LANES',16),('REQ_BITS',2432),('RSP_BITS',256)]:header=header.replace(symbol,str(value))
 sizes={'s_payload':sum(q),'cb_payload':sum(q[i]for i in allowed),'d_payload':sum(q),'s_rsp_payload':sum(a),'cb_rsp_payload':sum(a[i]for i in allowed),'d_rsp_payload':sum(a)}
 for name,width in sizes.items():header=re.sub(r'\[[^]]+\]'+name+r'\b','['+str(width-1)+':0]'+name,header)
 s='`timescale 1ns/1ps\n// Actual request/reply field widths, zero padding only; no fixed runtime data.\nmodule transaction_fence_bound(\n'+header.replace('output reg','output wire')+'\n);\n'
 for name in sizes:
  width=38912 if name in ['s_payload','cb_payload','d_payload']else 4096
  s+='wire['+str(width-1)+':0]full_'+name+';\n'
 for name in sizes:
  widths=q if name in ['s_payload','cb_payload','d_payload']else a;stride=2432 if widths is q else 256;offset=0
  for i,width in enumerate(widths):
   active=not name.startswith('cb_')or i in allowed
   if name in ['s_payload','cb_payload','d_rsp_payload']:
    if active:s+=f'assign full_{name}[{i*stride}+:{width}]={name}[{offset}+:{width}];\n'
    else:s+=f'assign full_{name}[{i*stride}+:{width}]=0;\n'
    if stride>width:s+=f'assign full_{name}[{i*stride+width}+:{stride-width}]=0;\n'
   elif active:s+=f'assign {name}[{offset}+:{width}]=full_{name}[{i*stride}+:{width}];\n'
   if active:offset+=width
 pins=','.join('.'+n+'(full_'+n+')'for n in sizes)
 s+="transaction_fence #(.LANES(16),.REQ_BITS(2432),.RSP_BITS(256),.ADMIN_FIRST(14),.CALLBACK_MASK(16'h037f))dut("+pins+',.*);\nendmodule\n'
 return s,q,a,sizes

def main():
 p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();shutil.copyfile(ROOT/'hardware/variants/transaction_fence_static_v2/transaction_fence.sv',src/'transaction_fence.sv');shutil.copyfile(__file__,src/Path(__file__).name)
 text,q,a,sizes=bound();(src/'transaction_fence_bound.sv').write_text(text)
 (p/'synth.tcl').write_text('set_param general.maxThreads 2\nread_verilog -sv {'+str(src/'transaction_fence.sv')+'}\nread_verilog -sv {'+str(src/'transaction_fence_bound.sv')+'}\nsynth_design -mode out_of_context -top transaction_fence_bound -part xcu280-fsvh2892-2L-e\nreport_utilization -file {'+str(p/'utilization.rpt')+'}\nwrite_checkpoint -force {'+str(p/'synth.dcp')+'}\nwrite_verilog -force {'+str(p/'synth.v')+'}\nputs TRANSACTION_FENCE_SYNTH_DONE\n')
 sha=lambda f:hashlib.sha256(f.read_bytes()).hexdigest()
 (p/'manifest.json').write_text(json.dumps(dict(status='prepared',rtl_sha256=sha(src/'transaction_fence.sv'),bound_sha256=sha(src/'transaction_fence_bound.sv'),tcl_sha256=sha(p/'synth.tcl'),request_widths=q,response_widths=a,interface_bits=sizes,part='xcu280-fsvh2892-2L-e',scope='Actual16 service widths, only interface padding bound to zero. Runtime data not fixed. Fence alone OOC, not native engine/recovery controllers or whole-system resources/timing.'),indent=2)+'\n')
if __name__=='__main__':main()
