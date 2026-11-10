"""Preserve the actual logical-seeding vs physical-empty-probe integration failure."""
from pathlib import Path
import sys,json,struct,zlib
from run_checkpoint_authority import sha
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='failed'and len(m['cases'])==1
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256']
assert 'raw_probe_build.py'not in m['sources'] and 'l_probe'not in(p/'sources/label_restore_controller.sv').read_text()
case=next(iter(m['cases']));d=p/case;rows=[x.split()for x in(d/'natural_trace.txt').read_text().splitlines()]
def by(k):return[t for t in rows if t[0]==k]
assert not by('I')and not by('Z')and not by('Z2')and not by('RELOAD')and not by('CHECK')and not by('ITER2_RETRY')and not by('WPR')and not by('WQR')
assert by('LABEL_CRC_RESULT')[0][2:]==['3','0','0','00000000']
assert by('ITER2_OWNER_REPAIRED')[0][2:]==['2','2'];assert len(by('BASELINE_TARGET_RESET'))==5 and all(t[2:]==['1','1','0']for t in by('BASELINE_TARGET_RESET'))
reset=next(i for i,t in enumerate(rows)if t[0]=='BASELINE_TARGET_RESET');post=rows[reset:]
miss=[t for t in post if t[0]=='BM'];replies=[t for t in post if t[0]=='BR'];assert len(miss)==len(replies)==1 and miss[0][2:]==['204279','0000000300010003']
im=json.loads((Path(m['baseline_image'])/'manifest.json').read_text());cpu=Path(im['source']);assert sha(cpu)==im['source_sha256']
with cpu.open('rb')as f:f.seek(204279*44);u=struct.unpack('<11I',f.read(44));v=[u[j]for j in [0,1,3,4,5]]
payload=sum(x<<(32*i)for i,x in enumerate(v));assert replies[0][2:]==['204279','0',f'{payload:040x}']
w=[t for t in post if t[0]=='NB'and t[2]=='3'];assert [(int(t[4])*8+int(t[6]),int(t[7]),int(t[8],16))for t in w]==[(204279,i,x)for i,x in enumerate(v)]
assert by('ABS')[-1][2]==f'{payload:040x}'and by('LX')[-1][2:]==['0','1',f'{payload:040x}']
source=[(int(t[2]),int(t[3],16))for t in by('LABEL_SNAPSHOT_RECORD')];assert len(source)==777 and len(dict(source))==777
crc=zlib.crc32(b''.join(struct.pack('<I',n)+v.to_bytes(20,'little')for n,v in source));assert by('LABEL_SNAPSHOT_DONE')[0][2:]==['777','389',f'{crc:08x}']
assert int(by('LABEL_SNAPSHOT_DONE')[0][1])<int(by('ITER2_G2_PUBLISHED')[0][1])<int(by('ITER2_OWNER_REPAIRED')[0][1])<int(by('ABS')[0][1])
assert(d/'owners.bin').read_bytes()==(d/'pool.bin').read_bytes();assert len((d/'owners.bin').read_bytes())==146284032
assert len([s for s in(d/'owner_axi.txt').read_text().splitlines()if s.startswith('W ')])==10
assert 'ITER2_PAIR_PASS'not in(d/'simulate.log').read_text()
r=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,counterexample=True,source_records=777,source_pages=389,source_crc=f'{crc:08x}',owner_repair_corrections=2,post_reset_probe_node=204279,unwanted_probe_seed_writes=5,probe_present=1,label_status=3,written=0,verified=0,limits=['Expected failed integration, not routing success. Logical baseline lookup made the mandatory empty-target probe nonempty; leaf correctly rejected it.','Simulation reached finite run bound while TB waited to send a stream the failed probe would not accept; no retry or completed warm restore. Raw-source/data proof only, full memory replay belongs to the passing fixed experiment.'])
(p/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print('BASELINE_PROBE_COUNTEREXAMPLE_AUDITED',case)
