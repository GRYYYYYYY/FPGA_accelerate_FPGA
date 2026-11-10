from pathlib import Path
import json,hashlib,shutil,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();base=Path(sys.argv[2]).resolve();bm=json.loads((base/'manifest.json').read_text());sources={}
 for n,v in bm['sources'].items():
  if n.startswith('tb_')or n=='runner.py':continue
  q=src/n;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(base/'sources'/n,q);assert sha(q)==v['sha256'];sources[n]=sha(q)
 rtl=[n for n in bm['rtl'] if not n.startswith('tb_')]
 for f in src.rglob('*.dat'):shutil.copyfile(f,p/f.name)
 tcl='set_param general.maxThreads 2\n'
 for n in rtl:tcl+='read_verilog -sv {'+str(src/n)+'}\n'
 tcl+='synth_design -mode out_of_context -top search_residency_system -part xcu280-fsvh2892-2L-e\nreport_utilization -file {'+str(p/'utilization.rpt')+'}\nwrite_checkpoint -force {'+str(p/'synth.dcp')+'}\nwrite_verilog -force {'+str(p/'synth.v')+'}\nputs SEARCH_SYSTEM_SYNTH_DONE\n'
 (p/'synth.tcl').write_text(tcl)
 (p/'manifest.json').write_text(json.dumps(dict(status='prepared',sources=sources,rtl=rtl,part='xcu280-fsvh2892-2L-e',tcl_sha256=sha(p/'synth.tcl'),scope='Full autonomous prepared-query search system OOC, default32 slots/16384 frames, test injection disabled. All runtime input data unconstrained; no clock/place/route or board claim.'),indent=2)+'\n')
if __name__=='__main__':main()
