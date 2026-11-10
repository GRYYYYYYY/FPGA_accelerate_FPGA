"""Freeze original owner methods, differential tests and full real-event replay."""
from pathlib import Path
import hashlib,json,os,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(8<<20),b''):h.update(b)
 return h.hexdigest()
def extract(s):
 chunks=[]
 for a,b in [('    inline int countUserSlot(', '    static uint8_t packHotFlags('),('    inline void syncHotOcc(', '    inline int countUserHot('),('    inline void incUserSlot(', '    int countConnectionsOfUser(')]:
  begin=s.index(a);end=s.index(b,begin);chunks.append(s[begin:end])
 return '\n'.join(chunks)
def main():
 baseline=ROOT/'results/owner_profile_real_v4_20261024'
 gate=json.loads((baseline/'source_bound_audit.json').read_text())
 assert gate['status']=='passed' and gate['manifest_sha256']==sha(baseline/'manifest.json')
 out=ROOT/'results/owner_store_20261024';out.mkdir();src=out/'sources';src.mkdir()
 original=ROOT/'../_shared/assets/gpu_router_original/rewrite/cpp_router/src/main.cpp'
 for p in (ROOT/'hardware/search/owner_state_v1').iterdir():
  if p.is_file():(src/p.name).write_bytes(p.read_bytes())
 (src/'original_owner.inc').write_text(extract(original.read_text()))
 (out/'runner.py').write_bytes(Path(__file__).read_bytes())
 m={'status':'preparing','pid':os.getpid(),'runner_sha256':sha(Path(__file__)),'original_path':str(original.resolve()),'original_sha256':sha(original),'baseline_gate_sha256':sha(baseline/'source_bound_audit.json'),'events_sha256':sha(baseline/'owner.events'),'sources':{p.name:sha(p)for p in src.iterdir()},'commands':[],'scope':'Executable backing-layout and bounded allocator specification. No AXI RTL or hardware timing; all real mutations compared to original event count/occupancy.'}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  commands=[('build',['g++','-std=c++17','-O2','-fsanitize=undefined','-fno-sanitize-recover=all','-I'+str(src),str(src/'test_owner.cpp'),'-o',str(out/'verify')]),('unit',[str(out/'verify')]),('real',[str(out/'verify'),str(baseline/'owner.events'),str(out/'final'), '65536'])]
  for stage,cmd in commands:
   m['status']=stage;m['commands'].append({'stage':stage,'argv':cmd});save()
   with (out/(stage+'.log')).open('w')as f:r=subprocess.run(cmd,stdout=f,stderr=subprocess.STDOUT,timeout=300)
   m['commands'][-1]['exit_code']=r.returncode;save();assert r.returncode==0,stage
  assert 'OWNER_UNIT_PASS random_mutations=200000 ' in (out/'unit.log').read_text()
  assert 'OWNER_REPLAY_PASS events=18515060 capacity=65536 peak_live=53734 ' in (out/'real.log').read_text()
  m['status']='passed'
 except Exception as e:m.update(status='failed',error=repr(e));raise
 finally:
  m['artifacts']={str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='manifest.json'};save()
 print((out/'unit.log').read_text()+(out/'real.log').read_text())
if __name__=='__main__':main()
