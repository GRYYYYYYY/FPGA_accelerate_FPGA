from pathlib import Path
import hashlib,json,runpy,subprocess
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_cost_exact_cpp_v2_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,d in m['sources'].items():assert sha(out/'sources'/n)==d
 for n,d in m['artifacts'].items():assert sha(out/n)==d
 assert sha(ROOT/'scripts/verify_search_cost_exact_cpp_v2.py')==m['runner_sha256']
 assert sha(ROOT/'results/cost_capture_real_20261024/source_bound_audit.json')==m['real_gate_sha256']
 compare=runpy.run_path(str(ROOT/'scripts/audit_search_cost_native.py'))['compare']
 groups,words,_=compare(out/'vectors.txt',out/'observed.txt');assert words==0 and groups[4]['cases']==16224
 assert 'SOFTFP_PRIMITIVES_PASS checks=5001280 both_nan_payload_policy_cases=0 inputs=1000256' in (out/'primitives.log').read_text()
 assert all(c['exit_code']==0 for c in m['commands'])
 asm=subprocess.check_output(['objdump','-d','-C','-Mintel',str(ROOT/'results/search_cost_native_hls_20261024/make_vectors')],text=True)
 assert 'addss  xmm0,xmm1' in asm
 (out/'oracle_disassembly.txt').write_text(asm)
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'oracle_disassembly_sha256':sha(out/'oracle_disassembly.txt'),'groups':groups,'primitive_checks':5001280,'undefined_behavior_sanitizer':True,'scope':'Software integer IEEE ops match 21000 frozen packets and 1,000,256 primitive input pairs. v1 retained one double-NaN payload mismatch; v2 operand priorities follow frozen SSE oracle. NaN payload portability across arbitrary compilers is not claimed. No RTL claim.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
