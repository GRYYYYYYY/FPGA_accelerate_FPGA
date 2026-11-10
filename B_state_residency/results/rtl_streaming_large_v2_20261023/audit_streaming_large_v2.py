from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/rtl_streaming_large_v2_20261023'
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for chunk in iter(lambda:f.read(1<<20),b''):h.update(chunk)
 return h.hexdigest()
m=json.loads((OUT/'manifest.json').read_text());assert m['status']=='passed'
assert sha(OUT/'manifest.json')==json.loads((OUT/'completion_audit.json').read_text())['manifest_sha256']
assert len(m['commands'])==3 and all(c['exit_code']==0 for c in m['commands'])
for name,digest in m['sources'].items():assert sha(ROOT/name)==digest==sha(OUT/'sources'/name)
for name,digest in m['artifacts'].items():assert sha(OUT/name)==digest
vp=Path(m['vector_manifest']['path']);assert sha(vp)==m['vector_manifest']['sha256'];v=json.loads(vp.read_text())
for name,digest in v['artifacts'].items():assert sha(vp.parent/name)==digest
census=ROOT/'results/large_query_demand_20261023';d=json.loads((census/'manifest.json').read_text())
assert sha(census/'manifest.json')=='cbc1340cf62b89ea6b00e3f1a62a8476857a5ac3c36bc0a0ca78243a16c6fbda'
assert sha(census/'queries.json')==d['artifacts']['queries.json']
q={row['attempt']:row for row in json.loads((census/'queries.json').read_text())}
commands=transfers=fields=0;receipts=[]
for i,(attempt,line) in enumerate(zip(v['selected_attempts'],m['query_receipts']),1):
 row=q[attempt];commands+=row['public_commands'];transfers+=row['transfers'];fields+=row['accesses']
 receipt={k:int(val) for k,val in re.findall(r'(\w+)=(\d+)',line)}
 assert receipt['queries']==i and receipt['commands']==commands and receipt['transfers']==transfers
 receipt['attempt']=attempt;receipts.append(receipt)
assert len(receipts)==7 and fields==2110433
assert receipts[-1]['time_ps']==m['end_time_ns']*1000
old=(ROOT/'hardware/tb/tb_memory_endpoint_stream.sv').read_text()
new=(OUT/'sources/hardware/tb/tb_memory_endpoint_stream_v2.sv').read_text()
assert old.replace('#500000000000;',"#(64'd500000000000);").replace('time_ns=%0t','time_ps=%0t')==new
probe=ROOT/'results/watchdog_width_probe_20261023/manifest.json';assert json.loads(probe.read_text())['status']=='passed'
a={'status':'passed','manifest_sha256':sha(OUT/'manifest.json'),'watchdog_probe_sha256':sha(probe),'fields':fields,'receipts':receipts,'no_partial_run_mixing':True,'board_performance':None,'source_sha256':sha(Path(__file__))}
(OUT/'coverage_audit.json').write_text(json.dumps(a,indent=2)+'\n');(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(json.dumps(a,indent=2))
