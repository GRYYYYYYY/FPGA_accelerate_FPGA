from pathlib import Path
from collections import Counter
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/search_geometry_hls_20261024';m=read(out/'manifest.json');assert m['status']=='completed'
 unit=ROOT/'results/search_geometry_unit_v3_20261024';gate=read(unit/'source_bound_audit.json')
 assert gate['status']=='passed' and sha(unit/'source_bound_audit.json')==m['unit_gate_sha256'] and gate['manifest_sha256']==sha(unit/'manifest.json')
 assert sha(ROOT/'scripts/run_search_geometry_hls.py')==m['runner_sha256']==sha(out/'runner.py')
 for name,digest in m['sources'].items():assert sha(out/'sources'/name)==digest==sha(unit/'sources'/name)
 for name,digest in m['generated_rtl_artifacts'].items():assert sha(out/name)==digest
 for name,digest in m['observations'].items():assert sha(out/name)==digest
 assert all(c['exit_code']==0 for c in m['commands'])
 assert sha(out/'vectors.txt')==m['vectors_sha256']==sha(unit/'vectors.txt') and sha(out/'run_hls.tcl')==m['tcl_sha256']
 log=(out/'hls.log').read_text();assert sha(out/'hls.log')==m['flow_log_sha256'] and 'GEOMETRY_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
 rpt=out/'geometry_step/solution1/sim/report/geometry_step_cosim.rpt';assert sha(rpt)==m['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
 vec=[s.split()for s in (out/'vectors.txt').read_text().splitlines()];assert len(vec)==9496
 paths=['csim_observed.txt','geometry_step/solution1/sim/wrapc/observed.txt','geometry_step/solution1/sim/wrapc_pc/observed.txt']
 for path in paths:
  lines=(out/path).read_text().splitlines();assert len(lines)==len(vec)
  for i,(v,line)in enumerate(zip(vec,lines)):
   o=line.split();assert len(v)==18 and len(o)==6 and list(map(int,o[:2]))==[i,int(v[0])]
   assert [int(x,16)for x in o[2:]]==[int(x,16)for x in v[14:]],(path,i)
 root=ET.parse(out/'geometry_step/solution1/syn/report/geometry_step_csynth.xml').getroot()
 estimates={path:{e.tag:e.text for e in root.find(path)}for path in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfOverallLatency','PerformanceEstimates/SummaryOfTimingAnalysis']}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'rtl_exact':True,'cases':9496,'output_words':9496*4,'groups':dict(Counter(int(v[0])for v in vec)),'synthesis_estimates':estimates,'scope':'Actual scalar geometry HLS RTL, includes explicit sentinel/range/length status. No input lookup/owner/reset service, full search, mapped area or board proof.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
