"""Bind the three original-CPU target conditions, six RTL cases and durable archives."""
from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1];BASE=Path('/tmp/B_state_residency_offer_20261025')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 profiles=[('free','early_inputs_v1','recursive_early_v2','recursive_early_backing_20261025.json',0,0,0,1),('foreign','occupied_target_inputs_v1','recursive_occupied_target_v1','recursive_occupied_target_backing_20261025.json',0,1,1,0),('shared','shared_target_inputs_v1','recursive_shared_target_v1','recursive_shared_target_backing_20261025.json',2,1,0,1)]
 records={};rtl=None;packets={};archives={}
 for name,inp_name,res_name,backing,refs,occ,index,early in profiles:
  inp=BASE/inp_name;out=BASE/res_name;im=json.loads((inp/'manifest.json').read_text());ig=json.loads((inp/'source_bound_audit.json').read_text());m=json.loads((out/'manifest.json').read_text());g=json.loads((out/'source_bound_audit.json').read_text());b=ROOT/'results'/backing;bg=json.loads(b.read_text())
  assert im['status']==ig['status']==m['status']==g['status']==bg['status']=='passed'
  assert ig['manifest_sha256']==sha(inp/'manifest.json')==m['input_manifest_sha256']
  assert g['manifest_sha256']==sha(out/'manifest.json')==bg['manifest_sha256']and bg['primary_audit_sha256']==sha(out/'source_bound_audit.json')
  current={n:v['sha256']for n,v in m['sources'].items()if n not in ['runner.py']and not Path(n).name.startswith('tb_')}
  assert len(current)==109
  if rtl is None:rtl=current
  else:assert current==rtl
  cpu=[l.split()for l in(inp/'cost_vectors.txt').read_text().splitlines()];packets[name]=[list(map(lambda x:int(x,16),t[2:]))for t in cpu];assert len(cpu)==2
  assert packets[name][1][1]==refs
  owner=(inp/'owners.bin').read_bytes();key,owner_refs,occupancy,ptr,reserved=struct.unpack_from('<IHHII',owner,256);same_refs=owner_refs if key==1 else 0
  assert (same_refs,occupancy)==(refs,occ)and ptr==reserved==0
  assert occ-(refs!=0)==index and int(not(occ>1 or(occ==1 and refs==0)))==early
  assert packets[name][1][4]==struct.unpack_from('<I',(inp/'cost.bin').read_bytes(),192+4*index)[0]
  assert set(g['counts'])=={'full','pressure'}
  for case,c in g['counts'].items():
   assert (c['outputs'],c['commits'],c['offers'],c['target_preserved'])==(2 if early else 3,2,1,True)
   assert c['ordered_native_cost_ACKs']==6 and c['final_native_records']==5
   assert sha(out/case/'labels.bin')==bg['cases'][case]['label_sha256']==m['cases'][case]['artifacts']['labels.bin']
   assert bg['cases'][case]['CPU_populated_frames']==5 and bg['cases'][case]['zero_frames']==16379
  for root in [inp,out]:
   idx=ROOT/'results/offer_archives_20261025'/(root.name+'.json');a=json.loads(idx.read_text());assert a['status']=='passed'and a['source_root']==str(root)and sha(Path(a['archive']))==a['archive_sha256'];archives[root.name]={'index_sha256':sha(idx),'archive_sha256':a['archive_sha256'],'files':len(a['members']),'bytes':Path(a['archive']).stat().st_size}
  records[name]={'input_root':str(inp),'result_root':str(out),'input_manifest_sha256':sha(inp/'manifest.json'),'input_audit_sha256':sha(inp/'source_bound_audit.json'),'manifest_sha256':sha(out/'manifest.json'),'audit_sha256':sha(out/'source_bound_audit.json'),'backing_audit_sha256':sha(b),'same_net_refs':refs,'occupancy':occ,'price_index':index,'early':bool(early),'cost_sharing_factor_bits':packets[name][1][23],'cost_total_bits':packets[name][1][27],'counts':g['counts']}
 # Device geometry and connection State are identical. Arithmetic packets differ
 # only in the source-use count and fetched price, preserving all other 21 words.
 for n in ['offsets.u32le','edges.u32le','nodes.rrt32','design.bin','expected_design.bin','connections.bin','rows.bin','columns.bin']:
  assert len({sha(Path(r['input_root'])/n)for r in records.values()})==1,n
 for n in ['cost.bin']:
  assert sha(BASE/'occupied_target_inputs_v1'/n)==sha(BASE/'shared_target_inputs_v1'/n)
 assert packets['free'][0]==packets['foreign'][0]==packets['shared'][0]
 for i in range(23):
  if i not in [1,4]:assert len({v[1][i]for v in packets.values()})==1,i
 r={'status':'passed','auditor_sha256':sha(Path(__file__)),'profiles':records,'archives':archives,'primary_RTL_dat_files_identical':109,'arithmetic_packet_only_varying_words':[1,4],'scope':'Three explicit synthetic target-state conditions with full+single-slot actual recursive pipeline. Initial owner snapshots, not mutable reference-update/overflow-pool or natural search traces. No performance or novelty claim.'}
 Path(sys.argv[1]).write_text(json.dumps(r,indent=2)+'\n');print('RECURSIVE_TARGET_MATRIX_PASS profiles=3 runs=6 archived_files='+str(sum(a['files']for a in archives.values())))
if __name__=='__main__':main()
