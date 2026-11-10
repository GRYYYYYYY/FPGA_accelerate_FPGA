from pathlib import Path
import hashlib,json,re,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=ROOT/'results/search_access_hls_20261024';m=read(out/'manifest.json');assert m['status']=='completed'
 unit=ROOT/'results/search_access_unit_v3_20261024';gate=read(unit/'source_bound_audit.json')
 assert gate['status']=='passed' and sha(unit/'source_bound_audit.json')==m['unit_gate_sha256'] and gate['manifest_sha256']==sha(unit/'manifest.json')
 assert sha(ROOT/'scripts/run_search_access_hls.py')==m['runner_sha256']==sha(out/'runner.py')
 for name,digest in m['sources'].items():
  assert sha(out/'sources'/name)==digest
  source=ROOT/'hardware/hls/search_access/v2'/name if name in ['testbench.cpp','hls_config.cfg'] else unit/'sources'/name
  assert sha(source)==digest
 for name,digest in m['generated_rtl_artifacts'].items():assert sha(out/name)==digest
 for name,digest in m['observations'].items():assert sha(out/name)==digest
 assert all(c['exit_code']==0 for c in m['commands']) and sha(out/'vectors.txt')==m['vectors_sha256'] and sha(out/'run_hls.tcl')==m['tcl_sha256']
 log=(out/'hls.log').read_text();assert sha(out/'hls.log')==m['flow_log_sha256'] and 'ACCESS_HLS_DONE' in log and not re.search(r'^ERROR:',log,re.M)
 rpt=out/'access_step/solution1/sim/report/access_step_cosim.rpt';assert sha(rpt)==m['cosim_report_sha256'] and re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
 with (unit/'vectors.txt').open()as f,(out/'vectors.txt').open()as h:
  for line in f:assert line==next(h)
  extra=[s.split()for s in h];assert len(extra)==9
 fields=[(0,2),(1,0),(1,19),(2,16),(4,3),(7,512),(8,256),(9,256),(10,256)]
 for i,(v,(field,value))in enumerate(zip(extra,fields)):
  x=[1,1,0,0,0,0,17,0,12,12,1,0,0,0,0,0,-1,1,-1,1];x[field]=value
  assert list(map(int,v[:2]))==[195175+i,46656+i]
  assert [int(a,16)for a in v[2:]]==[a&0xffffffff for a in x]+[1,0,0,0,0,0]
 paths=['csim_observed.txt','access_step/solution1/sim/wrapc/observed.txt','access_step/solution1/sim/wrapc_pc/observed.txt']
 for path in paths:
  with (out/'vectors.txt').open()as vf,(out/path).open()as of:
   count=0
   for line in vf:
    v=line.split();o=next(of).split();assert len(v)==28 and len(o)==8 and v[:2]==o[:2]
    assert [int(x,16)for x in o[2:]]==[int(x,16)for x in v[22:]],(path,count);count+=1
   assert count==195184 and next(of,None)is None
 root=ET.parse(out/'access_step/solution1/syn/report/access_step_csynth.xml').getroot()
 estimates={p:{e.tag:e.text for e in root.find(p)}for p in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfOverallLatency','PerformanceEstimates/SummaryOfTimingAnalysis']}
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'rtl_exact':True,'decisions':46656,'steps':195184,'invalid_packets':9,'output_words':195184*6,'synthesis_estimates':estimates,'scope':'Actual stateless access_step RTL replays source-bound original-equivalent decision traces plus malformed packets; no dynamic service backend, owner/epoch wrapper, recursive executor or board.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
