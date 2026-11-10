"""Freeze and run both native-float and HLS-ready integer-key frontier tests."""
from pathlib import Path
import json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha
from build_frontier_reference import generate
SDK=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vitis_HLS/2022.2/include')
def main():
 design=ROOT/'hardware/hls/frontier';ref=generate((ROOT/'results/frontier_real_20261024/original_trace.cpp').read_text())
 assert (design/'frame_based/frontier_reference.hpp').read_text()==ref
 assert (design/'rearchitect/v1/tb/frontier_reference.hpp').read_text()==ref
 assert (design/'frame_based/testbench.cpp').read_bytes()==(design/'rearchitect/v1/tb/testbench.cpp').read_bytes()
 out=ROOT/'results/frontier_cpp_verified_20261024';out.mkdir()
 for name in ['frame_based','rearchitect']:shutil.copytree(design/name,out/name)
 m={'status':'running','runner_sha256':sha(Path(__file__)),'reference_generator_sha256':sha(ROOT/'adapters/build_frontier_reference.py'),'sources':{str(p.relative_to(out)):sha(p) for folder in [out/'frame_based',out/'rearchitect'] for p in folder.rglob('*') if p.is_file()},'cases':{},'scope':'C++ only; no RTL/clock/resource performance conclusion.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for case,source,tb,includes in [('reference',out/'frame_based/kernel.cpp',out/'frame_based/testbench.cpp',[out/'frame_based']),('candidate',out/'rearchitect/v1/src/kernel_hls.cpp',out/'rearchitect/v1/tb/testbench.cpp',[SDK,out/'rearchitect/v1/src',out/'rearchitect/v1/tb'])]:
   binary=out/(case+'_test');argv=['g++','-std=c++14','-O2','-fno-fast-math','-Wno-unknown-pragmas']
   for p in includes:argv+=['-I',str(p)]
   argv+=[str(source),str(tb),'-o',str(binary)];row={'commands':[{'stage':'build','argv':argv}]};m['cases'][case]=row;save()
   with (out/(case+'.build.log')).open('w') as log:subprocess.run(argv,stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
   row['commands'][0]['exit_code']=0
   with (out/(case+'.log')).open('w') as log:subprocess.run([str(binary)],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=120)
   row['commands'].append({'stage':'verify','argv':[str(binary)],'exit_code':0});text=(out/(case+'.log')).read_text();assert 'FRONTIER_TEST_PASS capacity=65536 checks=135228 comparisons=1000169' in text
   row.update(status='passed',binary_sha256=sha(binary),log_sha256=sha(out/(case+'.log')));save();print(case,'passed',flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
