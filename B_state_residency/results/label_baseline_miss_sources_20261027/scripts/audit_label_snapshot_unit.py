from pathlib import Path
import sys,json,struct,re,zlib
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='observed'
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
assert all(c['exit_code']==0 for c in m['commands'])
raw=(p/'labels.bin').read_bytes();assert len(raw)==1536
pending=None;count=errors=0
for t in map(str.split,(p/'labelsnap_axi.txt').read_text().splitlines()):
 if t[0]=='A':assert pending is None and t[2]=='1';pending=int(t[1],16)
 else:
  assert t[0]=='R'and int(t[1],16)==pending and t[3]in ['0','2'];a=pending;pending=None
  assert int(t[2],16).to_bytes(64,'little')==raw[a:a+64];count+=1;errors+=t[3]=='2'
assert pending is None and count==23 and errors==1
log=(p/'simulate.log').read_text();assert 'LABEL_SNAPSHOT_UNIT_PASS checks=102'in log and 'Fatal:'not in log
results=[tuple(map(int,t[:4]))+(int(t[4],16),)for t in re.findall(r'LABEL_UNIT_RESULT (\d+) (\d+) (\d+) (\d+) ([0-9a-f]+)',log)]
rows=[]
for n in [0,2,7,17]:rows.append((n,tuple(0x10000000+f*256+n for f in range(5))))
crc=zlib.crc32(b''.join(struct.pack('<6I',n,*v)for n,v in rows))
assert results==[(1,0,4,2,crc),(2,4,4,2,0),(3,5,0,0,0),(4,2,0,0,0),(5,2,0,0,0),(6,6,4,3,0)]
records=[(int(phase),int(n),int(v,16))for phase,n,v in re.findall(r'LABEL_UNIT_RECORD (\d+) (\d+) ([0-9a-f]+)',log)]
assert records==[(phase,n,sum(w<<(32*i)for i,w in enumerate(v)))for phase in [1,2,6]for n,v in rows]
a={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'checks':102,'read_beats':count,'error_read_beats':errors,'results':results,'scope':'Native directory populated/reserved/pinned/published/retired via commands; only permitted frame scan exposes owner and published state, normal requests blocked while reply held. Actual DDR read stream and CRC independently replayed, including context filtering, unpublished page, R error, in-flight R cancellation, scan backpressure cancellation, padding corruption. Not a system or synthesis proof.'}
(p/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print('LABEL_SNAPSHOT_UNIT_AUDITED')
