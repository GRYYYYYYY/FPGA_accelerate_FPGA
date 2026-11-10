"""Check all pending first-touch phases and latched fault across coordinated cold reset."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=Path(sys.argv[1]).resolve();hls=Path(sys.argv[2]).resolve()
    gate=json.loads((hls/'source_bound_audit.json').read_text());assert gate['status']=='passed'
    out.mkdir();src=out/'sources';src.mkdir()
    m={'status':'running','sources':{},'commands':[],'hls_gate':{'path':str(hls/'source_bound_audit.json'),'sha256':sha(hls/'source_bound_audit.json')},'runner_sha256':sha(Path(__file__))}
    def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    paths=[]
    for name,digest in gate['cases']['32']['generated_rtl_artifacts'].items():
        p=hls/'gen32/children_step/solution1/syn/verilog'/name;assert sha(p)==digest
        if p.suffix=='.v':paths.append(p)
    paths += [ROOT/'hardware/variants/children_reset_check/tb_children_reset.sv']
    for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
    (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 100us\nquit\n');save()
    cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths]]),('elaborate',[BIN/'xelab','tb_children_reset','-s','reset_test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','reset_test','--tclbatch','run.tcl','--log','simulate.log'])]
    for stage,args in cmds:
        argv=list(map(str,args))
        with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
        m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0
    log=(out/'simulate.log').read_text()
    assert 'CHILDREN_RESET_PASS phases=8 resets=11 calls=63 fault_recovery=1 high_boundary=1' in log and 'Fatal:' not in log and '$finish called' in log
    m.update(status='passed',artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save();print(m['status'])
if __name__=='__main__':main()
