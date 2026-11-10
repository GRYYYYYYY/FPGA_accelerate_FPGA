from pathlib import Path
import json,struct,shutil,subprocess,sys
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir();single='--single'in sys.argv;drain='--drain'in sys.argv
base=out.parent/'label_source_crc_full_v2';bm=json.loads((base/'manifest.json').read_text());image=out.parent/'label_baseline_image_v1'
im=json.loads((image/'manifest.json').read_text());assert json.loads((image/'source_bound_audit.json').read_text())['status']=='passed'
assert sha(image/'baseline.bin')==im['baseline_sha256']
rtl=[]
# Exact actual native endpoint dependency closure from audited full query source list.
for name,spec in bm['sources'].items():
 if name.startswith('expansion_20261024/pager/backend/')or name.startswith('expansion_20261024/pager/adapter/'):
  p=base/'sources'/name;assert sha(p)==spec['sha256'];q=src/name;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
  if q.suffix in ['.sv','.v']:rtl.append(q)
for p in [ROOT/'hardware/variants/label_baseline_probe_v1/resident_page_manager.sv',ROOT/'hardware/variants/label_baseline_probe_v1/tb_probe.sv',ROOT/'hardware/variants/label_baseline_v1/label_baseline_reader.sv',ROOT/'hardware/variants/iter2_runtime_owner_v1/axi_file_memory.sv',Path(__file__),ROOT/'hardware/variants/label_baseline_probe_v1/build.py',ROOT/'hardware/variants/label_baseline_probe_v1/build_tb.py']:
 q=src/p.name;shutil.copyfile(p,q)
 if q.suffix=='.sv':rtl.append(q)
with Path(im['source']).open('rb')as f:
 v=[]
 for n in [0,1,8]:
  f.seek(n*44);u=struct.unpack('<11I',f.read(44));v.append(f'{int.from_bytes(struct.pack("<5I",u[0],u[1],u[3],u[4],u[5]),"little"):040x}')
(out/'vectors.txt').write_text(' '.join(v)+'\n');(out/'pages.bin').write_bytes(bytes(3072));(out/'run.tcl').write_text('run all\nquit\n')
m=dict(status='running',single=single,drain_fault=drain,image=str(image),image_manifest_sha256=sha(image/'manifest.json'),sources={str(p.relative_to(src)):sha(p)for p in src.rglob('*')if p.is_file()},vectors_sha256=sha(out/'vectors.txt'),commands=[],scope='Native resident-manager miss integration with real endpoint, baseline AXI and page writeback/refill. No full query oracle yet.')
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv']+(['--define','SINGLE']if single else[])+(['--define','FAULT_DRAIN']if drain else[])+rtl),('elaborate',[BIN/'xelab','tb_baseline_miss','-s','miss','--debug','typical']),('simulate',[BIN/'xsim','miss','--tclbatch','run.tcl','--testplusarg','baseline0='+str(image/'baseline.bin'),'--testplusarg','baselinelog='+str(out/'baseline_axi.txt'),'--testplusarg','pages0='+str(out/'pages.bin'),'--testplusarg','pageslog='+str(out/'pages_axi.txt'),'--testplusarg','vectors='+str(out/'vectors.txt'),'--testplusarg','trace='+str(out/'trace.txt')])]:
  with(out/(stage+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append(dict(stage=stage,exit_code=r.returncode));assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert 'BASELINE_MISS_PASS'in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('BASELINE_MISS_OBSERVED',single)
