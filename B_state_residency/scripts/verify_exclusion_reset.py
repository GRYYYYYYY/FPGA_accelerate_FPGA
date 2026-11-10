"""Replay exactly the same cold-reset contract against old and state-reset HLS RTL."""
from pathlib import Path
import hashlib,json,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=Path(sys.argv[1]).resolve();hls=Path(sys.argv[2]).resolve();negative=len(sys.argv)>3 and sys.argv[3]=='--negative'
    gate=json.loads((hls/'source_bound_audit.json').read_text());assert gate['status']=='passed'
    out.mkdir();src=out/'sources';src.mkdir()
    m={'status':'running','negative':negative,'sources':{},'commands':[],'hls_gate':{'path':str(hls/'source_bound_audit.json'),'sha256':sha(hls/'source_bound_audit.json')},'runner_sha256':sha(Path(__file__))}
    def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
    paths=[]
    for name,digest in gate['cases']['32']['generated_rtl_artifacts'].items():
        p=hls/'gen32/exclusion_step/solution1/syn/verilog'/name;assert sha(p)==digest
        if p.suffix=='.v':paths.append(p)
    paths += [ROOT/'hardware/variants/exclusion_engine_v2/exclusion_hls_call.sv',ROOT/'hardware/variants/exclusion_reset_check/tb_reset_generation.sv']
    for p in paths:(src/p.name).write_bytes(p.read_bytes());m['sources'][p.name]={'path':str(p),'sha256':sha(p)}
    (out/'runner.py').write_bytes(Path(__file__).read_bytes());(out/'run.tcl').write_text('run 100us\nquit\n');save()
    cmds=[('compile',[BIN/'xvlog','--sv',*[src/p.name for p in paths]]),('elaborate',[BIN/'xelab','tb_reset_generation','-s','reset_test','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','reset_test','--tclbatch','run.tcl','--log','simulate.log'])]
    for stage,args in cmds:
        argv=list(map(str,args))
        with (out/(stage+'.stdout.log')).open('w') as f:r=subprocess.run(argv,cwd=out,stdout=f,stderr=subprocess.STDOUT,timeout=120)
        m['commands'].append({'stage':stage,'argv':argv,'exit_code':r.returncode});save();assert r.returncode==0
    log=(out/'simulate.log').read_text()
    if negative:
        assert 'RESET_OBSERVATION call=1 resets=2 status=0 generation=2 phase=0' in log
        assert 'Fatal: RESET_CONTRACT_FAIL expected_generation=1 actual_generation=2 expected_phase=0 actual_phase=0' in log
        assert 'RESET_CONTRACT_PASS' not in log
    else:assert 'RESET_CONTRACT_PASS calls=4 resets=3' in log and 'Fatal:' not in log
    m.update(status='expected_failure_verified' if negative else 'passed',artifacts={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')});save();print(m['status'])
if __name__=='__main__':main()
