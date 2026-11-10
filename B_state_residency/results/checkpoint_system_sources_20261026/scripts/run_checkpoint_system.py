"""Ordinary start regression: new production root with boot_required=0."""
from pathlib import Path
import sys,json,shutil,subprocess,time
from run_checkpoint_authority import ROOT,BIN,sha

def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();base=Path('/tmp/B_state_residency_offer_20261025/bundle_capture_v3');fixed=Path('/tmp/B_state_residency_offer_20261025/cold_axi_fixed_v1');bm=json.loads((base/'manifest.json').read_text());fm=json.loads((fixed/'manifest.json').read_text());inp=Path(bm['input'])
 assert json.loads((base/'source_bound_audit.json').read_text())['status']==json.loads((fixed/'source_bound_audit.json').read_text())['status']=='passed'
 m={'status':'running','base':str(base),'production':str(fixed),'input':str(inp),'sources':{},'rtl':[],'cases':{},'scope':'Normal boot_required=0 full fault/recovery/retry and capture regression, both cache capacities. Integrated staged metadata cancellation under native full-system lease; stream offers blocked; prior recovery/capture retained.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def copy(p,n):
  q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][n]={'path':str(p),'sha256':sha(q)}
 for n,h in bm['sources'].items():
  if n not in bm['rtl']and not n.endswith('.dat'):continue
  assert sha(base/'sources'/n)==h['sha256'];copy((ROOT/'hardware/variants/checkpoint_system_v1'/n) if n in ['query_residency_system.sv','search_residency_system.sv','residency_system.sv'] else (ROOT/'hardware/variants/checkpoint_stage_v1'/n) if n in ['recovery_coordinator.sv','config_restore_controller.sv'] else base/'sources'/n,n)
 copy(fixed/'sources/boot_restore_gate.sv','boot_restore_gate.sv');copy(Path(__file__),'runner.py')
 for n in ['build.py','build_tb.py']:copy(ROOT/'hardware/variants/checkpoint_system_v1'/n,n)
 for p in [ROOT/'hardware/variants/authority_rotate_v1/checkpoint_authority_rotator.sv', ROOT/'hardware/variants/checkpoint_stage_v1/checkpoint_publish_barrier.sv']:copy(p,p.name)
 sys.path.insert(0,str(ROOT/'hardware/variants/checkpoint_system_v1'))
 from build_tb import make
 tb=make((src/'tb_query_fault.sv').read_text());needle=')system(.jp_start';assert tb.count(needle)==1
 ties=""".boot_required(1'b0),.boot_cfg_valid(1'b0),.boot_verify_valid(1'b0),.boot_rsp_ready(1'b0),.boot_design(64'd0),.boot_generation(64'd0),.boot_checkpoint(32'd0),.boot_version(32'd0),.boot_nodes(32'd0),.boot_label_count(32'd0),.boot_label_crc(32'd0),.boot_path_crc(32'd0),.boot_query_crc(32'd0),.boot_query(2'd0),.boot_slots(2'd0),.boot_price(4'd0),.boot_payload(2304'd0),"""
 tb=tb.replace(needle,')system('+ties+'.jp_start');tb=tb.replace('endmodule','always @(posedge clk)if(!k_cold_rst&&!rst)begin if(system.boot_pending||system.boot_rsp_valid)$fatal(1,"normal start entered bootstrap");end\nendmodule');(src/'tb_query_fault.sv').write_text(tb);m['sources']['tb_query_fault.sv']['sha256']=sha(src/'tb_query_fault.sv')
 m['rtl']=bm['rtl']+['boot_restore_gate.sv','checkpoint_authority_rotator.sv','checkpoint_publish_barrier.sv'];save()
 def run(d,stage,args,c):
  t=time.monotonic()
  with(d/(stage+'.stdout.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=d,stdout=f,stderr=subprocess.STDOUT,timeout=600)
  c['commands'].append({'stage':stage,'argv':list(map(str,args)),'exit_code':r.returncode,'elapsed_s':time.monotonic()-t});save();assert r.returncode==0
 try:
  for mode,define in [('full',None),('pressure','PRESSURE')]:
   name=mode+'_5';d=out/name;d.mkdir();c=m['cases'][name]={'status':'running','commands':[]};save()
   run(d,'compile',[BIN/'xvlog','--sv','--define','BUNDLE_TRACE','--define','QC_NO_LOSS']+(['--define',define]if define else[])+[src/n for n in m['rtl']],c)
   run(d,'elaborate',[BIN/'xelab','tb_candidate_offer','-s','normal','--debug','typical','--mt','2'],c)
   for n in ['design.bin','owners.bin','cost.bin']:shutil.copyfile(inp/n,d/n)
   with(d/'owners.bin').open('ab')as f:f.write((inp/'owner_allocator.bin').read_bytes())
   shutil.copyfile(inp/'owners.bin',d/'primary.bin');shutil.copyfile(inp/'owner_allocator.bin',d/'allocator.bin');(d/'pool.bin').write_bytes(b'')
   with(d/'labels.bin').open('wb')as f:f.truncate(3145728)
   for p in src.rglob('*.dat'):shutil.copyfile(p,d/p.name)
   (d/'run.tcl').write_text('run 30ms\nquit\n');args=[BIN/'xsim','normal','--tclbatch','run.tcl','--log','simulate.log'];old=bm['cases'][name]['commands'][-1]['argv']
   for i,x in enumerate(old):
    if x!='--testplusarg':continue
    k,v=old[i+1].split('=',1)
    if k in ['design0','owners0','cost0','labels0','snapshot0','snapshot1','snapshot2']or k.endswith('log'):v=str(d/Path(v).name)
    args+=['--testplusarg',k+'='+v]
   run(d,'simulate',args,c);log=(d/'simulate.log').read_text();assert 'QUERY_FAULT_OBSERVED case=5 outcome=recovered_retry'in log and 'Fatal:'not in log and 'JOINT_SYSTEM_CANCEL_PASS'in log,log[-2000:]
   c['status']='observed';save();print(name,'normal regression observed',flush=True)
  m['status']='observed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:save()
if __name__=='__main__':main()
