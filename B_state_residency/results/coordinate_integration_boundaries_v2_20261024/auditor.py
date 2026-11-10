from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/coordinate_integration_boundaries_v2_20261024';old=ROOT/'results/coordinate_integration_boundaries_20261024';dep=ROOT/'results/coordinate_service_v2_20261024'
 m=json.loads((out/'manifest.json').read_text());om=json.loads((old/'manifest.json').read_text());dm=json.loads((dep/'manifest.json').read_text())
 assert m['status']=='passed'and m['functional_manifest_sha256']==sha(dep/'manifest.json')and all(c['exit_code']==0 for c in m['commands'])
 for n,s in m['sources'].items():
  assert sha(out/'sources'/n)==s['sha256']
  if n in dm['sources']:assert s['sha256']==dm['sources'][n]['sha256']==om['sources'][n]['sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 log=(out/'simulate.log').read_text();assert m['result']in log and 'Fatal:'not in log and 'Error:'not in log and '$finish called'in log
 cnt={k:int(v)for k,v in re.findall(r'(\w+)=(\d+)',m['result'])};assert cnt['faults']==cnt['recoveries']==7
 # Show the only testbench edit: sample recovery data after the NBA delta.
 before=(old/'sources/tb_coordinate_integration.sv').read_text();after=(out/'sources/tb_coordinate_integration.sv').read_text()
 assert before.replace('wait(rsp_valid);if(rsp_y!=70)','wait(rsp_valid);@(negedge clk);if(rsp_y!=70)')==after
 counts={}
 for kind in ['graph','table','label']:
  lines=[s.split()for s in (out/(kind+'_axi.txt')).read_text().splitlines()]
  counts[kind+'_r_errors']=sum(r[0]=='R'and int(r[3])!=0 for r in lines)
  counts[kind+'_b_errors']=sum(r[0]=='B'and int(r[1])!=0 for r in lines)
 assert counts['graph_r_errors']==counts['table_r_errors']==1 and counts['label_r_errors']>=1 and counts['label_b_errors']==1
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':cnt,'actual_axi_faults':counts,'scope':'Actual graph/table/paged-label integration, AXI R/B errors, invalid prev, abort and late abort, seven coordinated cold-reset recoveries. SLOTS1; reset also cancels memory model transactions, not arbitrary physical AXI reset.'};(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
