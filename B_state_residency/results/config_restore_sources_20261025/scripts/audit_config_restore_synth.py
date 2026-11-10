from pathlib import Path
from collections import Counter
import json,hashlib,re,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 syn=Path(sys.argv[1]).resolve();unit=Path(sys.argv[2]).resolve();m=json.loads((syn/'manifest.json').read_text());assert m['status']=='passed' and json.loads((unit/'source_bound_audit.json').read_text())['status']=='passed'
 rtl=syn/'sources/config_restore_controller.sv';assert sha(rtl)==m['rtl_sha256']==sha(unit/'sources/config_restore_controller.sv')==sha(ROOT/'hardware/variants/config_restore_v1/config_restore_controller.sv')
 assert sha(syn/'synth.tcl')==m['tcl_sha256'];log=(syn/'vivado.log').read_text();assert 'CONFIG_RESTORE_SYNTH_DONE'in log and 'synth_design completed successfully'in log and not re.search(r'^ERROR:',log,re.M)
 r=(syn/'utilization.rpt').read_text();assert 'Vivado v.2022.2'in r and 'Synthesized'in r and 'xcu280-fsvh2892-2L-e'in r
 def num(label):return float(re.search(r'^\|\s*'+re.escape(label)+r'\s*\|\s*([\d.]+)',r,re.M)[1])
 util={k:num(v)for k,v in [('LUT','CLB LUTs*'),('FF','CLB Registers'),('latches','Register as Latch'),('BRAM','Block RAM Tile'),('DSP','DSPs')]};assert util['latches']==util['DSP']==0
 warnings=Counter(re.findall(r'^WARNING: \[([^]]+)\]',log,re.M))
 for n in ['synth.dcp','synth.v']:assert (syn/n).stat().st_size>1000
 a=dict(status='passed',manifest_sha256=sha(syn/'manifest.json'),auditor_sha256=sha(Path(__file__)),unit_audit_sha256=sha(unit/'source_bound_audit.json'),utilization=util,warnings=dict(warnings),files={str(p.relative_to(syn)):sha(p)for p in sorted(syn.rglob('*'))if p.is_file()and p.name!='source_bound_audit.json'},scope='Resident descriptor/controller only OOC, no place/route/Fmax or whole recovery-system resource claim.')
 (syn/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a))
if __name__=='__main__':main()
