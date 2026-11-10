from pathlib import Path
import json,struct,random,shutil,subprocess,sys
from run_checkpoint_authority import ROOT,BIN,sha
out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
image=out.parent/'label_baseline_image_v1';im=json.loads((image/'manifest.json').read_text());assert im['status']=='prepared'
assert sha(image/'baseline.bin')==im['baseline_sha256']
cpu=Path(im['source']);assert sha(cpu)==im['source_sha256']
closure={int(x.split()[0])for x in(out.parent/'label_source_crc_full_v2/imports.txt').read_text().splitlines()}
rng=random.Random(27419);nodes=sorted(closure|{0,1,2,3,7,8,im['node_count']-1,im['node_count']-2}|set(rng.sample(range(im['node_count']),64)))
with cpu.open('rb')as f,(out/'vectors.txt').open('w')as g:
 for n in nodes:
  f.seek(n*44);u=struct.unpack('<11I',f.read(44));v=struct.pack('<5I',u[0],u[1],u[3],u[4],u[5]);g.write(f'{n} {int.from_bytes(v,"little"):040x}\n')
 f.seek(0);u=struct.unpack('<11I',f.read(44));node0=int.from_bytes(struct.pack('<5I',u[0],u[1],u[3],u[4],u[5]),'little')
for p in [ROOT/'hardware/variants/label_baseline_v1/label_baseline_reader.sv',ROOT/'hardware/variants/label_baseline_v1/tb_baseline.sv',ROOT/'hardware/variants/iter2_runtime_owner_v1/axi_file_memory.sv',Path(__file__)]:shutil.copyfile(p,src/p.name)
f=src/'tb_baseline.sv';f.write_text(f.read_text().replace("160'h000000007f800000ffffffff000000007f800000",f"160'h{node0:040x}"))
(out/'run.tcl').write_text('run all\nquit\n')
m=dict(status='running',image=str(image),image_manifest_sha256=sha(image/'manifest.json'),vectors_sha256=sha(out/'vectors.txt'),future_closure_nodes=len(closure),tested_nodes=len(nodes),tested_outside_closure=len(set(nodes)-closure),sources={p.name:sha(p)for p in src.iterdir()},commands=[],scope='Read-only real all-node baseline reader component; not integrated resident miss handling yet.')
try:
 for stage,args in [('compile',[BIN/'xvlog','--sv',src/'label_baseline_reader.sv',src/'axi_file_memory.sv',src/'tb_baseline.sv']),('elaborate',[BIN/'xelab','tb_baseline','-s','baseline','--debug','typical']),('simulate',[BIN/'xsim','baseline','--tclbatch','run.tcl','--testplusarg','baseline0='+str(image/'baseline.bin'),'--testplusarg','baselinelog='+str(out/'baseline_axi.txt'),'--testplusarg','vectors='+str(out/'vectors.txt'),'--testplusarg','trace='+str(out/'trace.txt')])]:
  with(out/(stage+'.log')).open('w')as f:r=subprocess.run(list(map(str,args)),cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
  m['commands'].append(dict(stage=stage,exit_code=r.returncode));assert r.returncode==0,stage
 log=(out/'simulate.log').read_text();assert 'LABEL_BASELINE_PASS'in log and 'Fatal:'not in log;m['status']='observed'
finally:(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
print('LABEL_BASELINE_OBSERVED')
