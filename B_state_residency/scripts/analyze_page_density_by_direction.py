"""Separate WB/RF sparse record work in hash-bound full public vectors."""
from pathlib import Path
from collections import Counter
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
 source=ROOT/'results/small_checkpoint_vectors_full_20261023';mb=(source/'manifest.json').read_bytes();m=json.loads(mb)
 ca=json.loads((source/'completion_audit.json').read_text());assert ca['status']=='passed' and ca['manifest_sha256']==hashlib.sha256(mb).hexdigest()
 commands_hash=hashlib.sha256();pages_hash=hashlib.sha256();hist={5:Counter(),6:Counter()};transfers=commands=0
 with (source/'actual.txt').open('rb') as cmd,(source/'pages.hex').open('rb') as pages:
  for line in cmd:
   commands_hash.update(line);commands+=1
   token=line.split(b' ',1)[0]
   if token in (b'5',b'6'):
    op=int(token,16);assert int(line.rsplit(None,1)[-1],16)==transfers
    words=[pages.readline() for _ in range(3)];assert all(len(w)==129 for w in words)
    for word in words:pages_hash.update(word)
    hist[op][(int(words[0],16)&255).bit_count()]+=1;transfers+=1
  assert not pages.read()
 assert commands_hash.hexdigest()==m['artifacts']['actual.txt'] and pages_hash.hexdigest()==m['artifacts']['pages.hex']
 assert commands==m['public_commands'] and transfers==m['transfers']
 rows={}
 for op,label in [(5,'writeback'),(6,'refill')]:
  pages=sum(hist[op].values());assert pages==m['counts'][str(op)]
  present=sum(k*v for k,v in hist[op].items());absent=8*pages-present
  rows[label]={'transfers':pages,'histogram':dict(sorted(hist[op].items())),'present_records':present,'absent_records':absent,'absent_record_fraction':absent/(8*pages),'payload_bytes':pages*192}
 global_density=json.loads((ROOT/'results/page_record_density_20261024/manifest.json').read_text());assert global_density['status']=='passed'
 assert sum(r['present_records'] for r in rows.values())==global_density['present_records']
 assert sum(r['absent_records'] for r in rows.values())==global_density['absent_records']
 result={'status':'passed','vector_manifest_sha256':ca['manifest_sha256'],'commands_sha256':commands_hash.hexdigest(),'pages_sha256':pages_hash.hexdigest(),'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'queries':38,'directions':rows,'refill_share_of_absent_records':rows['refill']['absent_records']/global_density['absent_records'],'scope':'Offline frozen transfer-occurrence work census, not full candidate execution or cycle savings.'}
 out=ROOT/'results/page_density_by_direction_20261024';out.mkdir();(out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
