from pathlib import Path
import json,sys,struct,zlib
from run_checkpoint_authority import ROOT,sha

def main():
 p=Path(sys.argv[1]).resolve();cases={};base=Path('/tmp/B_state_residency_offer_20261025/authority_query_v4')
 for n in ['query_checkpoint_join_v1','query_checkpoint_join_v2']:
  d=p/n;m=json.loads((d/'manifest.json').read_text());assert m['status']=='observed'
  for f,h in m['sources'].items():assert sha(d/'sources'/f)==h['sha256']
  for name,c in m['cases'].items():
   assert c['outcome']=='recovered_retry'
   for f,h in c['artifacts'].items():assert sha(d/name/f)==h
   for f in ['graph_axi.txt','cost_axi.txt','design_axi.txt','owner_axi.txt','label_axi.txt','qstate_axi.txt','table_axi.txt','snapshot_axi.txt','owners.bin','labels.bin','cost.bin','design.bin']:assert sha(d/name/f)==sha(base/name/f)
   rows=[t.split()for t in(d/name/'natural_trace.txt').read_text().splitlines()];cp=[t for t in rows if t[0]=='QCP'];assert len(cp)==3 and [int(t[2])for t in cp]==[0,1,0]
   image=[0x51435031,1,0x9abcdef0,0x12345678,1,1,4,82,1,0];crc=zlib.crc32(struct.pack('<10I',*image));assert all(int(t[3],16)==crc for t in cp)
   assert any(t[0]=='QCP_REJECT'and t[2:]==['1','0','0']for t in rows)
  cases[n]={'status':'intermediate_behavioral_pass','manifest_sha256':sha(d/'manifest.json'),'scope':'Two-capacity diagnostic-only restore with CRC rejection; superseded by selected generation rejection and production/default-off tests.'}
 own=p/'source_bound_audit.json';a={'status':'passed','cases':cases,'auditor_sha256':sha(Path(__file__)),'files':{str(f.relative_to(p)):sha(f)for f in sorted(p.rglob('*'))if f.is_file()and f!=own},'scope':'Preserve intermediate runs without promoting them to selected production evidence.'};own.write_text(json.dumps(a,indent=2)+'\n');print(json.dumps({'status':'passed','cases':2}))
if __name__=='__main__':main()
