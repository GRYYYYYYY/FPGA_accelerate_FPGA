"""Bind address64/sparse-record composition to both audited source lineages."""
from pathlib import Path
import hashlib,json,re
from make_sparse_records_address64_tb import render
ROOT=Path(__file__).resolve().parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def term(t,prefix):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search('^'+prefix+r' (.+)$',t,re.M)[1])}
def main():
 out=ROOT/'results/sparse_records_address64_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 base=ROOT/'results/sparse_records_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert sha(base/'manifest.json')==m['native_manifest_sha256'] and sha(base/'source_bound_audit.json')==m['native_audit_sha256']
 assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 old=ROOT/'results/address64_trace_pilot_20261024';om=json.loads((old/'manifest.json').read_text());assert om['status']=='passed' and sha(old/'manifest.json')==m['address_manifest_sha256']
 expected={k:v for k,v in bm['cases']['candidate']['sources'].items() if not k.startswith('tb_')}
 address={Path(k).name:v for k,v in om['cases']['pilot']['sources'].items() if Path(k).name in ('backing_base_config.sv','memory_scratch_endpoint_address64.sv')};assert len(address)==2
 expected|=address;generated=render();rows={}
 assert sha(ROOT/'hardware/scripts/run_sparse_records_address64.py')==m['runner_sha256']
 assert sha(ROOT/'hardware/scripts/make_sparse_records_address64_tb.py')==m['generator_sha256']
 vector=ROOT/'results/small_checkpoint_vectors_pilot_20261023';vm=json.loads((vector/'manifest.json').read_text());assert vm['status']=='passed'
 for filename in ['actual.txt','pages.hex']:assert sha(vector/filename)==vm['artifacts'][filename]
 for case,tb,top,ref in [('stalls','tb_sparse_records_address64_stalls.sv','tb_sparse_records_address64_stalls','stalls'),('pilot','tb_sparse_records_address64_pilot.sv','tb_sparse_records_address64_small','candidate')]:
  d=out/case;r=m['cases'][case];sources=expected|{tb:hashlib.sha256(generated[tb].encode()).hexdigest()}
  assert r['status']=='passed' and r['sources']==sources
  for filename,digest in sources.items():assert sha(d/'sources'/filename)==digest
  commands=r['commands'];assert [s['stage'] for s in commands]==['compile','elaborate','simulate'] and all(s['exit_code']==0 for s in commands)
  assert set(Path(x) for x in commands[0]['argv'] if x.endswith('.sv'))=={d/'sources'/name for name in sources}
  assert commands[1]['argv'][1]==top
  if case=='pilot':assert commands[2]['argv'][6:]==bm['cases']['candidate']['commands'][-1]['argv'][6:]
  log=(d/'simulate.log').read_text();original=(base/ref/'simulate.log').read_text()
  assert sha(d/'simulate.log')==r['log_sha256'] and 'Fatal:' not in log and '$finish' in log
  carry=re.search(r'SPARSE_RECORDS_ADDRESS64_PASS base=00000012fffff000 aw_carries=(\d+) ar_carries=(\d+)',log);assert carry
  observed=dict(zip(['aw','ar'],map(int,carry.groups())));assert observed==r['carry_counts'] and all(observed.values())
  retry=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1]);assert retry==r['finish_retries']
  assert r['end_ns']==int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
  for direction in ['WB','RF']:
   fields=['exports','omitted','masks'] if direction=='WB' else ['beats','omitted','masks']
   match=re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),log);assert match
   assert r[direction.lower()+'_counts']==dict(zip(fields,map(int,match.groups())))==bm['cases'][ref][direction.lower()+'_counts']
  if case=='stalls':
   assert 'SMALL_STALLS_PASS cases=8 blocked_cycles=800' in log
   c=term(log,'SMALL_32SLOTS_PASS');assert c==r['counts']
   assert all(c[k]==v for k,v in {'pages':32,'fields':5,'checkpoints':8,'transfers':288,'checks':1778+retry,'tag_wraps':4}.items())
  else:
   for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
    strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
    assert strip(log)==strip(original)
   counts,previous=term(log,'TEST_PASS memory_endpoint'),term(original,'TEST_PASS memory_endpoint');assert counts==r['counts'] and counts.keys()==previous.keys()
   assert counts['checks']==75194+retry and all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
   equality=all(re.findall('^'+p+r' (.+)$',log,re.M)==re.findall('^'+p+r' (.+)$',original,re.M) for p in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint'])
   assert equality==r['exact_time_receipts_equal']
   assert equality and r['end_ns']==r['native_end_ns']==bm['cases']['candidate']['end_ns']
  rows[case]={'carry_counts':observed,'end_ns':r['end_ns'],'finish_retries':retry,'log_sha256':r['log_sha256']}
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':rows,'pilot_queries':19,'pilot_transfers':5183,'pilot_time_equal_native':True,'address_sources_unchanged':address,'scope':'Composition at high64bit base with carry and gated configuration; selected actual pilot and32slot test. No address64 full38, XRT, allocation, platform or board proof.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
