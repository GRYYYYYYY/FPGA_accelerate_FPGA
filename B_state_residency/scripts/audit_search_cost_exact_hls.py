"""Exact returned-word gate for integer binary32 cost RTL; not just cosim PASS."""
from pathlib import Path
import hashlib,json,re,runpy,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_cost_exact_hls_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='characterized'
 assert sha(ROOT/'scripts/run_search_cost_exact_hls.py')==m['runner_sha256']==sha(out/'runner.py')
 for n,d in m['sources'].items():
  assert sha(out/'sources'/n)==d
  if n!='vector_count.hpp':assert sha(ROOT/'hardware/hls/search_cost/exact_v2'/n)==d
 for n,d in m['gates'].items():
  p=ROOT/'results'/n/'source_bound_audit.json';assert sha(p)==d and json.loads(p.read_text())['status']=='passed'
 cpp=ROOT/'results/search_cost_exact_cpp_v2_20261024'
 for name in ['kernel.cpp','softfloat32.hpp']:assert sha(out/'sources'/name)==sha(cpp/'sources'/name)
 for n,d in m['generated_rtl_artifacts'].items():assert sha(out/n)==d
 for n,d in m['observations'].items():assert sha(out/n)==d
 assert sha(out/'vectors.txt')==m['vectors_sha256'] and sha(out/'run_hls.tcl')==m['tcl_sha256']
 assert all(c['exit_code']==0 for c in m['commands']) and sha(out/'hls.log')==m['flow_log_sha256']
 log=(out/'hls.log').read_text();assert 'COST_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
 rpt=out/'cost_step/solution1/sim/report/cost_step_cosim.rpt';assert sha(rpt)==m['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
 native=ROOT/'results/search_cost_native_hls_20261024';v=(out/'vectors.txt').read_text().splitlines();synthetic=(out/'synthetic_vectors.txt').read_text().splitlines()
 assert len(v)==21576 and len(synthetic)==5352 and synthetic[:4776]==(native/'vectors.txt').read_text().splitlines() and v[:5352]==synthetic
 real=ROOT/'results/cost_capture_real_20261024';packets=['4 '+' '.join(line.split()[6:])for line in (real/'cost_packets.txt').read_text().splitlines()if line.startswith('V ')];assert v[5352:]==packets
 compare=runpy.run_path(str(ROOT/'scripts/audit_search_cost_native.py'))['compare'];results={}
 for label,path in [('host','observed.txt'),('csim','csim_observed.txt'),('rtl','cost_step/solution1/sim/wrapc_pc/observed.txt')]:
  groups,words,_=compare(out/'vectors.txt',out/path);assert words==0,(label,groups)
  assert {k:g['cases']for k,g in groups.items()}=={0:4096,1:144,2:512,3:24,4:16224,5:576};results[label]=groups
 root=ET.parse(out/'cost_step/solution1/syn/report/cost_step_csynth.xml').getroot()
 estimates={path:{e.tag:e.text for e in root.find(path)}for path in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfOverallLatency','PerformanceEstimates/SummaryOfTimingAnalysis']}
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'rtl_bit_exact_on_all_vectors':True,'cases':21576,'output_words':107880,'groups':results['rtl'],'synthesis_estimates':estimates,'cosim_report_sha256':sha(rpt),'scope':'Actual integer binary32 HLS cost RTL matches every observed word on synthetic/NaN-pair and sampled real vectors. No exhaustive IEEE proof, arbitrary-compiler NaN payload portability, full-query integration, actual mapped area or board claim.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
