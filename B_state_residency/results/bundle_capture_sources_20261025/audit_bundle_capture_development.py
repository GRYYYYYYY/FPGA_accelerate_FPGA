from pathlib import Path
import json,sys,struct,zlib
from run_checkpoint_authority import sha
from decode_bundle_directory import decode

def main():
 root=Path(sys.argv[1]).resolve();cases={}
 for name in ['bundle_capture_v1','bundle_capture_v2']:
  p=root/name;m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
  for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
  for case,cm in m['cases'].items():
   assert cm['outcome']=='recovered_retry'
   for n,h in cm['artifacts'].items():assert sha(p/case/n)==h
   base=Path(m['base'])/case
   for n in ['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin']:assert sha(p/case/n)==sha(base/n)
   rows=[t.split()for t in(p/case/'natural_trace.txt').read_text().splitlines()];by=lambda k:[t for t in rows if t[0]==k];assert len(by('BREADY'))==1 and by('BREADY')[0][4:]==['6','1','0','0']
   word=[0x51435031,1,0x9abcdef0,0x12345678,2,1,4,82,1,0];assert [(int(t[2]),int(t[3],16),int(t[4]))for t in by('QCM')]==[(i,w,int(i==9))for i,w in enumerate(word)]and int(by('BREADY')[0][2],16)==zlib.crc32(struct.pack('<10I',*word))
   assert [int(t[2])for t in by('QCP')]==[1,0]and len(by('BPATH'))==78
   if name=='bundle_capture_v2':
    d,r=decode(p/case/'directory.txt',p/case/'labels.bin',2,4);assert d['allocated']==120 and len(r)==328
  cases[name]={'status':'intermediate_capture_pass','manifest_sha256':sha(p/'manifest.json'),'limits':'No committed package; no selected default-generation import isolation test. v1 also lacks passive directory protocol capture.'}
 own=root/'source_bound_audit.json';a={'status':'passed','cases':cases,'files':{str(p.relative_to(root)):sha(p)for p in sorted(root.rglob('*'))if p.is_file()and p!=own},'auditor_sha256':sha(Path(__file__))};own.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'status':'passed','intermediate_runs':2}))
if __name__=='__main__':main()
