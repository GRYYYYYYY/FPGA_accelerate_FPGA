"""Audit OOC synthesis completion and retain resource/model limitations."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def resources(path):
 text=path.read_text();result={}
 for label,key in [('CLB LUTs*','LUT'),('CLB Registers','FF'),('Register as Latch','latches'),('Block RAM Tile','BRAM'),('DSPs','DSP')]:
  match=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',text,re.M);assert match,label;result[key]=float(match[1])
 assert result['latches']==0
 return result

def main():
 out=ROOT/'results/rtl_static_endpoint_synthesis_20261023';m=json.loads((out/'manifest.json').read_text());receipt=json.loads((out/'completion_receipt.json').read_text())
 assert receipt['is_command_running'] is False and receipt['last_completed_code']==0 and 'rtl_static_endpoint_synthesis_20261023' in receipt['last_completed_output']
 assert 'STATIC_ENDPOINT_SYNTH_DONE version=2022.2' in (out/'completed.txt').read_text()
 for n,h in m['sources'].items():
  p=Path(n);assert sha(p)==h
  if '/rtl/' in n:assert sha(out/'sources'/p.name)==h
 assert (out/'research_clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
 new=resources(out/'utilization.rpt');oldpath=ROOT/'results/rtl_small_endpoint_synthesis_20261023/utilization.rpt';old=resources(oldpath)
 dcp=out/'memory_scratch_endpoint_small_staticcodec.dcp';assert dcp.stat().st_size>10000
 report=(out/'utilization.rpt').read_text();assert 'memory_scratch_endpoint_small_staticcodec' in report and 'xcu280-fsvh2892-2L-e' in report and 'Synthesized' in report
 ram=(out/'ram_cells.txt').read_text().splitlines();assert sum(1 if 'RAMB36' in line else .5 for line in ram)==new['BRAM']
 result={'status':'synthesis_evidence_verified','launch_manifest_sha256':sha(out/'manifest.json'),'resources':new,'baseline_resources':old,'delta':{k:new[k]-old[k] for k in new},'baseline_report_sha256':sha(oldpath),'artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file()},'source_sha256':sha(Path(__file__)),'platform_closed':False,'physical_timing_complete':False,'board_performance':None}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(new));print(json.dumps(result['delta']))
if __name__=='__main__':main()
