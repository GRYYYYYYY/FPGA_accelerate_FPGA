"""Verify default-capacity record-response bypass synthesis against frozen baseline."""
from pathlib import Path
import json,hashlib,re
from audit_small_synthesis import resources
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/address64_synthesis_20261024';mp=out/'manifest.json';m=json.loads(mp.read_text())
 receipt=json.loads((out/'completion_receipt.json').read_text())
 assert receipt['is_command_running'] is False and receipt['last_completed_code']==0
 assert 'address64_synthesis_20261024' in receipt['last_completed_output']
 assert (out/'completed.txt').read_text()=='ADDRESS64_SYNTH_DONE version=2022.2\n'
 assert m['generic']=={'EPOCH_BITS':6} and m['frames']==163840 and m['hash_bits']==18
 assert '-generic EPOCH_BITS=6' in (out/'synthesize_address64.tcl').read_text()
 raw=Path(receipt['log_file']).read_text();starts=list(re.finditer(r'^ADDRESS64_SYNTH_BEGIN version=2022\.2',raw,re.M));assert len(starts)==1
 log=raw[starts[0].start():];end=re.search(r'^ADDRESS64_SYNTH_DONE\s*$',log,re.M);assert end;log=log[:end.end()]+'\n';assert not re.search(r'^ERROR:',log,re.M)
 block=re.search(r"synthesizing module 'backing_frame_directory_small'.*?done synthesizing module 'backing_frame_directory_small'",log,re.S);assert block
 for key,value in [('FRAMES',163840),('INDEX_BITS',18),('HASH_BITS',18),('EPOCH_BITS',6)]:assert f'Parameter {key} bound to: {value} - type: integer' in block[0]
 cfg=re.search(r"synthesizing module 'backing_base_config'.*?done synthesizing module 'backing_base_config'",log,re.S);assert cfg
 assert 'Parameter FRAMES bound to: 163840 - type: integer' in cfg[0]
 assert sha(ROOT/'results/address64_endpoint_v3_20261024/source_bound_audit.json')==m['functional_audit_sha256']
 (out/'synthesis_session.log').write_text(log)

 for p,h in m['sources'].items():assert sha(Path(p))==h,p
 assert sha(out/'research_clock.xdc')==m['clock_sha256']
 assert (out/'research_clock.xdc').read_text()=='create_clock -name core_clk -period 10.000 [get_ports clk]\n'
 pilot=ROOT/'results/address64_endpoint_v3_20261024';pm=json.loads((pilot/'manifest.json').read_text());assert sha(pilot/'manifest.json')==m['parent_manifest_sha256']
 for p in (out/'sources').glob('*.sv'):assert sha(p)==sha(pilot/'endpoint/sources'/p.name)
 base=ROOT/'results/record_epoch6_synthesis_20261024';ba=json.loads((base/'final_audit.json').read_text());assert sha(base/'final_audit.json')==m['baseline_audit_sha256']
 assert sha(base/'utilization.rpt')==ba['artifacts']['utilization.rpt']
 current=resources(out/'utilization.rpt');old=resources(base/'utilization.rpt');assert old==ba['resources']
 text=(out/'utilization.rpt').read_text();assert 'Synthesized' in text and 'memory_scratch_endpoint_address64' in text and 'xcu280-fsvh2892-2L-e' in text
 ram=(out/'ram_cells.txt').read_text().splitlines();assert sum(1 if 'RAMB36' in s else .5 for s in ram)==current['BRAM']
 assert (out/'memory_scratch_endpoint_address64.dcp').stat().st_size>10000
 result={'status':'synthesis_evidence_verified','launch_manifest_sha256':sha(mp),'resources':current,'baseline_resources':old,'delta':{k:current[k]-old[k] for k in old},'artifacts':{p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='final_audit.json'},'source_sha256':sha(Path(__file__)),'physical_timing_complete':False,'platform_closed':False}
 (out/'final_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result['resources']));print(json.dumps(result['delta']))
if __name__=='__main__':main()
