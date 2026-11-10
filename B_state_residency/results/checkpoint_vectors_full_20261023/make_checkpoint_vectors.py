"""Full actual-value oracle with retained-backing checkpoint projection."""
from pathlib import Path
import argparse,json,os,sys
from collections import Counter
from make_streaming_memory_vectors import Projection,transformed_oracle
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'scripts'))
from audit_large_query_demand import sha

def oracle_text(source):
 text=transformed_oracle(source)
 before='        elif op==FINISH:'
 after='''        elif op==12:
            if self.active is None or len(self.used_queries)!=1:status=BAD
            elif self.frames or self.draining:status=BUSY
            else:self.last_gen.clear();self.issued.clear()
        elif op==FINISH:'''
 assert text.count(before)==1;text=text.replace(before,after)
 before="                page,off=divmod(node,64)"
 after='''                if o.limit-len(o.issued)<6 or max(generations)>=65534:
                    for resident_page in list(slots):evict(resident_page)
                    o.emit(12,q=q,price=p,expect=OK)
                    generations=[0]*4;counts['checkpoints']+=1
                page,off=divmod(node,64)'''
 assert text.count(before)==1;text=text.replace(before,after)
 # Progress and per-query receipts are diagnostics; state transitions unchanged.
 before="            o.emit(FENCE,expect=OK);o.emit(FINISH,peer=1,empty=1,expect=OK)"
 after=before+"\n            o.stream.query_done(row['attempt'],dict(counts))"
 assert text.count(before)==1;text=text.replace(before,after)
 return text

class CheckpointProjection(Projection):
 def __init__(self,host,pages,callback):super().__init__(host,pages);self.callback=callback
 def query_done(self,attempt,counts):
  self.callback(attempt,counts,dict(self.counts),self.transfers)

def main():
 parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);parser.add_argument('--small',action='store_true');args=parser.parse_args()
 out=args.output.resolve();out.mkdir()
 plan_path=ROOT/'results/retained_checkpoint_plan_20261023/manifest.json'
 assert sha(plan_path)=='158bf20f132d9f032883eb425aaca793ff1936777ad8b91c61cbcfc389f46dc4'
 plan=json.loads(plan_path.read_text());chosen=[q for q in plan['queries'] if not args.small or q['counts']['accesses']<=100000];selected=[q['attempt'] for q in chosen]
 capture=ROOT/'results/real_field_values_20261023T024250Z'
 for name,digest in plan['inputs'].items():assert sha(Path(name))==digest
 source=ROOT/'hardware/scripts/make_controller_vectors.py';parent=ROOT/'results/rtl_page_controller_20261023/vectors/vectors_manifest.json'
 assert sha(source)==json.loads(parent.read_text())['files'][str(source)]
 text=oracle_text(source);(out/'oracle_transformed.py').write_text(text)
 ns={'__name__':'checkpoint_value_oracle','__file__':str(source)};exec(compile(text,str(out/'oracle_transformed.py'),'exec'),ns)
 m={'status':'running','pid':os.getpid(),'selected_attempts':selected,'queries_completed':[],
    'inputs':{str(p):sha(p) for p in [plan_path,source,parent,*map(Path,plan['inputs'])]},
    'sources':{str(p):sha(p) for p in [Path(__file__).resolve(),ROOT/'hardware/scripts/make_streaming_memory_vectors.py']},'rtl_executed':False,'board_performance':None}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def progress(attempt,counts,public,transfers):
  m['queries_completed'].append({'attempt':attempt,'cumulative_field_counts':counts,'cumulative_public_counts':public,'cumulative_transfers':transfers});save();print(attempt,'generated',counts['field_accesses'],flush=True)
 save()
 try:
  with (out/'actual.txt').open('w') as host,(out/'pages.hex').open('w') as pages:
   projection=CheckpointProjection(host,pages,progress);oracle=ns['Oracle'](projection,tx_bits=16)
   result=ns['real'](oracle,capture,set(selected));assert projection.pending is None
  expected=Counter()
  for q in chosen:
   for key,value in q['counts'].items():
    if not key.startswith('max_'):expected[key]+=value
  assert result['field_accesses']==expected['accesses'] and result['writebacks']==expected['writebacks'] and result['refills']==expected['refills']
  assert result.get('checkpoints',0)==expected['checkpoints']
  assert projection.counts['1']==expected['bindings'] and projection.counts['4']==expected['releases']
  assert projection.counts['2']==expected['reads'] and projection.counts['3']==expected['writes']
  assert projection.counts['12']==expected['checkpoints'] and projection.transfers==expected['writebacks']+expected['refills']
  assert projection.queries==len(selected)==len(m['queries_completed'])
  if args.small:
   for name in ['actual.txt','pages.hex']:assert sha(out/name)==sha(ROOT/'results/rtl_memory_endpoint_20261023/vectors'/name)
  m.update(status='passed',queries=projection.queries,public_commands=sum(projection.counts.values()),transfers=projection.transfers,
    counts=dict(projection.counts),peak_reserved_owners=projection.peak,maximum_generation=projection.max_generation,maximum_transaction=projection.max_transaction,
    field_replay=result,oracle_commands=oracle.count,small_bitwise_equivalence=args.small,
    artifacts={name:sha(out/name) for name in ['actual.txt','pages.hex','oracle_transformed.py']})
  for name,digest in m['sources'].items():assert sha(Path(name))==digest
  save();(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());(out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
  print('PASS',m['public_commands'],m['transfers'],dict(projection.counts),flush=True)
 except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
