"""Transfer byte-identical audited query prefix, then independently audit new G3 exports/publication.
No manufactured trace view is supplied to the old auditor; the old artifact and its
restored audit are pinned, and every compared prefix is checked on original files.
"""
from pathlib import Path
import hashlib,json,runpy,struct,sys,zlib
from run_checkpoint_authority import ROOT,sha
from audit_route_fault_axi import replay
p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());receipt_only_failure=m['status']=='failed';assert receipt_only_failure and 'AssertionError'in m['error']and len(m['cases'])==1
case=next(iter(m['cases']));c=m['cases'][case];assert c['status']=='running'and all(x['exit_code']==0 for x in c['commands'])and len(c['commands'])==3
d=p/case;negative='--negative'in c['commands'][-1]['argv'] # flags are plusargs below, not simulator argv options
args=c['commands'][-1]['argv'];negative='g3negative=1'in args;fixed='KEEP_RECEIPT_ON_BUSY(1)'in(p/'sources/tb_query_fault.sv').read_text();assert not negative and fixed
for n,h in m['sources'].items():assert sha(p/'sources'/n)==h['sha256'],n
ref=p.parent/('cumulative_owner_system_'+case+'_v4');a=json.loads((ref/'source_bound_audit.json').read_text())
report=json.loads((ROOT/'results/cumulative_owner_system_20261027.json').read_text());assert report['cases'][ref.name]==a
rest=json.loads((ROOT/'results'/(ref.name+'_restore_20261025.json')).read_text());assert rest['audit_byte_identical']and rest['audit_sha256']==sha(ref/'source_bound_audit.json')
assert a['manifest_sha256']==sha(ref/'manifest.json')and a['auditor_sha256']==sha(ROOT/'scripts/audit_cumulative_owner_system.py')
rm=json.loads((ref/'manifest.json').read_text());allowed=['tb_query_fault.sv','runner.py','iter2_build_tb.py','cumulative_owner_snapshot.sv','export_manifest.sv','publish_build_tb.py']
for n,h in m['sources'].items():
 if n not in allowed:assert h['sha256']==rm['sources'][n]['sha256'],n
assert m['rtl']==['export_manifest.sv']+rm['rtl']
b=runpy.run_path(str(p/'sources/iter2_build_tb.py'));b['make'].__globals__['ROOT']=ROOT
assert b['make']()==(p/'sources/tb_query_fault.sv').read_text()
if fixed:
 unit=p.parent/'owner_receipt_busy_unit_v2';assert json.loads((unit/'source_bound_audit.json').read_text())['status']=='passed'
 assert sha(p/'sources/cumulative_owner_snapshot.sv')==sha(unit/'sources/cumulative_owner_snapshot.sv')
else:assert sha(p/'sources/cumulative_owner_snapshot.sv')==sha(ref/'sources/cumulative_owner_snapshot.sv')
unit=p.parent/'export_manifest_unit_v1';assert json.loads((unit/'source_bound_audit.json').read_text())['status']=='passed'
assert sha(p/'sources/export_manifest.sv')==sha(unit/'sources/export_manifest.sv')
assert sha(Path(m['binding']))==json.loads((ref/'manifest.json').read_text())['binding_sha256']
def prefix(path):
 out=[]
 for line in path.read_bytes().splitlines(keepends=True):
  out.append(line)
  if line.startswith(b'CUMULATIVE_G3_CANDIDATE '):return b''.join(out)
 raise AssertionError('missing G3 candidate')
assert prefix(d/'natural_trace.txt')==prefix(ref/case/'natural_trace.txt')
allrows=[t.split()for t in(d/'natural_trace.txt').read_text().splitlines()]
cut=next(i for i,t in enumerate(allrows)if t[0]=='CUMULATIVE_G3_CANDIDATE');rows=allrows[cut+1:]
def by(tag):return[t for t in rows if t[0]==tag]
# Every old physical transaction remains byte-identical; only label-snapshot and
# authority-read files may append actual G3 operations.
prefix_counts={}
for tag in ['graph','design','table','label','owner','cost','qstate','snapshot','copy','labelsnap','baseline','g3copy']:
 old=(ref/case/(tag+'_axi.txt')).read_bytes();new=(d/(tag+'_axi.txt')).read_bytes();assert new.startswith(old),tag
 if tag not in ['snapshot','labelsnap']:assert new==old,tag
 prefix_counts[tag]=len(old.splitlines())
for n in ['owners.bin','g3.bin','pool.bin','snapshot.bin','cost.bin','design.bin','labels.bin']:
 assert (d/n).read_bytes()==(ref/case/n).read_bytes(),n
assert sha(d/'g3.bin')==a['working_owner_sha256']==sha(d/'owners.bin')and sha(d/'pool.bin')==a['g2_authority_sha256']
# G3 labels: real native directory entries, physical DDR reads, full CPU final bits.
records=[(int(t[2]),int(t[3],16))for t in by('G3_LABEL_RECORD')];assert len(records)==781 and len(dict(records))==781
misses={int(t[2])for t in allrows[:cut]if t[0]=='BM'};assert set(dict(records))==misses
cpu=p.parent/'followup_iter2_next_v1';expected={}
with(cpu/'search_final_nodes.u32').open('rb')as f:
 for node in misses:
  f.seek(node*44);u=struct.unpack('<11I',f.read(44));v=[u[j]for j in [0,1,3,4,5]]
  if node==67922:v[4]=0
  expected[node]=sum(w<<(32*i)for i,w in enumerate(v))
assert dict(records)==expected
raw=b''.join(struct.pack('<I',n)+v.to_bytes(20,'little')for n,v in records);label_crc=zlib.crc32(raw)
assert by('G3_LABEL_DONE')[0][2:]==['781','393',f'{label_crc:08x}']
file_records=[(int(t[0]),sum(int(w,16)<<(32*i)for i,w in enumerate(t[1:])))for t in map(str.split,(d/'runtime_g3_labels.txt').read_text().splitlines())];assert file_records==records
scan=by('G3_FRAME_REPLY');requests=by('G3_FRAME_REQUEST');assert len(scan)==len(requests)==394
assert [int(t[2])for t in requests]==list(range(394))and scan[-1][2:]==['6','393','0000000','0']
frame_pages={}
for frame,t in enumerate(scan[:-1]):
 owner=int(t[4],16);assert t[2]=='0'and int(t[3])==frame and t[5]=='1'and owner>>21==23
 frame_pages[frame]=owner&((1<<21)-1)
assert len(set(frame_pages.values()))==393 and set(frame_pages.values())=={n//8 for n in misses}
pages={}
for n,v in expected.items():
 page,slot=divmod(n,8);buf=pages.setdefault(page,bytearray(192));buf[0]|=1<<slot;buf[1+20*slot:21+20*slot]=v.to_bytes(20,'little')
snap=[t.split()for t in(d/'labelsnap_axi.txt').read_text().splitlines()][prefix_counts['labelsnap']:];assert len(snap)==2358
backing=(d/'labels.bin').read_bytes()
for i in range(1179):
 ar,r=snap[2*i:2*i+2];frame,chunk=divmod(i,3);address=frame*192+chunk*64
 assert ar==['A',f'{address:08x}','1']or ar==['A',f'{address:016x}','1']
 assert r[0]=='R'and int(r[1],16)==address and r[3]=='0'
 value=int(r[2],16).to_bytes(64,'little');assert value==pages[frame_pages[frame]][chunk*64:(chunk+1)*64]==backing[address:address+64]
# Native full two-path export and exact selected-generation query image.
path=[int(t[3],16)for t in by('G3_PATH_WORD')];assert len(path)==78 and [int(t[2])for t in by('G3_PATH_WORD')]==list(range(78))
path_expected=[]
for sink,first in [(204279,339193),(67922,990179)]:path_expected +=[1,3,26422,66893,sink,0x9abcdef0,0x12345678,first,558358,265324]+[0]*29
assert path==path_expected
assert [(int(t[1]),int(t[2],16),int(t[3]))for t in by('BPATH')]==[(i,w,int(i==77))for i,w in enumerate(path)]
pcrc=zlib.crc32(struct.pack('<78I',*path));assert by('G3_PATH_RESULT')[0][2]==f'{pcrc:08x}'
query=[int(t[3],16)for t in by('G3_QUERY_WORD')];assert query==[0x51435031,1,0x9abcdef0,0x12345678,3,1,5,0x57,180328,0]
assert [int(t[2])for t in by('G3_QUERY_WORD')]==list(range(10))
qcrc=zlib.crc32(struct.pack('<10I',*query));exports={}
for t in by('QCM'):exports.setdefault(int(t[1]),[]).append((int(t[2]),int(t[3],16),int(t[4])))
assert len(exports)==(1 if negative or receipt_only_failure else 2)
for batch,v in exports.items():assert v==[(i,w,int(i==9))for i,w in enumerate(query)]
assert all(t[2:]==['0',f'{qcrc:08x}','0','180328']for t in by('QCP'))and len(by('QCP'))==len(exports)
bundle=by('G3_BUNDLE');assert len(bundle)==1 and bundle[0][2:]==['781',f'{label_crc:08x}',f'{pcrc:08x}',f'{qcrc:08x}']+(['0','0','0']if negative else['1','1','1'])
held=by('G3_AUTH_HELD');assert len(held)==8 and all(t[2:]==(['0','0','0','0']if negative else['0','0','1','0'])for t in held)
# Full read-only AXI byte replay from G1/G2/G3 authority windows.
regions=[(0x91fffff000,d/'snapshot.bin'),(0xa000000000,d/'pool.bin'),(0xc000000000,d/'g3.bin')]
authority=replay(d/'snapshot_axi.txt',regions,None);assert authority['write_beats']==0 and authority['error_read_beats']==0
pubs=by('JP');assert len(pubs)==(0 if negative or receipt_only_failure else 1)
if negative or receipt_only_failure:
 assert not by('G3_PUBLISH_BLOCKED')and not by('G3_PUBLISHED')and not by('APQ')
 assert by('JKR')[0][2:]==['0','18','3']and by('JCR')[0][2:]==['0','18']
 assert authority['read_beats']==43
else:
 assert pubs[0][2:]==['7','18','18','3','0000000100000002']
 assert by('G3_PUBLISHED')[0][2:]==['0000000100000003','19','5','3','180328']and not by('G3_PUBLISH_BLOCKED')
 assert len(by('APQ'))==len(by('APR'))==6
 assert [(int(t[2]),int(t[3]),t[4])for t in by('APQ')]==[(339193,26422,'0000000100000002'),(339193,26422,'0000000100000003'),(990179,26422,'0000000100000003'),(558358,26422,'0000000100000003'),(558358,23916,'0000000100000003'),(265324,26422,'0000000100000003')]
 assert [t[2:6]for t in by('APR')]==[[s,r,o,'0000000100000003']for s,r,o in [('1','0','0'),('0','1','1'),('0','2','2'),('0','4','2'),('0','1','2'),('0','5','1')]]
 assert by('JE')[0][2:]==['0','19','0','19','1']
 assert authority['read_beats']>43
log=(d/'simulate.log').read_text();assert log.count('Fatal:')==1 and 'Fatal: G3 prepared identity/manifest'in log and '$finish called'in log
assert 'G3_PUBLISH_PASS'not in log
result=dict(status='passed',manifest_sha256=sha(p/'manifest.json'),auditor_sha256=sha(Path(__file__)),case=case,negative=True,fixed=fixed,counterexample='copy admission includes ordinary-work permit disabled by native prepare',system_manifest_status=m['status'],reference_audit_sha256=sha(ref/'source_bound_audit.json'),query_prefix_byte_identical=True,prefix_sha256=hashlib.sha256(prefix(d/'natural_trace.txt')).hexdigest(),axi_interfaces_audited=12,working_owner_bytes=146284032,g3_owner_sha256=sha(d/'g3.bin'),g2_owner_sha256=sha(d/'pool.bin'),g3_labels=781,g3_pages=393,g3_label_read_beats=1179,g3_label_crc=f'{label_crc:08x}',g3_path_words=78,g3_path_crc=f'{pcrc:08x}',g3_query_words=10,g3_query_crc=f'{qcrc:08x}',query_floor=180328,source_context=[5,3,5],published_checkpoint=18,published_generation=0x100000002,journal=3,authority=authority,scope='Actual native G3 export and prepare/publication or old writer receipt readiness counterexample. Source query prefix and12physical prefixes byte-identical to restored audited candidate. No new q3, G3 warm recovery, persistent writer/authentication, arbitrary reprice or board proof.')
(p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print('OWNER_G3_AUDITED',case,'verified receipt-only failure')
