from pathlib import Path
import sys,shutil,json,hashlib
ROOT=Path(__file__).resolve().parents[1]
p=Path(sys.argv[1]).resolve();p.mkdir();src=p/'sources';src.mkdir();rtl=ROOT/'hardware/variants/label_restore_v1/label_restore_controller.sv';shutil.copyfile(rtl,src/rtl.name);shutil.copyfile(__file__,src/Path(__file__).name)
(p/'synth.tcl').write_text('set_param general.maxThreads 2\nread_verilog -sv {'+str(src/rtl.name)+'}\nsynth_design -mode out_of_context -top label_restore_controller -part xcu280-fsvh2892-2L-e\nreport_utilization -file {'+str(p/'utilization.rpt')+'}\nwrite_checkpoint -force {'+str(p/'synth.dcp')+'}\nwrite_verilog -force {'+str(p/'synth.v')+'}\nputs LABEL_RESTORE_SYNTH_DONE\n')
sha=lambda q:hashlib.sha256(q.read_bytes()).hexdigest()
(p/'manifest.json').write_text(json.dumps(dict(status='prepared',rtl_sha256=sha(src/rtl.name),tcl_sha256=sha(p/'synth.tcl'),part='xcu280-fsvh2892-2L-e',max_records=512,scope='Default512 snapshot record label restore OOC synthesis only, no placement/timing closure or complete system resource claim.'),indent=2)+'\n')
