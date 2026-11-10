from pathlib import Path
from collections import defaultdict
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def raw(f):return struct.unpack('<I',struct.pack('<f',f))[0]
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 dep=ROOT/'results/candidate_decisions_20261024';dm=json.loads((dep/'manifest.json').read_text());assert m['base_manifest_sha256']==sha(dep/'manifest.json')
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 for n,h in dm['sources'].items():
  if n!='make_inputs.cpp':assert sha(out/'sources'/n)==h
 original=(dep/'sources/make_inputs.cpp').read_text();driver=(out/'sources/make_inputs.cpp').read_text()
 a=driver.index('\n std::ifstream edit(argv[3])');b=driver.index(' Router::SparseLabels labels;',a)
 assert (driver[:a]+driver[b:]).replace('check(argc==4);','check(argc==3);',1)==original
 assert 'r.incrementUser(en,ew)'in driver[a:b] and 'r.updatePresentCongestionCosts(1.25f)'in driver[a:b]
 own=ROOT/'results/candidate_initial_owner_20261024';cost=ROOT/'results/cost_state_inputs_20261025'
 assert m['base_owner_manifest_sha256']==sha(own/'manifest.json') and m['base_cost_manifest_sha256']==sha(cost/'manifest.json')
 before=bytearray((own/'owners.bin').read_bytes());after=(out/'owners.bin').read_bytes();ol=m['owner_layout'];ledger=defaultdict(dict)
 for node,net,refs in m['events']:
  assert net not in ledger[node];ledger[node][net]=refs
 seen=set();actual_samples=[]
 for node,entries in ledger.items():
  assert not any(before[node*16:node*16+16]);key,packed,ptr,reserved=struct.unpack_from('<4I',after,node*16);assert reserved==0
  decoded={key-1:packed&65535};occ=packed>>16
  while ptr:
   assert ptr not in seen and 0<ptr<=ol['pool_capacity'];seen.add(ptr)
   key,refs,ptr,reserved=struct.unpack_from('<4I',after,ol['pool_offset']+(ptr-1)*16);assert reserved==0 and key-1 not in decoded
   decoded[key-1]=refs
  assert decoded==entries and occ==len(entries)
  actual_samples.extend((node,net,refs,occ)for net,refs in entries.items())
  before[node*16:node*16+16]=after[node*16:node*16+16]
 assert seen==set(range(1,55)) and struct.unpack_from('<4I',after,ol['allocator_offset'])==(54,0,54,0)
 for offset,length in [(ol['pool_offset'],54*16),(ol['allocator_offset'],16)]:before[offset:offset+length]=after[offset:offset+length]
 assert bytes(before)==after
 cpu=[tuple(map(int,line.split())) for line in (out/'cpu_owner_samples.txt').read_text().splitlines()];assert actual_samples==cpu
 before=bytearray((cost/'real/initial.bin').read_bytes());after=(out/'cost.bin').read_bytes();cl=m['cost_layout']
 for i,x in enumerate(m['snapshots']):
  node=x['node'];expected=raw(1.25+i/8);assert expected==x['history_bits']==struct.unpack_from('<I',after,node*4)[0];struct.pack_into('<I',before,node*4,expected)
 table=b''.join(struct.pack('<I',raw(1 if i==0 else 1+i*1.25)) for i in range(256))
 assert table==(out/'cpu_prices.bin').read_bytes()==after[cl['prices_offset']:cl['prices_offset']+1024]
 before[cl['prices_offset']:cl['prices_offset']+1024]=table;assert bytes(before)==after
 for name in ['initial_design.bin','expected_design.bin']:assert (out/name).stat().st_size==ol['primary_bytes']==145424192
 assert sha(out/'initial_design.bin')==dm['artifacts']['initial_design.bin']
 assert all(c['exit_code']==0 for c in m['commands']) and 'EXPANSION_INPUTS_PASS'in(out/'execute.log').read_text()
 text=(out/'vectors.txt').read_text();assert sum(s.startswith('E ')for s in text.splitlines())==1212 and sum(s.startswith('A ')for s in text.splitlines())==m['coverage']['decisions'] and text.rstrip().endswith('Q 1 2 5')
 old_a=[s for s in (dep/'vectors.txt').read_text().splitlines() if s.startswith('A ')];new_a=[s for s in text.splitlines() if s.startswith('A ')]
 a={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'edited_nodes':len(ledger),'overflow_records':len(seen),'cpu_owner_rows_checked':len(cpu),'all_other_owner_cost_bytes_unchanged':True,'price_words_checked':256,'coverage':m['coverage'],'changed_A_rows':sum(x!=y for x,y in zip(old_a,new_a)) if len(old_a)==len(new_a) else None,'scope':'Scripted nonzero owner/history/factor changes on actual graph; unchanged original incrementUser and golden candidate methods, fresh CPU execution, full output integrity; not live route updates'}
 (out/'source_bound_audit.json').write_text(json.dumps(a,indent=2)+'\n');print(json.dumps(a,indent=2))
if __name__=='__main__':main()
