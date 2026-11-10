"""Accept typed CSR candidate proof before paired compact candidate execution."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {
    'compressed_bus64_binary_fsm_rtl_audit_20261025_v1.json':
        'binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified',
    'paired_binary_fsm_candidates_preparation_audit_20261025_v1.json':
        'both_graph_modes_matched_binary_fsm_candidate_preparations_verified_full_rtl_pending',
    'hls_compact_binary_fsm_candidate_edit_audit_20261025_v1.json':
        'binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked',
    'hls_compact_binary_fsm_state_relation_audit_20261025_v1.json':
        'actual_candidate_legal_state_decoders_and_named_transition_relations_exhaustively_checked',
}


def validate(root=ROOT):
    files = {str(Path(__file__).resolve()):digest(__file__)}
    for name,status in REPORTS.items():
        path = root/'results'/name
        require(path.is_file(),'Paired compact binary-FSM prerequisite missing: '+name)
        report = json.loads(path.read_text())
        require(report.get('status')==status,'Unaccepted paired compact prerequisite: '+name)
        bindings = report.get('files')
        require(isinstance(bindings,dict) and bindings,'Missing exact paired prerequisite bindings')
        if name.startswith('compressed_bus64_binary'):
            require(report.get('ports')==44 and report.get('models')==30 and len(report.get('snapshots',[]))==4,
                    'Incomplete original CSR candidate acceptance')
            require(report.get('candidate_encoding_changed') is True,'Wrong unencoded CSR predecessor')
        if name.startswith('paired_binary'):
            require(report.get('shared_pointer_ports')==44 and report.get('shared_axi_models')==30 and report.get('transactions_per_mode')==4,
                    'Incomplete matched original interface')
            require([r['graph_mode'] for r in report['candidates']]==[0,1],'Wrong graph-mode pair')
        if name.startswith('hls_compact'):
            require(len(report.get('modules',[]))==45,'Incomplete compact encoding proof')
        for source,checksum in bindings.items():
            require(source not in files or files[source]==checksum,'Conflicting paired evidence')
            if source not in files:
                require(digest(source)==checksum,'Changed paired compact evidence: '+source)
            files[source] = checksum
        files[str(path)] = digest(path)
    return files
