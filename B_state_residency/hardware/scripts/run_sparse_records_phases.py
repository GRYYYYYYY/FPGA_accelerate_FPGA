"""Paired phase-sensitivity ablation; fixed host pacing, unmodified RTL/data."""
from pathlib import Path
import hashlib,json,subprocess,os,re
from make_sparse_records_phase_tb import render,PHASES
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def term(t):return {k:int(v) for k,v in re.findall(r'(\w+)=(\d+)',re.search(r'^TEST_PASS memory_endpoint (.+)$',t,re.M)[1])}
def main():
 out=ROOT/'results/sparse_records_phases_20261024';out.mkdir()
 base=ROOT/'results/sparse_records_20261024';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
 assert json.loads((base/'source_bound_audit.json').read_text())['status']=='passed'
 tb=ROOT/'hardware/tb/tb_sparse_records_phases.sv';assert tb.read_text()==render()
 m={'status':'running','pid':os.getpid(),'pilot_audit_sha256':sha(base/'source_bound_audit.json'),'cases':{},'runner_sha256':sha(Path(__file__)),'tb_generator_sha256':sha(ROOT/'hardware/scripts/make_sparse_records_phase_tb.py')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 save()
 try:
  for phase in PHASES:
   for label in ('control','candidate'):
    old=(base/label/'simulate.log').read_text();name=f'{label}{phase}';d=out/name;d.mkdir();src=d/'sources';src.mkdir()
    paths=sorted(p for p in (base/label/'sources').glob('*.sv') if not p.name.startswith('tb_'))+[tb]
    row={'status':'running','phase':phase,'label':label,'commands':[],'sources':{}};m['cases'][name]=row
    for p in paths:
     if p!=tb:assert sha(p)==bm['cases'][label]['sources'][p.name]
     (src/p.name).write_bytes(p.read_bytes());row['sources'][p.name]=sha(p)
    (d/'run.tcl').write_text('run all\nquit\n')
    cmds=[('compile',[str(BIN/'xvlog'),'--sv',*[str(src/p.name) for p in paths]]),('elaborate',[str(BIN/'xelab'),f'tb_sparse_records_phase_{label}{phase}','-s','phase','--debug','typical','--mt','2']),('simulate',[str(BIN/'xsim'),'phase','--tclbatch','run.tcl','--log','simulate.log']+bm['cases'][label]['commands'][-1]['argv'][6:])]
    for stage,argv in cmds:
     with (d/f'{stage}.stdout.log').open('w') as f:
      proc=subprocess.Popen(argv,cwd=d,stdout=f,stderr=subprocess.STDOUT);step={'stage':stage,'argv':argv,'pid':proc.pid};row['commands'].append(step);save();step['exit_code']=proc.wait();save();assert step['exit_code']==0,(name,stage)
    log=(d/'simulate.log').read_text();assert 'TEST_PASS memory_endpoint' in log and 'Fatal:' not in log and '$finish' in log
    for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE']:
     strip=lambda t:[re.sub(r' ?time_ps=\d+','',x) for x in re.findall('^'+prefix+r' (.+)$',t,re.M)]
     assert strip(log)==strip(old)
    counts,previous=term(log),term(old);retry=int(re.search(r'FINISH_RETRY_COUNTS retries=(\d+)',log)[1])
    assert counts['checks']==75194+retry and counts.keys()==previous.keys()
    assert all(counts[k]==v for k,v in previous.items() if k not in ('checks','gap_cycles','host_stalls'))
    for direction,fields in [('WB',['exports','omitted','masks']),('RF',['beats','omitted','masks'])]:
     match=re.search('SPARSE_'+direction+'_COUNTS '+r' '.join(k+r'=(\d+)' for k in fields),log);assert match
     row[direction.lower()+'_counts']=dict(zip(fields,map(int,match.groups())));assert row[direction.lower()+'_counts']==bm['cases'][label][direction.lower()+'_counts']
    end_ns=int(re.search(r'\$finish called at time : (\d+) ns',log)[1])
    if phase==0:
     assert end_ns==bm['cases'][label]['end_ns']
     for prefix in ['STREAM_QUERY_DONE','STREAM_CHECKPOINT_DONE','TEST_PASS memory_endpoint','FINISH_RETRY_COUNTS']:
      assert re.findall('^'+prefix+r' (.+)$',log,re.M)==re.findall('^'+prefix+r' (.+)$',old,re.M)
    row.update(status='passed',log_sha256=sha(d/'simulate.log'),counts=counts,finish_retries=retry,end_ns=end_ns);save();print(name,'passed',end_ns,flush=True)
  m['phase_comparisons']=[{'phase':phase,'control_end_ns':m['cases'][f'control{phase}']['end_ns'],'candidate_end_ns':m['cases'][f'candidate{phase}']['end_ns'],'incremental_reduction_fraction':1-m['cases'][f'candidate{phase}']['end_ns']/m['cases'][f'control{phase}']['end_ns']} for phase in PHASES]
  m['status']='passed';save()
 except Exception as e:m.update(status='failed',error=repr(e));save();raise
if __name__=='__main__':main()
