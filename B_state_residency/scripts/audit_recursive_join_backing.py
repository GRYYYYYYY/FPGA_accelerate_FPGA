"""Independent whole-image label semantics, allowing allocator frame permutation."""
from pathlib import Path
from collections import Counter
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());a=json.loads((out/'source_bound_audit.json').read_text());assert m['status']==a['status']=='passed'and a['manifest_sha256']==sha(out/'manifest.json')
 inp=Path(m['input']);ig=json.loads((inp/'source_bound_audit.json').read_text());assert ig['status']=='passed'and ig['manifest_sha256']==sha(inp/'manifest.json')==m['input_manifest_sha256']
 codec=out/'sources/expansion_20261024/pager/backend/scratch_page_codec_small_static.sv';assert sha(codec)==m['sources'][str(codec.relative_to(out/'sources'))]['sha256']
 source=codec.read_text();assert 'page[8 +:160]'in source and 'record_out_present=page[node]'in source
 labels={int(t[0]):[int(x,16)for x in t[1:]]for t in(l.split()for l in(inp/'final_labels.txt').read_text().splitlines())}
 assert set(labels)=={0,8,16,24,32}
 expected=Counter(bytes([1])+struct.pack('<5I',*v)+bytes(171)for v in labels.values());expected[bytes(192)]+=16384-5
 cases={}
 for case in ['full','pressure']:
  p=out/case/'labels.bin';data=p.read_bytes();assert len(data)==3145728
  actual=Counter(data[i:i+192]for i in range(0,len(data),192));assert actual==expected,'whole physical image differs from independently encoded CPU labels'
  cases[case]={'label_sha256':sha(p),'physical_frames':16384,'CPU_populated_frames':5,'zero_frames':16379,'bytes_compared':len(data)}
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'primary_audit_sha256':sha(out/'source_bound_audit.json'),'auditor_sha256':sha(Path(__file__)),'codec_sha256':sha(codec),'cases':cases,'scope':'All 16384 physical 192B pages match original CPU final labels plus zero unused pages, modulo allocator frame permutation; primary audit also checks five tagged native reads and complete byte journals.'}
 target=Path(sys.argv[2]);target.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
