"""Validate a committed reference bundle without accepting staging directories."""
from pathlib import Path
import json,sys,struct,zlib
from run_checkpoint_authority import sha

def verify(path,check_immutable=True):
 p=Path(path);assert p.name=='bundle'and not p.is_symlink()
 commit=json.loads((p/'COMMIT.json').read_text());m=json.loads((p/'manifest.json').read_text());assert commit['manifest_sha256']==sha(p/'manifest.json')and m['format']=='B_STATE_BUNDLE_1'and (commit['generation'],commit['checkpoint'])==(m['generation'],m['checkpoint'])
 required={'labels.bin','design.bin','cost.bin','owner_primary.bin','owner_pool.bin','owner_allocator.bin','query.bin','paths.bin','config_saved.bin','config_effective.bin','labels.records','journal_absorbed.u32','directory.json'};assert set(m['components'])==required
 for n,h in m['components'].items():
  f=p/n;assert f.is_file()and not f.is_symlink()and f.stat().st_size==h['bytes']and sha(f)==h['sha256'],n
 if check_immutable:
  assert set(m['immutable_resources'])=={'graph0','graph1','graph2','tables0','tables1','qstate0'}
  for n,h in m['immutable_resources'].items():f=Path(h['path']);assert f.stat().st_size==h['bytes']and sha(f)==h['sha256']
 ctx=m['context'];d=m['design'];g=m['generation'];version=ctx['version'];q=ctx['query'];price=ctx['price'];seq=ctx['sequence_floor'];assert 0<d<2**64 and 0<g<2**64 and 0<seq<2**32 and 0<version<2**32 and 0<=q<4 and 0<=price<16 and price==version&15 and 0<m['checkpoint']<2**32
 qb=(p/'query.bin').read_bytes();pb=(p/'paths.bin').read_bytes();assert len(qb)==40 and len(pb)==312 and zlib.crc32(qb)==m['query_crc32']and zlib.crc32(pb)==m['path_crc32'];qw=struct.unpack('<10I',qb);assert qw==(0x51435031,1,d&0xffffffff,d>>32,g&0xffffffff,g>>32,version,q+(price<<2)+64,seq,0)
 ps=struct.unpack('<78I',pb);keys=set();slots=0
 for slot in range(2):
  w=ps[slot*39:(slot+1)*39]
  if not w[0]:assert not any(w);continue
  valid,n,net,source,sink,lo,hi=w[:7];nodes=w[7:7+n];assert valid==1 and 0<n<=32 and net<m['net_count']and source<m['node_count']and sink<m['node_count']and lo+(hi<<32)==d and len(set(nodes))==n and all(0<=x<m['node_count']and x not in [source,sink]for x in nodes)and not any(w[7+n:]);keys|={(x,net)for x in nodes};slots|=1<<slot
 assert slots==m['path_slots']and m['restore_journal']==[]
 journal=list(struct.iter_unpack('<2I',(p/'journal_absorbed.u32').read_bytes()));assert len(journal)==len(set(journal))==m['absorbed_journal_count']and set(journal)==keys
 primary=(p/'owner_primary.bin').read_bytes();pool=(p/'owner_pool.bin').read_bytes();allocator=(p/'owner_allocator.bin').read_bytes();assert not pool and m['owner_pool_capacity']==0 and len(primary)==(m['node_count']*16+63)//64*64 and len(allocator)==64
 import hashlib
 h=hashlib.sha256();h.update(primary);h.update(allocator);assert h.hexdigest()==m['source_hashes']['owners.bin']
 for node,net in keys:assert struct.unpack_from('<4I',primary,node*16)==(net+1,65537,0,0)
 raw=struct.unpack('<72I',(p/'config_saved.bin').read_bytes());effective=struct.unpack('<72I',(p/'config_effective.bin').read_bytes());want=list(raw);want[70]=version;assert tuple(want)==effective and effective[5]==m['node_count']and effective[6]==m['net_count']
 directory=json.loads((p/'directory.json').read_text());image=(p/'labels.bin').read_bytes();records={n:list(r)for n,*r in struct.iter_unpack('<6I',(p/'labels.records').read_bytes())};assert len(records)==m['label_records']and len(directory['owners'])==directory['allocated']==m['directory_allocated']and directory['live_leases']==0
 decoded={};owners=set()
 for i,e in enumerate(directory['owners']):
  assert e['frame']==i and e['published']and e['owner']not in owners and e['owner']==e['page']+(q<<21)+(price<<23);owners.add(e['owner']);b=image[i*192:(i+1)*192];assert len(b)==192 and b[161:]==bytes(31)
  for slot in range(8):
   if b[0]>>slot&1:
    node=e['page']*8+slot;assert node<m['node_count']and node not in decoded;decoded[node]=list(struct.unpack_from('<5I',b,1+20*slot))
 assert decoded==records and len(image)==192*directory['physical_frames']
 assert m['recovery_attempt_floor']=={'version':version,'query':q}and m['checkpoint']==m['capture_baseline_checkpoint']+1
 return m
if __name__=='__main__':
 m=verify(sys.argv[1]);print(json.dumps({'status':'passed','generation':m['generation'],'checkpoint':m['checkpoint'],'labels':m['label_records'],'frames':m['directory_allocated']}))
