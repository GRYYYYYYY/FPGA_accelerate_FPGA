"""Bind actual Vivado synthesis resources to audited full-capacity HLS RTL."""
from pathlib import Path
import collections,json,re,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'adapters'))
from prepare_real import sha

def main():
 out=ROOT/'results/frontier_hls_vivado_synthesis_20261024'
 gate=out/'hls_source_bound_audit.json';g=json.loads(gate.read_text());assert g['status']=='passed'
 assert sha(gate)==sha(ROOT/'results/frontier_hls_relative_project_20261024/source_bound_audit.json')
 assert {p.name:sha(p) for p in (out/'sources').iterdir() if p.is_file()}==g['generated_rtl_artifacts']
 assert (out/'completed.txt').read_text()=='FRONTIER_VIVADO_SYNTH_DONE version=2022.2\n'
 assert sha(out/'synthesize_frontier_hls.tcl')==sha(ROOT/'hardware/scripts/synthesize_frontier_hls.tcl')
 assert (out/'research_clock.xdc').read_text()=='create_clock -name research_clock -period 10.000 [get_ports ap_clk]\n'
 text=(out/'utilization.rpt').read_text()
 def used(label):
  match=re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)\s*\|',text,re.M);assert match,label
  return float(match[1])
 resources={name:used(name) for name in ['CLB LUTs*','CLB Registers','Register as Latch','Block RAM Tile','URAM','DSPs']}
 assert resources['Register as Latch']==0
 cells=collections.Counter(line.split()[-1] for line in (out/'ram_cells.txt').read_text().splitlines())
 capacity=sum(n*(36864 if name.startswith('RAMB36') else 18432 if name.startswith('RAMB18') else 294912 if name.startswith('URAM') else 0) for name,n in cells.items())
 # Count is a physical capacity sanity bound; source and full-capacity cosim prove semantics separately.
 assert capacity>=65536*64,(capacity,cells)
 result={'status':'passed','auditor_sha256':sha(Path(__file__)),'resources':resources,'memory_primitives':dict(cells),'physical_memory_capacity_bits':capacity,'artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name not in ('final_audit.json','audit.stdout.log')},'scope':'Standalone frontier Vivado OOC synthesis; no routed timing, integrated router or board performance.'}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
