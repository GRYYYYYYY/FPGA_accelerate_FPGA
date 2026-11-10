"""Freeze integer IEEE core, primitive differential and all synthetic/real cost packets."""
from pathlib import Path
import hashlib,json,shutil,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_cost_exact_cpp_20261024';out.mkdir();src=out/'sources';shutil.copytree(ROOT/'hardware/hls/search_cost/exact_v1',src)
 native=ROOT/'results/search_cost_native_hls_20261024';real=ROOT/'results/cost_capture_real_20261024'
 assert json.loads((native/'manifest.json').read_text())['status']=='characterized'
 assert json.loads((real/'source_bound_audit.json').read_text())['status']=='passed'
 lines=(native/'vectors.txt').read_text().splitlines()
 for line in (real/'cost_packets.txt').read_text().splitlines():
  v=line.split()
  if v[0]=='V':lines.append('4 '+' '.join(v[6:]))
 assert len(lines)==21000
 (out/'vectors.txt').write_text('\n'.join(lines)+'\n');(src/'vector_count.hpp').write_text('#pragma once\n#define COST_CASES 21000\n')
 m={'status':'preparing','sources':{p.name:sha(p)for p in src.iterdir()},'native_manifest_sha256':sha(native/'manifest.json'),'real_gate_sha256':sha(real/'source_bound_audit.json'),'runner_sha256':sha(Path(__file__)),'vectors_sha256':sha(out/'vectors.txt'),'commands':[]}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 (out/'runner.py').write_bytes(Path(__file__).read_bytes());save()
 try:
  flags=['g++','-std=c++14','-O2','-fno-fast-math','-ffp-contract=off','-fsanitize=undefined','-fno-sanitize-recover=all']
  cmds=[('primitive_build',flags+[str(src/'test_primitives.cpp'),'-o',str(out/'primitives')]),('primitives',[str(out/'primitives')]),('cost_build',flags+[str(src/'kernel.cpp'),str(src/'testbench.cpp'),'-o',str(out/'cost')]),('cost',[str(out/'cost')])]
  for stage,argv in cmds:
   with (out/(stage+'.log')).open('w')as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=180)
   m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0
  assert 'SOFTFP_PRIMITIVES_PASS checks=5001280 both_nan_payload_policy_cases=0 inputs=1000256' in (out/'primitives.log').read_text()
  log=(out/'cost.log').read_text();assert 'COST_CHARACTERIZED cases=21000 mismatched_cases=0 mismatched_words=0 normal_mismatches=0' in log,log
  m.update(status='passed',artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file() and p.name!='manifest.json'});save();print(log,end='')
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
