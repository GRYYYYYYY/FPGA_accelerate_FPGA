"""Reference healthy-boundary bundle from real RTL streams and stopped AXI images."""
from pathlib import Path
import json,sys,struct,shutil,zlib,os
from run_checkpoint_authority import sha
from decode_bundle_directory import decode

def dump_json(p,x):p.write_text(json.dumps(x,sort_keys=True,indent=2)+'\n')
def fsync_file(p):
 with p.open('rb')as f:os.fsync(f.fileno())
def fsync_dir(p):
 fd=os.open(p,os.O_RDONLY|os.O_DIRECTORY)
 try:os.fsync(fd)
 finally:os.close(fd)
def prepare(case):
 case=Path(case).resolve();run=json.loads((case.parent/'manifest.json').read_text());assert run['status']=='observed'and run['cases'][case.name]['status']=='observed'
 pre=json.loads((case.parent/'prebundle_audit.json').read_text());assert pre['status']=='passed'and pre['manifest_sha256']==sha(case.parent/'manifest.json')
 argv=run['cases'][case.name]['commands'][-1]['argv'];refs={}
 for i,x in enumerate(argv):
  if x=='--testplusarg':
   k,v=argv[i+1].split('=',1)
   if k in ['graph0','graph1','graph2','tables0','tables1','qstate0']:
    f=Path(v);refs[k]={'path':str(f),'bytes':f.stat().st_size,'sha256':sha(f)}
 assert len(refs)==6
 rows=[t.split()for t in(case/'natural_trace.txt').read_text().splitlines()];by=lambda k:[t for t in rows if t[0]==k]
 assert len(by('BCONTEXT'))==len(by('BFLOORS'))==len(by('BCFG'))==len(by('BREADY'))==1
 t=by('BCONTEXT')[0];design=int(t[1],16);generation=int(t[2],16);old_cp,version,query,price,published,sequence,slots=map(int,t[3:]);assert version==published and sequence>0 and old_cp<0xffffffff
 floors=list(map(int,by('BFLOORS')[0][1:]));assert floors==[version,query,price,version,query]
 ready=by('BREADY')[0];assert ready[5:]==['1','0','0'];qc_crc=int(ready[2],16);path_crc=int(ready[3],16);journal_count=int(ready[4])
 qrows=[t for t in by('QCM')if int(t[1])==1];assert len(qrows)==10 and all(int(t[2])==i and int(t[4])==int(i==9)for i,t in enumerate(qrows));qwords=[int(t[3],16)for t in qrows];qbytes=struct.pack('<10I',*qwords)
 assert zlib.crc32(qbytes)==qc_crc and qwords[:7]==[0x51435031,1,design&0xffffffff,design>>32,generation&0xffffffff,generation>>32,version]and qwords[7:]==[query+(price<<2)+64,sequence,0]
 pathrows=by('BPATH');assert len(pathrows)==78 and all(int(t[1])==i and int(t[3])==int(i==77)for i,t in enumerate(pathrows));pwords=[int(t[2],16)for t in pathrows];pbytes=struct.pack('<78I',*pwords);assert zlib.crc32(pbytes)==path_crc
 pathkeys=set()
 for slot in range(2):
  words=pwords[slot*39:(slot+1)*39];valid,n,net,source,sink,lo,hi=words[:7]
  if not valid:assert words==[0]*39;continue
  assert valid==1 and 0<n<=32 and lo+(hi<<32)==design;nodes=words[7:7+n];assert len(set(nodes))==n and source not in nodes and sink not in nodes and words[7+n:]==[0]*(32-n)
  pathkeys|={(node,net)for node in nodes}
 raw_cfg=int(by('BCFG')[0][1],16).to_bytes(288,'little');cfg=list(struct.unpack('<72I',raw_cfg));node_count=cfg[5];net_count=cfg[6];assert cfg[2]+(cfg[3]<<32)==design and cfg[66]+(cfg[67]<<32)==design and node_count>0 and net_count>0
 current_cfg=cfg.copy();current_cfg[70]=version;effective=struct.pack('<72I',*current_cfg)
 primary_bytes=(node_count*16+63)//64*64;live=(case/'owners.bin').read_bytes();assert len(live)==primary_bytes+64
 allocator=live[primary_bytes:];primary=live[:primary_bytes];original=(case/'primary.bin').read_bytes();assert len(original)==len(primary)and allocator==(case/'allocator.bin').read_bytes()
 journal=[tuple(map(int,t[2:]))for t in by('BJ')];assert len(journal)==journal_count and len(set(journal))==journal_count and set(journal)==pathkeys
 changed=set()
 for off in range(0,len(primary),65536):
  if primary[off:off+65536]!=original[off:off+65536]:
   for j in range(off,min(off+65536,len(primary)),16):
    if primary[j:j+16]!=original[j:j+16]:changed.add(j//16)
 assert changed=={n for n,net in journal}
 for n,net in journal:assert 0<=n<node_count and 0<=net<net_count and struct.unpack_from('<4I',primary,n*16)==(net+1,65537,0,0)
 directory,records=decode(case/'directory.txt',case/'labels.bin',query,price)
 actual_z={int(t[2]):list(struct.unpack('<5I',int(t[3],16).to_bytes(20,'little')))for t in by('Z')};assert records==actual_z and all(n<node_count for n in records)
 stage=case/'bundle.staging';dest=case/'bundle';assert not stage.exists()and not dest.exists();stage.mkdir();source_hashes={n:sha(case/n)for n in ['natural_trace.txt','directory.txt','owners.bin','labels.bin','design.bin','cost.bin']}
 for n in ['labels.bin','design.bin','cost.bin']:shutil.copyfile(case/n,stage/n)
 (stage/'owner_primary.bin').write_bytes(primary);(stage/'owner_pool.bin').write_bytes(b'');(stage/'owner_allocator.bin').write_bytes(allocator)
 (stage/'query.bin').write_bytes(qbytes);(stage/'paths.bin').write_bytes(pbytes);(stage/'config_saved.bin').write_bytes(raw_cfg);(stage/'config_effective.bin').write_bytes(effective)
 (stage/'labels.records').write_bytes(b''.join(struct.pack('<6I',n,*record)for n,record in sorted(records.items())))
 (stage/'journal_absorbed.u32').write_bytes(b''.join(struct.pack('<2I',n,net)for n,net in journal));dump_json(stage/'directory.json',directory)
 for q in stage.iterdir():fsync_file(q)
 components={q.name:{'bytes':q.stat().st_size,'sha256':sha(q)}for q in sorted(stage.iterdir())if q.is_file()}
 manifest={'format':'B_STATE_BUNDLE_1','design':design,'generation':generation,'checkpoint':old_cp+1,'capture_baseline_checkpoint':old_cp,'context':{'version':version,'query':query,'price':price,'sequence_floor':sequence},'node_count':node_count,'net_count':net_count,'path_slots':slots,'owner_pool_capacity':0,'query_words':10,'path_words':78,'query_crc32':qc_crc,'path_crc32':path_crc,'label_records':len(records),'directory_allocated':directory['allocated'],'restore_journal':[],'absorbed_journal_count':journal_count,'recovery_attempt_floor':{'version':floors[3],'query':floors[4]},'frontier_policy':'empty at capture; reconstruct empty frontier','directory_policy':'authoritative mapping reconstructed from passive accepted protocol; nonauthoritative index must be rebuilt','cookie_policy':'all leases retired at healthy boundary; cold restart must reset endpoint and directory freshness coherently','configuration_policy':'raw saved descriptor plus explicit current-version override at word70, matching RTL config_restore.cfg_payload','publication_scope':'Host reference filesystem commit from stopped simulation under held RTL lease; not in-place authority rotation or hardware metadata export','source_hashes':source_hashes,'immutable_resources':refs,'components':components}
 dump_json(stage/'manifest.json',manifest);fsync_file(stage/'manifest.json');commit={'manifest_sha256':sha(stage/'manifest.json'),'generation':generation,'checkpoint':old_cp+1};dump_json(stage/'COMMIT.json',commit);fsync_file(stage/'COMMIT.json');fsync_dir(stage);stage.rename(dest);fsync_dir(case)
 for n,h in source_hashes.items():assert sha(case/n)==h
 return commit
if __name__=='__main__':print(json.dumps(prepare(sys.argv[1])))
