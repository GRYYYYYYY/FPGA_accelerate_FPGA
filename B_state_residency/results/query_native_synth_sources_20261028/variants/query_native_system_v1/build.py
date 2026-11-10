"""Overlay the frozen query specialization on the audited native full system."""
from pathlib import Path
import json
import hashlib

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=HERE.parent/'query_native_exclusion_v1'
NAMES=['query_lifecycle.sv','query_residency_system.sv']
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def sources(fixed):
    m=json.loads((PARENT/'manifest.json').read_text())
    mode='fixed'if fixed else 'baseline';key='candidate'if fixed else 'baseline'
    result={}
    for n in NAMES:
        p=PARENT/mode/n;assert sha(p)==m['sources'][n][key];result[n]=p.read_text()
    return result
def evidence(ref):
    unit=ref.parent/'query_native_exclusion_unit_v1'
    a=json.loads((unit/'source_bound_audit.json').read_text())
    rp=ROOT/'results/query_native_exclusion_unit_v1_restore_20261025.json';r=json.loads(rp.read_text())
    assert a['status']==r['status']=='passed'and r['audit_byte_identical']
    assert a['manifest_sha256']==sha(unit/'manifest.json')and r['audit_sha256']==sha(unit/'source_bound_audit.json')
    assert len(a['cases'])==12
    proof=ROOT/'results/query_native_exclusion_20261027.json';pr=json.loads(proof.read_text())
    assert pr['status']=='source_bound_two_state_exclusion_not_rtl_validation'
    assert pr['analyzer_sha256']==sha(ROOT/'scripts/analyze_query_native_exclusion.py')
    matrix=ROOT/'results/native_retirement_matrix_sources_20261027/manifest.json'
    fm=json.loads(matrix.read_text());assert fm['status']=='frozen'and fm['cases']==8 and fm['case_file_comparisons']==216
    return dict(builder_sha256=sha(HERE/'build.py'),unit_audit_sha256=sha(unit/'source_bound_audit.json'),
                unit_restore_sha256=sha(rp),proof_sha256=sha(proof),matrix_freeze_sha256=sha(matrix),
                parent_manifest_sha256=sha(PARENT/'manifest.json'),
                candidate_sha256={n:sha(PARENT/'fixed'/n)for n in NAMES})
def monitored_tb(original):
    assert original.count('module tb_candidate_offer;')==1
    decl='''
 integer qi_cycles=0,qi_service_req=0,qi_service_rsp=0,qi_search_req=0,qi_search_rsp=0,qi_route_req=0,qi_route_rsp=0;
'''
    s=original.replace('module tb_candidate_offer;','module tb_candidate_offer;\n'+decl)
    monitor='''
 always @(posedge clk)if(!k_cold_rst)begin
  if((Qservice_ready&&Qservice_rsp_valid)!==1'b0)$fatal(1,"query service READY/reply overlap or unknown");
  if((Qsearch_ready&&Qsearch_rsp_valid)!==1'b0)$fatal(1,"query search READY/reply overlap or unknown");
  if((Qroute_ready&&Qroute_rsp_valid)!==1'b0)$fatal(1,"query route READY/reply overlap or unknown");
  qi_cycles=qi_cycles+1;
  if(Qservice_valid&&Qservice_ready)qi_service_req=qi_service_req+1;
  if(Qservice_rsp_valid&&Qservice_rsp_ready)qi_service_rsp=qi_service_rsp+1;
  if(Qsearch_valid&&Qsearch_ready)qi_search_req=qi_search_req+1;
  if(Qsearch_rsp_valid&&Qsearch_rsp_ready)qi_search_rsp=qi_search_rsp+1;
  if(Qroute_valid&&Qroute_ready)qi_route_req=qi_route_req+1;
  if(Qroute_rsp_valid&&Qroute_rsp_ready)qi_route_rsp=qi_route_rsp+1;
 end
'''.replace('Q','system.controller.')
    assert s.count('\nendmodule')==1;s=s.replace('\nendmodule',monitor+'\nendmodule')
    marker=' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
    assert s.count(marker)==1
    check=''' if(qi_cycles==0||qi_service_req==0||qi_search_req==0||qi_route_req==0||qi_service_req!=qi_service_rsp||qi_search_req!=qi_search_rsp||qi_route_req!=qi_route_rsp)
  $fatal(1,"query native interface coverage missing or unbalanced");
 $display("QUERY_INTERFACE_EXCLUSION_PASS cycles=%0d service_req=%0d service_rsp=%0d search_req=%0d search_rsp=%0d route_req=%0d route_rsp=%0d",qi_cycles,qi_service_req,qi_service_rsp,qi_search_req,qi_search_rsp,qi_route_req,qi_route_rsp);
'''
    return s.replace(marker,check+marker)
