"""Frozen automatic paging + real HLS + actual native AXI endpoint regression."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,shutil,time
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
    base=ROOT/'results/exclusion_edge_engine_v4_20261024';bm=read(base/'manifest.json');gate=read(base/'source_bound_audit.json')
    assert bm['status']==gate['status']=='passed' and gate['manifest_sha256']==sha(base/'manifest.json')
    variant=ROOT/'hardware/variants/auto_pager_v1'
    m={'status':'running','pid':os.getpid(),'sources':{},'gates':{},'cases':{},'commands':[],
       'scope':'Automatic paging, actual state-reset HLS and native AXI RTL using independent label/byte models and original-function edge vectors; no board, full routing or speedup claim.'}
    def save():
        tmp=out/'manifest.tmp';tmp.write_text(json.dumps(m,indent=2)+'\n');tmp.replace(out/'manifest.json')
    def freeze(p,dest):
        q=src/dest;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q);m['sources'][dest]={'path':str(p),'sha256':sha(p)};return q
    rtl=[]
    for name,spec in bm['sources'].items():
        take=name.startswith(('backend/','adapter/','hls32/')) or name in ['engine/exclusion_hls_call.sv','engine/exclusion_edge_controller.sv','engine/exclusion_edge_engine.sv','engine/original_functions.inc']
        if take:
            p=base/'sources'/name;assert sha(p)==spec['sha256'];q=freeze(p,name)
            if q.suffix in ('.v','.sv'):rtl.append(q)
    for p in sorted(variant.iterdir()):
        if p.is_file():
            q=freeze(p,'pager/'+p.name)
            if q.suffix=='.sv':rtl.append(q)
    for p in [base/'manifest.json',base/'source_bound_audit.json',ROOT/'results/exclusion_hls_reset_20261024/source_bound_audit.json',ROOT/'results/sparse_records_20261024/source_bound_audit.json']:
        m['gates'][str(p)]=sha(p)
    freeze(Path(__file__),'runner.py');save()
    def run(stage,args,d,rows):
        argv=list(map(str,args));row={'stage':stage,'argv':argv};rows.append(row);save();t=time.monotonic()
        with (d/(stage+'.stdout.log')).open('w') as log:
            proc=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save();row['exit_code']=proc.wait();row['elapsed_s']=time.monotonic()-t;save()
        assert row['exit_code']==0,(stage,d)
    try:
        run('oracle_build',['g++','-std=c++17','-O2','-I'+str(src/'engine'),src/'pager/make_vectors.cpp','-o',out/'make_vectors'],out,m['commands'])
        run('oracle_run',[out/'make_vectors',out/'vectors.txt'],out,m['commands'])
        m['oracle']={'binary_sha256':sha(out/'make_vectors'),'vectors_sha256':sha(out/'vectors.txt'),'log_sha256':sha(out/'oracle_run.stdout.log'),'lines':sum(1 for _ in (out/'vectors.txt').open())};assert m['oracle']['lines']==27680;save()
        for case,define in [('budget32','PAGER_BUDGET'),('single','PAGER_SINGLE'),('fault','PAGER_FAULT'),('wrap16','PAGER_WRAP'),('production32',None)]:
            d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[],'define':define};save()
            (d/'run.tcl').write_text('run 1000ms\nquit\n')
            run('compile',[BIN/'xvlog','--sv']+(['--define',define] if define else [])+rtl,d,cm['commands'])
            run('elaborate',[BIN/'xelab','tb_paged_exclusion_engine','-s','pager','--debug','typical','--mt','2'],d,cm['commands'])
            run('simulate',[BIN/'xsim','pager','--tclbatch','run.tcl','--log','simulate.log','--testplusarg','fixture='+str(out/'vectors.txt')],d,cm['commands'])
            log=(d/'simulate.log').read_text();marker='PAGER_FAULT_PASS ' if case=='fault' else 'PAGER_WRAP_PASS ' if case=='wrap16' else 'PAGER_ENGINE_PASS '
            matches=[s for s in log.splitlines() if s.startswith(marker)]
            assert len(matches)==1 and 'Fatal:' not in log and 'Error:' not in log and '$finish called' in log,(case,log[-2200:])
            cm.update(status='passed',result=matches[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save();print(case,matches[0],flush=True)
        for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
        for path,digest in m['gates'].items():assert sha(Path(path))==digest
        m['status']='passed';save()
    except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
