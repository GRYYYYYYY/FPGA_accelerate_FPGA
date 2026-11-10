from pathlib import Path
import hashlib,json,difflib
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 a=ROOT/'results/access_fabric_v2_20261024';b=ROOT/'results/access_fabric_v3_20261024';am=json.loads((a/'manifest.json').read_text());bm=json.loads((b/'manifest.json').read_text());assert am['status']==bm['status']=='passed'
 for n in bm['sources']:
  if not n.endswith(('.sv','.v')):continue
  x=(a/'sources'/n).read_text();y=(b/'sources'/n).read_text()
  if n=='fabric/access_fabric.sv':
   expected=x.replace('reg host_pending;','reg host_pending,access_pending;').replace('!a_busy','!access_pending').replace('assign busy=a_busy','assign busy=access_pending').replace('if(rst)host_pending<=0;','if(rst)begin host_pending<=0;access_pending<=0;end').replace('  else begin\n','  else begin\n   if(req_valid&&req_ready)access_pending<=1;\n   if(rsp_valid&&rsp_ready)access_pending<=0;\n',1).replace('=a_busy?','=access_pending?').replace('&&a_busy','&&access_pending')
   assert expected==y
   (b/'ownership_fix.diff').write_text(''.join(difflib.unified_diff(x.splitlines(True),y.splitlines(True),fromfile='v2/access_fabric.sv',tofile='v3/access_fabric.sv')))
  else:assert x==y,n
 for case in bm['cases']:
  assert am['cases'][case]['result']==bm['cases'][case]['result']
  for name in ['observed.txt','graph_axi.txt','table_axi.txt','label_axi.txt','labels.bin']:assert sha(a/case/name)==sha(b/case/name),(case,name)
 neg=ROOT/'results/access_fabric_synthesis_20261024/negative_audit.json';nm=json.loads(neg.read_text());assert nm['status']=='failed'and nm['evidence_verified']and nm['combinational_loop_violations']==1
 (b/'ownership_auditor.py').write_bytes(Path(__file__).read_bytes());r={'status':'passed','old_manifest_sha256':sha(a/'manifest.json'),'new_manifest_sha256':sha(b/'manifest.json'),'negative_audit_sha256':sha(neg),'auditor_sha256':sha(Path(__file__)),'design_delta':'Register decision ownership at request acceptance and final response retirement; use it for label routing and external-host exclusion.','all_normal_results_cycles_and_memory_traces_identical':True,'physical_loop_gate':'Must pass new full synthesis; this comparison alone is not structural proof.'};(b/'ownership_change_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
