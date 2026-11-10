"""Actual generated HLS -> native label endpoint; independent original-function vectors."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def main():
    out=Path(sys.argv[1]).resolve();out.mkdir();src=out/'sources';src.mkdir()
    engine=ROOT/'hardware/variants/exclusion_engine_v3'
    base=ROOT/'results/sparse_records_20261024';bm=read(base/'manifest.json');assert bm['status']=='passed'
    hls=ROOT/'results/exclusion_hls_reset_20261024';ha=read(hls/'source_bound_audit.json');assert ha['status']=='passed'
    label=ROOT/'results/exclusion_label_adapter_v2_20261024';la=read(label/'source_bound_audit.json');assert la['status']=='passed'
    assert la['manifest_sha256']==sha(label/'manifest.json') and ha['manifest_sha256']==sha(hls/'manifest.json')
    m={'status':'running','pid':os.getpid(),'sources':{},'gates':{},'cases':{},'commands':[],
       'scope':'Actual HLS edge exclusion integrated with resident native label endpoint; no automatic pager, full routing, AXI transfer, platform or timing proof.'}
    def save():
        tmp=out/'manifest.tmp';tmp.write_text(json.dumps(m,indent=2)+'\n');tmp.replace(out/'manifest.json')
    def freeze(p,dest):
        q=src/dest;q.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(p,q)
        m['sources'][dest]={'path':str(p),'sha256':sha(p)};return q
    backend=[]
    for name,digest in bm['cases']['candidate']['sources'].items():
        if name.startswith('tb_'):continue
        p=base/'candidate/sources'/name;assert sha(p)==digest;backend.append(freeze(p,'backend/'+name))
    p=label/'sources/exclusion_label_adapter.sv'
    assert sha(p)==read(label/'manifest.json')['sources'][p.name]['sha256']
    adapter=freeze(p,'adapter/'+p.name)
    generated={}
    for bits in (32,3):
        generated[bits]=[]
        for name,digest in ha['cases'][str(bits)]['generated_rtl_artifacts'].items():
            p=hls/f'gen{bits}/exclusion_step/solution1/syn/verilog'/name;assert sha(p)==digest
            q=freeze(p,f'hls{bits}/'+name)
            if p.suffix=='.v':generated[bits].append(q)
    for p in sorted(engine.iterdir()):
        if p.is_file():freeze(p,'engine/'+p.name)
    original=ROOT/'results/frontier_real_20261024/original_trace.cpp'
    text=original.read_text();a=text.index('    bool isPartOfExistingRoute(int parent, int child) const {');b=text.index('    // ----------------------------------------------------------------- getChildren',a)
    oracle=hls/'rearchitect/v1/tb/original_functions.inc';assert oracle.read_text()==text[a:b]
    freeze(oracle,'engine/original_functions.inc')
    for p in [base/'manifest.json',base/'source_bound_audit.json',hls/'source_bound_audit.json',label/'source_bound_audit.json',original]:
        m['gates'][str(p)]=sha(p)
    freeze(Path(__file__),'runner.py');save()
    def run(stage,argv,d,rows):
        argv=list(map(str,argv));row={'stage':stage,'argv':argv};rows.append(row);save();t=time.monotonic()
        with (d/(stage+'.stdout.log')).open('w') as log:
            proc=subprocess.Popen(argv,cwd=d,stdout=log,stderr=subprocess.STDOUT);row['pid']=proc.pid;save()
            row['exit_code']=proc.wait(timeout=900);row['elapsed_s']=time.monotonic()-t;save()
        assert row['exit_code']==0,(stage,d)
    try:
        run('oracle_build',['g++','-std=c++17','-O2',src/'engine/make_vectors.cpp','-o',out/'make_vectors'],out,m['commands'])
        run('oracle_run',[out/'make_vectors',out/'vectors.txt'],out,m['commands'])
        m['oracle']={'binary_sha256':sha(out/'make_vectors'),'vectors_sha256':sha(out/'vectors.txt'),'lines':sum(1 for _ in (out/'vectors.txt').open()),'log_sha256':sha(out/'oracle_run.stdout.log')}
        assert m['oracle']['lines']==27680;save()
        rtl=[src/'engine'/name for name in ['exclusion_hls_call.sv','exclusion_edge_controller.sv','exclusion_edge_engine.sv']]
        for case in ('collector','engine32','engine3'):
            d=out/case;d.mkdir();cm=m['cases'][case]={'status':'running','commands':[]};save()
            if case=='collector':paths=[rtl[0],src/'engine/tb_exclusion_hls_call.sv'];top='tb_exclusion_hls_call';defines=[]
            else:
                bits=32 if case=='engine32' else 3;paths=backend+[adapter]+generated[bits]+rtl+[src/'engine/tb_exclusion_edge_engine.sv'];top='tb_exclusion_edge_engine'
                defines=[] if bits==32 else ['--define','HLS_GEN3']
            (d/'run.tcl').write_text('run 100ms\nquit\n')
            run('compile',[BIN/'xvlog','--sv']+defines+paths,d,cm['commands'])
            run('elaborate',[BIN/'xelab',top,'-s','engine','--debug','typical','--mt','2'],d,cm['commands'])
            argv=[BIN/'xsim','engine','--tclbatch','run.tcl','--log','simulate.log']
            if case=='engine32':argv+=['--testplusarg','fixture='+str(out/'vectors.txt')]
            run('simulate',argv,d,cm['commands'])
            log=(d/'simulate.log').read_text();marker={'collector':'HLS_CALL_PASS ','engine32':'EDGE_ENGINE_PASS ','engine3':'EDGE_GEN3_PASS '}[case]
            passed=[s for s in log.splitlines() if s.startswith(marker)]
            assert len(passed)==1 and 'Fatal:' not in log and 'Error:' not in log and '$finish called' in log,(case,log[-1800:])
            cm.update(status='passed',result=passed[0],artifacts={p.name:sha(p) for p in d.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save();print(case,passed[0],flush=True)
        for name,spec in m['sources'].items():assert sha(src/name)==spec['sha256']==sha(Path(spec['path']))
        for path,digest in m['gates'].items():assert sha(Path(path))==digest
        m['status']='passed';save()
    except Exception as exc:m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
