from pathlib import Path
import hashlib,json,re,sys,struct,xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
 out=Path(sys.argv[1]).resolve();m=read(out/'manifest.json');assert m['status']=='completed'
 unit=ROOT/'results/cost_center_cpu_20261025';ug=read(unit/'source_bound_audit.json');um=read(unit/'manifest.json');assert ug['status']=='passed'and ug['manifest_sha256']==sha(unit/'manifest.json')==m['unit_manifest_sha256']and sha(unit/'source_bound_audit.json')==m['unit_audit_sha256']
 for name,h in m['sources'].items():assert sha(out/'sources'/name)==h
 for n in ['cost_center.hpp','kernel.cpp']:assert m['sources']['hls/cost_center/v1/'+n]==um['sources']['hls/cost_center/v1/'+n]['sha256']
 assert sha(ROOT/'hardware/hls/cost_center/v1/rtl_testbench.cpp')==m['sources']['hls/cost_center/v1/rtl_testbench.cpp']
 assert sha(out/'runner.py')==sha(ROOT/'scripts/run_cost_center_hls.py')and sha(out/'run_hls.tcl')==m['tcl_sha256']and sha(out/'hls_config.cfg')==m['config_sha256']
 assert m['cosim_argv_preflight']=={'csim_argv':'','cosim_argv':'','both_empty_allowed':True}
 for n,h in m['generated_rtl_artifacts'].items():assert sha(out/n)==h
 for n,h in m['observations'].items():assert sha(out/n)==h
 assert all(c['exit_code']==0 for c in m['commands'])
 log=(out/'hls.log').read_text();assert sha(out/'hls.log')==m['flow_log_sha256']and 'COST_CENTER_HLS_DONE'in log and not re.search(r'^ERROR:',log,re.M)
 rpt=out/'cost_center_step/solution1/sim/report/cost_center_step_cosim.rpt';assert sha(rpt)==m['cosim_report_sha256']and re.search(r'Verilog\s*\|\s*Pass',rpt.read_text())
 assert sha(out/'vectors.txt')==sha(unit/'vectors.txt')==m['vectors_sha256']==um['vectors_sha256']
 vec=[tuple(int(x,16)for x in line.split())for line in(out/'vectors.txt').read_text().splitlines()];assert len(vec)==110397 and all(len(r)==6 for r in vec)
 expected=[r[4:]for r in vec]
 observations={}
 for name in ['csim_observed.txt','cost_center_step/solution1/sim/wrapc/observed.txt','cost_center_step/solution1/sim/wrapc_pc/observed.txt']:
  rows=[tuple(int(x,16)for x in line.split())for line in(out/name).read_text().splitlines()];assert rows==expected;observations[name]=len(rows)
 # HLS2022.2 binary TV format: each transaction has big-endian u64 element
 # count then that many u32 values; an eight-byte runtime-end marker follows.
 marker=bytes.fromhex('5a5aa5a50f0ff0f0')
 def transactions(path,width):
  data=path.read_bytes();size=8+width*4;assert data[-8:]==marker and len(data)==len(vec)*size+8
  rows=[]
  for i in range(len(vec)):
   start=i*size;assert struct.unpack_from('>Q',data,start)[0]==width;rows.append(struct.unpack_from('>'+str(width)+'I',data,start+8))
  return rows
 tv=out/'cost_center_step/solution1/sim/tv'
 c_in=tv/'cdatafile/c.cost_center_step.autotvin_input_r.dat';c_out=tv/'cdatafile/c.cost_center_step.autotvout_output_r.dat';rtl_out=tv/'rtldatafile/rtl.cost_center_step.autotvout_output_r.dat'
 assert transactions(c_in,4)==[r[:4]for r in vec]
 assert transactions(c_out,2)==expected and transactions(rtl_out,2)==expected
 root=ET.parse(out/'cost_center_step/solution1/syn/report/cost_center_step_csynth.xml').getroot();estimates={p:{e.tag:e.text for e in root.find(p)}for p in ['AreaEstimates/Resources','PerformanceEstimates/SummaryOfOverallLatency','PerformanceEstimates/SummaryOfTimingAnalysis']}
 rtl=(out/'cost_center_step/solution1/syn/verilog/cost_center_step.v').read_text();assert 'Version: 2022.2'in rtl and 'input_r_address1'not in rtl and 'output_r_address1'in rtl
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes())
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':len(vec),'rtl_output_words':len(vec)*2,'observations':observations,'raw_TV_transactions_checked':len(vec),'raw_TV_sha256':{str(p.relative_to(out)):sha(p)for p in[c_in,c_out,rtl_out]},'synthesis_estimates':estimates,'elapsed_s':m['commands'][-1]['elapsed_s'],'scope':'Actual cost-center scalar HLS2022.2 Csim/synthesis/Verilog cosim; all frozen cases and raw RTL words checked. Finite center input contract; no service/reset/query ownership, actual lookup/post-prev ordering, mapped implementation or joined cost/search proof.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
