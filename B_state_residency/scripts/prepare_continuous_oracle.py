from pathlib import Path
import json,struct,mmap,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();q1=ROOT/'results/natural_query_v2';q2=ROOT/'results/followup_q2_v1';i1=ROOT/'results/natural_query_inputs_v1'
 union=set()
 for p in [ROOT/'results/natural_query_oracle_v1',ROOT/'results/followup_q2_oracle_v1']:union.update(v[0]for v in struct.iter_unpack('<6I',(p/'initial_label_imports.u32').read_bytes()))
 assert len(union)==328
 for name,snapshot in [('initial_label_imports.u32',q1/'initial_nodes.u32'),('expected_label_reads.u32',q1/'search_final_nodes.u32'),('prepared.u32',q2/'initial_nodes.u32'),('final2.u32',q2/'search_final_nodes.u32')]:
  with snapshot.open('rb')as f,(out/name).open('wb')as g,mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)as m:
   for node in sorted(union):
    v=struct.unpack_from('<11I',m,node*44);g.write(struct.pack('<6I',node,v[0],v[1],v[3],v[4],v[5]))
 a=dict(status='passed',runner_sha256=sha(Path(__file__)),input_audit_sha256=sha(i1/'source_bound_audit.json'),capture_audits={str(p):sha(p/'source_bound_audit.json')for p in [q1,q2]},label_import_records=328,scope='One initial q1 import of union CPU-known read footprints; authoritative q1 final/q2 prepared/q2 final snapshots. No q2 label reload.',artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()})
 (out/'manifest.json').write_text(json.dumps(a,indent=2)+'\n');a['manifest_sha256']=sha(out/'manifest.json');(out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print('CONTINUOUS_ORACLE_READY')
if __name__=='__main__':main()
