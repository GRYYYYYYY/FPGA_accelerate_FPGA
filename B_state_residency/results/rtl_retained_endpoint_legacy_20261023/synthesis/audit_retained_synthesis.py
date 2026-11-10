from pathlib import Path
import hashlib,json,re
from report_indexed_directory import resource_counts
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/rtl_retained_endpoint_legacy_20261023/synthesis'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((OUT/'completion_receipt.json').read_text());assert not r['is_command_running'] and r['last_completed_code']==0
assert 'rtl_retained_endpoint_legacy_20261023' in r['last_completed_output']
log=Path(r['log_file']).read_text();start=log.rfind('B_RETAINED_ENDPOINT_SYNTH_BEGIN version=');end=log.rfind('\nB_RETAINED_ENDPOINT_SYNTH_DONE')
assert start>=0 and end>start;log=log[start:end+len('\nB_RETAINED_ENDPOINT_SYNTH_DONE')]
assert 'ERROR:' not in log and 'CRITICAL WARNING:' not in log
(OUT/'synthesis_session.log').write_text(log+'\n')
sim=ROOT/'results/rtl_retained_endpoint_legacy_20261023/simulation_manifest.json';m=json.loads(sim.read_text())
for name,digest in m['sources'].items():assert sha(ROOT/name)==digest==sha(OUT.parent/'sources'/name)
assert (OUT/'memory_scratch_endpoint_retained.dcp').stat().st_size>10000
resources=resource_counts(OUT/'utilization.rpt');baseline=resource_counts(ROOT/'results/rtl_indexed_endpoint_20261023/synthesis/utilization.rpt')
assert resources['Register as Latch']==0 and resources['RAMB36/FIFO']==43
p=ROOT/'hardware/scripts/synthesize_retained_endpoint.tcl';(OUT/p.name).write_bytes(p.read_bytes())
result={'status':'passed','resources':resources,'baseline':baseline,'delta':{k:resources[k]-baseline[k] for k in resources},'warnings':re.findall(r'^WARNING:.*$',log,re.M),'simulation_manifest_sha256':sha(sim),'synthesis_source_sha256':sha(p),'audit_source_sha256':sha(Path(__file__)),'scope':'Default-capacity synthesis only; no implementation timing or board measurement','artifacts':{p.name:sha(p) for p in OUT.iterdir() if p.is_file()}}
(OUT/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))
