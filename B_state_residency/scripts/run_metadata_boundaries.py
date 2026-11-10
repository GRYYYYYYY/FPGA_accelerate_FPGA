from pathlib import Path
import hashlib,json,shutil,struct,subprocess,sys,time
ROOT=Path(__file__).resolve().parents[1];BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();dep=ROOT/'results/metadata_v2_20261024';dm=json.loads((dep/'manifest.json').read_text());g=json.loads((dep/'source_bound_audit.json').read_text());assert g['status']=='passed'and g['manifest_sha256']==sha(dep/'manifest.json')
 m={'status':'running','functional_gate_sha256':sha(dep/'source_bound_audit.json'),'sources':{},'commands':[]};rtl=[]
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 for n in dm['rtl']:
  if Path(n).name.startswith('tb_'):continue
  p=dep/'sources'/n;q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':sha(p)};rtl.append(q)
 for p in list((ROOT/'hardware/variants/metadata_boundaries_v1').iterdir())+[Path(__file__)]:
  if p.is_file():shutil.copyfile(p,src/p.name);m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
 rtl.append(src/'tb_metadata_boundaries.sv');inputs=ROOT/'results/access_fabric_inputs_20261024/synthetic'
 attrs=bytearray((inputs/'nodes.rrt32').read_bytes());attrs[9]&=~1;struct.pack_into('<h',attrs,14,-32768);struct.pack_into('<i',attrs,0,-2147483648);struct.pack_into('<hh',attrs,36*32+10,-32768,32767);struct.pack_into('<i',attrs,36*32,2147483647)
 (out/'attrs.bin').write_bytes(attrs);(out/'design.bin').write_bytes(bytes(1024))
 words=[0xffffffff,0x1ff,0,0,0,0xffff8000,0x80000000,0x7fffffff,0xffff8000,32767,0x80000000,0x7fffffff,0xffffffff,0]
 (out/'numeric_expected.txt').write_text(f'{sum(v<<(32*i)for i,v in enumerate(words)):0112x}\n');(out/'run.tcl').write_text('run 5ms\nquit\n');save()
 args=[BIN/'xsim','test','--tclbatch','run.tcl','--log','simulate.log']
 for k,v in {'graph0':inputs/'offsets.u32le','graph1':inputs/'edges.u32le','graph2':out/'attrs.bin','graphlog':out/'graph_axi.txt','design0':out/'design.bin','designlog':out/'design_axi.txt','expected':out/'numeric_expected.txt'}.items():args+=['--testplusarg',k+'='+str(v)]
 try:
  for stage,argv in [('compile',[BIN/'xvlog','--sv']+rtl),('elaborate',[BIN/'xelab','tb_metadata','-s','test','--debug','typical','--mt','2']),('simulate',args)]:
   c={'stage':stage,'argv':list(map(str,argv))};m['commands'].append(c);save();t=time.monotonic()
   with (out/(stage+'.stdout.log')).open('w')as f:c['exit_code']=subprocess.call(c['argv'],cwd=out,stdout=f,stderr=subprocess.STDOUT)
   c['elapsed_s']=time.monotonic()-t;save();assert c['exit_code']==0,stage
  log=(out/'simulate.log').read_text();hits=[s for s in log.splitlines()if s.startswith('METADATA_BOUNDARIES_PASS ')];assert len(hits)==1 and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log,log[-2000:]
  m.update(status='passed',result=hits[0]);save();print(hits[0])
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
