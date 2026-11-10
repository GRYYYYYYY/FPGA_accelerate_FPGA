"""Sparse WB/RF plus unchanged address64, with high-base carry and real pilot."""
from pathlib import Path
import hashlib,json,subprocess,os,re
from make_sparse_records_address64_tb import render
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def term(t,prefix):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search('^'+prefix+r' (.+)$',t,re.M)[1])}
def main():
 out=ROOT/'results/sparse_records_address64_20261024';out.mkdir()
 base=ROOT/'results/sparse_records_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 old=ROOT/'results/address64_trace_pilot_20261024';om=json.loads((old/'manifest.json').read_text());assert om['status']=='passed'
 originals=sorted(p for p in (base/'candidate/sources').glob('*.sv') if not p.name.startswith('tb_'))
 for p in originals:assert sha(p)==bm['cases']['candidate']['sources'][p.name]
 expected={Path(k).name:v for k,v in om['cases']['pilot']['sources'].items()}
 address=[old/'pilot/sources'/name for name in ['backing_base_config.sv','memory_scratch_endpoint_address64.sv']]
 for p in address:assert sha(p)==expected[p.name]
 tbs=render()
 for name,s in tbs.items():assert (ROOT/'hardware/tb'/name).read_text()==s
 m={'status':'running','pid':os.getpid(),'native_manifest_sha256':sha(base/'manifest.json'),'native_audit_sha256':sha(base/'source_bound_audit.json'),'address_manifest_sha256':sha(old/'manifest.json'),'cases':{},'runner_sha256':sha(Path(__file__)),'generator_sha256':sha(ROOT/'hardware/scripts/make_sparse_records_address64_tb.py')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for case,tb,top,marker,reference in [('stalls','tb_sparse_records_address64_stalls.sv','tb_sparse_records_address64_stalls','SMALL_STALLS_PASS cases=8 blocked_cycles=800','stalls'),('pilot','tb_sparse_records_address64_pilot.sv','tb_sparse_records_address64_small','TEST_PASS memory_endpoint','candidate')]:
   d=out/case;d.mkdir();src=d/'sources';src.mkdir();paths=originals+address+[ROOT/'hardware/tb'/tb]
   row={'status':'running','sources':{},'commands':[]};m['cases'][case]=row
   for p in paths:(src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
   (d/'run.tcl').write_text('run all\nquit\n')
   sim=[str(BIN/'xsim'),'address64','--tclbatch','run.tcl','--log','simulate.log']
   if case=='pilot':sim+=bm['cases']['candidate']['commands'][-1]['argv'][6:]
   cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),top,'-s','address64','--debug','typical','--mt','2']),('simulate',sim)]
   for stage,argv in cmds:
    with (d/f'{stage}.stdout.log').open('w') as f:
     proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(case,stage)
   log=(d/'simulate.log').read_text();assert marker in log and 'Fatal:' not in log and '$finish' in log
   carry=re.search(r'SPARSE_RECORDS_ADDRESS64_PASS base=00000012fffff000 aw_carries=(\d+) ar_carries=(\d+)',log);assert carry and all(int(x)>0 for x in carry.groups())
   row['carry_counts']=dict(zip(['aw','ar'],map(int,carry.groups())))
   row['end_ns']=int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
   retries=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1]);row['finish_retries']=retries
   original=(base/reference/'simulate.log').read_text()
   for direction in ['WB','RF']:
    fields=['exports','omitted','masks'] if direction=='WB' else ['beats','omitted','masks']
    extract=lambda t:dict(zip(fields,map(int,re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),t).groups())))
    row[direction.lower()+'_counts']=extract(log);assert extract(log)==extract(original)
   if case=='pilot':
    for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
     strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
     assert strip(log)==strip(original)
    c,oldc=term(log,'TEST_PASS memory_endpoint'),term(original,'TEST_PASS memory_endpoint');assert c.keys()==oldc.keys()
    assert c['checks']==75194+retries and all(c[k]==v for k,v in oldc.items() if k not in ('checks','gap_cycles','host_stalls'))
    row['exact_time_receipts_equal']=all(re.findall('^'+p+r' (.+)$',log,re.M)==re.findall('^'+p+r' (.+)$',original,re.M) for p in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint'])
    row['counts']=c;row['native_end_ns']=bm['cases']['candidate']['end_ns']
   else:
    c=term(log,'SMALL_32SLOTS_PASS');assert c['pages']==32 and c['fields']==5 and c['checkpoints']==8 and c['transfers']==288 and c['checks']==1778+retries and c['tag_wraps']==4;row['counts']=c
   row.update(status='passed',log_sha256=sha(d/'simulate.log'));save();print(case,'passed',row['end_ns'],row['carry_counts'],flush=True)
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
