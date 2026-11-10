#!/usr/bin/env python3
"""Check exact model edit ledgers: all other protocol text must remain unchanged."""
import argparse,hashlib,json,re
from pathlib import Path
from check_vitis_kernel import digest,require
ROOT=Path(__file__).resolve().parents[1]
def sha(s):return hashlib.sha256(s.encode()).hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--bundle',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();require(not a.output.exists(),'Refuse overwrite')
 plan=json.loads((a.bundle/'plan.json').read_text());original=Path(plan['original_sim']);files={};counts={};models=[]
 require(plan['transactions']==30 and plan['pointers']==13 and len(plan['models'])==10,'Different snapshot model matrix')
 require({Path(m['path']).name for m in plan['models']}=={p.name for p in (original/'verilog').glob('AESL_axi_master_*.v')},'Incomplete model set')
 for p,h in plan['files'].items():require(digest(p)==h,'Changed preflight input '+p);files[p]=h
 for model in plan['models']:
  target=Path(model['path']);ledger=Path(model['ledger']);r=json.loads(ledger.read_text());source=original/'verilog'/target.name;text=source.read_text()
  require(digest(source)==model['before_sha256']==r['input_sha256'] and digest(target)==model['after_sha256']==r['output_sha256'],'Model artifact changed')
  require(r['storage_only'] and r['pages']==model['pages'],'Page count differs')
  require([x['kind'] for x in r['phases']]==['storage_declarations','procedural_memory_writes','low16_reads','packed_bit_reads','whole_word_reads'],'Unexpected transformation phase')
  for phase in r['phases']:
   require(sha(text)==phase['before_sha256'],'Wrong source phase hash');previous=-1
   for e in phase['edits']:
    require(previous<=e['start']<e['end'] and text[e['start']:e['end']]==e['old'],'Invalid/overlapping edit span');previous=e['end'];kind=phase['kind']
    if kind=='storage_declarations':
     require(re.fullmatch(r"\s*reg\s*\[[^\]]+\]\s*\w+_mem_\d+\s*\[[^\]]+\]\s*=\s*'\{\s*default\s*:\s*'h0\s*\};\s*",e['old']) is not None,'Not an original zero storage declaration')
     if e['new']:
      writes=set(re.findall(r'\b(\w+)\s*(?:<=|=(?!=))',e['new']));require(writes<= {'a_storage_id','a_storage_commit','value'},'New helper writes protocol state')
      require('TRAN_' not in e['new'] and '#' not in e['new'],'Helper changes interface or time delays')
      require(e['new'].count('always @(a_storage_commit)')==1,'Wrong NBA commit event')
    else:
     require('_mem_' in e['old'] and e['new'].startswith('a_storage_'),'Edit outside storage access')
     if kind=='procedural_memory_writes':require(e['new'].startswith('a_storage_write_') and re.search(r'\)\);$',e['new']) is not None,'Wrong write hook')
     elif kind=='low16_reads':require(e['new'].startswith('a_storage_read_low16(') and re.search(r'\[15:0\]\s*$',e['old']) is not None,'Wrong low16 read hook')
     elif kind=='packed_bit_reads':require(e['new'].startswith('a_storage_read_bit('),'Wrong bit read hook')
     else:require(e['new'].startswith('a_storage_read('),'Wrong word read hook')
   for e in reversed(phase['edits']):text=text[:e['start']]+e['new']+text[e['end']:]
   require(sha(text)==phase['after_sha256'],'Edit ledger replay differs');counts[phase['kind']]=counts.get(phase['kind'],0)+len(phase['edits'])
  require(text==target.read_text(),'Unlisted protocol/model edits')
  for q in [source,target,ledger]:files[str(q)]=digest(q)
  models.append(dict(bundle=r['bundle'],pages=r['pages'],exact_protocol_text_preserved_except_storage=True))
 for q in [a.bundle/'plan.json',Path(__file__).resolve()]:files[str(q)]=digest(q)
 result=dict(status='ten_snapshot_axi_models_exact_storage_edits_checked_all_30_transactions_still_pending',models=models,edit_counts=counts,files=files,limits=['Static textual scope audit only; full cycle/output/PC oracle replay remains required','No snapshot DUT/TV execution occurred; all original30 full-depth transactions and original C postcheck remain required'])
 with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
 print(result['status'],counts)
if __name__=='__main__':main()
