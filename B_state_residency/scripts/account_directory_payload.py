"""Analytic metadata payload accounting; not synthesized BRAM utilization."""
from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 out=ROOT/'results/directory_payload_accounting_20261023';out.mkdir()
 specs=[('64node_default',23405,15,15,24,4,64),('8node_default',163840,18,18,27,32,8),('8node_trace_capacity_candidate',65536,16,17,27,32,8)]
 rows=[]
 for name,frames,index_bits,hash_bits,owner_bits,slots,nodes in specs:
  owner=frames*(owner_bits+1);index=(1<<hash_bits)*(8+index_bits)
  rows.append({'name':name,'frames':frames,'owner_bits_total':owner,'index_bits_total':index,'metadata_KiB':(owner+index)/8192,'resident_data_and_valid_bits':slots*nodes*137,'scope':'raw array payload only; excludes lease/control/FIFO/codec, RAM shape and replication'})
 pp=ROOT/'results/small_page_checkpoint_20261023/manifest.json';p=json.loads(pp.read_text());assert p['status']=='passed';peak=max(q['backing_pages'] for q in p['queries']);assert peak==59843 and peak<65536
 result={'status':'computed','rows':rows,'captured_peak_published_pages':peak,'planner_sha256':hashlib.sha256(pp.read_bytes()).hexdigest(),'candidate_is_default_capacity_equivalent':False,'candidate_limitation':'65536-frame candidate only fits these captured queries; it does not provide the default30MiB/163840-frame capacity. Neither candidate synthesized nor checkpoint/RTL large-capacity equivalence tested.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
 (out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
