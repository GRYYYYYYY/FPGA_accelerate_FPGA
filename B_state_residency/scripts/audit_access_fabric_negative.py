from pathlib import Path
import hashlib,json,re,subprocess,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/access_fabric_synthesis_20261024';receipt=json.loads((out/'completion_receipt.json').read_text());log=(out/'full_synthesis.log').read_text();capture=json.loads((out/'log_capture.json').read_text());assert receipt['exit_code']==0 and sha(out/'full_synthesis.log')==capture['sha256']and 'ACCESS_FABRIC_SYNTH_DONE'in log
 rpt=(out/'combinational_loops.rpt').read_text();timing=(out/'check_timing.rpt').read_text();assert re.search(r'Violations found:\s*1\b',rpt)and '4 LUT cells form a combinatorial loop'in rpt and 'checking loops (1)'in timing
 gate=ROOT/'scripts/audit_access_fabric_synthesis.py';(out/'failed_gate_auditor.py').write_bytes(gate.read_bytes())
 with (out/'failed_gate_attempt.log').open('w')as f:r=subprocess.run([sys.executable,str(gate)],stdout=f,stderr=subprocess.STDOUT)
 assert r.returncode!=0
 (out/'negative_auditor.py').write_bytes(Path(__file__).read_bytes());result={'status':'failed','evidence_verified':True,'tool_exit_code':receipt['exit_code'],'elapsed_s':receipt['elapsed_seconds'],'combinational_loop_violations':1,'loop_lut_cells':4,'cause':'a_busy includes fault and gates shared label response ownership; dispatcher unexpected-response fault feeds a_busy.','failed_gate_exit_code':r.returncode,'artifacts':{str(p.relative_to(out)):sha(p)for p in out.rglob('*')if p.is_file()and p.name!='negative_audit.json'}};(out/'negative_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items()if k!='artifacts'},indent=2))
if __name__=='__main__':main()
