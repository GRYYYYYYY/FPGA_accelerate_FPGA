"""Specialize reply qualification only for source-proven exclusive backends."""
from pathlib import Path
import hashlib, json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/route_block_system_crc_pressure_v1')
NAMES = ['recovery_coordinator.sv', 'residency_system.sv',
         'search_residency_system.sv', 'query_residency_system.sv']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def replace_once(s, old, new):
    assert s.count(old) == 1, old
    return s.replace(old, new, 1)

def sources(fixed):
    m = json.loads((BASE / 'manifest.json').read_text())
    a = json.loads((BASE / 'source_bound_audit.json').read_text())
    receipt = json.loads((ROOT / 'results' / (BASE.name + '_restore_20261025.json')).read_text())
    proof = json.loads((ROOT / 'results/recovery_backend_exclusion_20261027.json').read_text())
    assert m['status'] == 'observed' and a['status'] == receipt['status'] == 'passed'
    assert a['manifest_sha256'] == sha(BASE / 'manifest.json')
    assert receipt['audit_byte_identical'] and receipt['audit_sha256'] == sha(BASE / 'source_bound_audit.json')
    assert proof['status'] == 'native_interface_exclusion_verified_not_rtl_validation'
    assert proof['analyzer_sha256'] == sha(ROOT / 'scripts/analyze_recovery_backend_exclusion.py')
    for n, h in proof['source_sha256'].items():
        assert sha(BASE / 'sources' / n) == h == m['sources'][n]['sha256'], n
    result = {}
    for n in NAMES:
        p = BASE / 'sources' / n
        assert sha(p) == m['sources'][n]['sha256']
        result[n] = p.read_text()
    if fixed:
        n = 'recovery_coordinator.sv'
        s = replace_once(result[n], 'MAX_CYCLES=1048576)(',
                         'MAX_CYCLES=1048576,EXCLUSIVE_BACKEND_RESPONSES=0)(')
        old = ' wire unexpected=(a_rsp_valid&&state!=AW&&!(state==AS&&a_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready));'
        new = ''' // Enabled only when each backend guarantees !(request_ready && response_valid).
 // Default preserves request-cycle responses for general external backends.
 wire unexpected=EXCLUSIVE_BACKEND_RESPONSES ?
     ((a_rsp_valid&&state!=AW)||(o_rsp_valid&&state!=OW)) :
     ((a_rsp_valid&&state!=AW&&!(state==AS&&a_ready))||(o_rsp_valid&&state!=OW&&!(state==OS&&o_ready)));'''
        result[n] = replace_once(s, old, new)
        for n in ['residency_system.sv', 'search_residency_system.sv']:
            result[n] = replace_once(result[n], 'RESTORE_RECORDS=512)(',
                'RESTORE_RECORDS=512,EXCLUSIVE_BACKEND_RESPONSES=0)(')
        result['residency_system.sv'] = replace_once(result['residency_system.sv'],
            'recovery_coordinator #(.ENTRIES(32),',
            'recovery_coordinator #(.EXCLUSIVE_BACKEND_RESPONSES(EXCLUSIVE_BACKEND_RESPONSES),.ENTRIES(32),')
        result['search_residency_system.sv'] = replace_once(result['search_residency_system.sv'],
            'residency_system #(.PATH_SLOTS(PATH_SLOTS),',
            'residency_system #(.EXCLUSIVE_BACKEND_RESPONSES(EXCLUSIVE_BACKEND_RESPONSES),.PATH_SLOTS(PATH_SLOTS),')
        result['query_residency_system.sv'] = replace_once(result['query_residency_system.sv'],
            'search_residency_system #(.PATH_SLOTS(PATH_SLOTS),',
            '// Native authority reader and owner fence lane9 provide exclusive request/reply qualifiers.\n'
            'search_residency_system #(.EXCLUSIVE_BACKEND_RESPONSES(1),.PATH_SLOTS(PATH_SLOTS),')
    return result

def monitored_tb(original):
    monitor = '''
 // Observation only: neither stimulus nor any DUT handshake is overridden.
 integer exclusive_checks=0,exclusive_a_requests=0,exclusive_a_replies=0;
 integer exclusive_o_requests=0,exclusive_o_replies=0;
 always @(posedge clk) if(!k_cold_rst)begin
  if((system.k_a_ready&&system.k_a_rsp_valid)!==1'b0)
   $fatal(1,"authority READY/reply VALID exclusion failed");
  if((system.inner.backend.k_o_ready&&system.inner.backend.k_o_rsp_valid)!==1'b0)
   $fatal(1,"owner READY/reply VALID exclusion failed");
  exclusive_checks=exclusive_checks+1;
  if(system.k_a_valid&&system.k_a_ready)exclusive_a_requests=exclusive_a_requests+1;
  if(system.k_a_rsp_valid&&system.k_a_rsp_ready)exclusive_a_replies=exclusive_a_replies+1;
  if(system.inner.backend.k_o_valid&&system.inner.backend.k_o_ready)exclusive_o_requests=exclusive_o_requests+1;
  if(system.inner.backend.k_o_rsp_valid&&system.inner.backend.k_o_rsp_ready)exclusive_o_replies=exclusive_o_replies+1;
 end
'''
    declaration = ' integer exclusive_checks=0,exclusive_a_requests=0,exclusive_a_replies=0;\n integer exclusive_o_requests=0,exclusive_o_replies=0;\n'
    assert declaration in monitor
    monitor = monitor.replace(declaration, '')
    s = replace_once(original, 'module tb_candidate_offer;', 'module tb_candidate_offer;\n' + declaration)
    s = replace_once(s, '\nendmodule', monitor + '\nendmodule')
    marker = ' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
    check = ''' if(exclusive_checks==0||exclusive_a_requests==0||exclusive_o_requests==0||
    exclusive_a_requests!=exclusive_a_replies||exclusive_o_requests!=exclusive_o_replies)
  $fatal(1,"exclusive backend coverage or retirement missing");
 $display("BACKEND_EXCLUSION_PASS cycles=%0d authority=%0d owner=%0d",exclusive_checks,exclusive_a_requests,exclusive_o_requests);
'''
    return replace_once(s, marker, check + marker)

if __name__ == '__main__':
    for mode in ['baseline', 'fixed']:
        d = HERE / mode
        d.mkdir()
        for n, s in sources(mode == 'fixed').items():
            (d / n).write_text(s)
    (HERE / 'tb_query_fault.sv').write_text(monitored_tb((BASE / 'sources/tb_query_fault.sv').read_text()))
    print('RECOVERY_BACKEND_CANDIDATE_PREPARED_NOT_VALIDATED')
