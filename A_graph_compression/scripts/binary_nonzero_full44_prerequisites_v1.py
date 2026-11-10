"""Strict typed predecessors for both full44 nonzero-address encoded trials."""
import json
from pathlib import Path
from check_vitis_kernel import digest,require

ROOT=Path(__file__).resolve().parents[1]
NATIVE='compact_nonzero_native_rtl_audit_20261029_v1.json'
NATIVE_STATUS='compact_nonzero_native_full4tx_full44_original_DUT_and_C_oracle_verified'
ENCODED_STATUS='binary_nonzero_full44_four_transaction_original_c_and_complete_snapshots_independently_verified'
CSR='compressed_bus64_binary_nonzero_rtl_audit_20261029_v1.json'
COMPACT='compressed_compact_bus64_binary_nonzero_rtl_audit_20261029_v1.json'
COMMON={
    'paired_binary_nonzero_axi_structure_audit_20261029_v1.json':'both_encoded_modes_complete_nonzero_address_environment_structure_independently_verified',
    'paired_axi_rebase_dpi_regression_20261029_v3.json':'both_modes_six_full_depth_models_native_vs_dpi_rebase_all4pages_verified',
    'paired_axi_rebase_dpi_independent_audit_20261029_v1.json':'both_modes_native_dpi_rebase_regression_receipts_and_full_payloads_independently_rechecked',
    'paired_binary_fsm_candidates_preparation_audit_20261025_v1.json':'both_graph_modes_matched_binary_fsm_candidate_preparations_verified_full_rtl_pending',
    'fsm_binary_four_state_regression_20261025_v1.json':'seven_state_encoding_mechanism_four_state_control_reset_and_outputs_regression_passed',
    'full_rtl_stricter_cap_incident_20261025_v1.json':'full44_dpi_compile_llvm_allocation_failure_and_native_compact_guard_abort_preserved',
    'search_axi_dpi_replay_audit_20261025_v3.json':'full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified',
}


def full_outputs(report):
    snapshots=report.get('snapshots',[]);cycles=report.get('cycles',[])
    require(len(snapshots)==4 and [s.get('transaction') for s in snapshots]==list(range(4)) and
            all(s.get('bytes')==946498280 and isinstance(s.get('sha256'),str) and len(s['sha256'])==64 for s in snapshots),'Incomplete full44 snapshots')
    require(len(cycles)==4 and all(type(c) is int and c>0 for c in cycles),'Incomplete positive actual cycles')


def native_scope(report):
    require(report.get('status')==NATIVE_STATUS and report.get('rtl_verified') is True,'Unaccepted nonzero native baseline')
    require((report.get('transactions'),report.get('pointers'),report.get('models'),report.get('pages'))==(4,44,30,4),'Partial native interface')
    require(report.get('dut_unchanged') is True and report.get('pointer_address_offset')==4096,'Different native environment')
    full_outputs(report)


def encoded_scope(report,mode):
    require(report.get('status')==ENCODED_STATUS and report.get('rtl_verified') is True,'Unaccepted nonzero encoded result')
    require((report.get('graph_mode'),report.get('transactions'),report.get('ports'),report.get('models'),report.get('pages'))==(mode,4,44,30,4),'Partial/wrong-mode encoded interface')
    require(report.get('candidate_encoding_changed') is True and report.get('native_cycle_parity_claimed') is False and report.get('pointer_address_offset')==4096,'Different encoded identity/environment')
    require(report.get('encoded_modules')==(43 if mode==0 else 45),'Incomplete encoded module set')
    full_outputs(report)


def validate(mode,root=ROOT):
    require(mode in [0,1],'Unsupported graph mode'); files={str(Path(__file__).resolve()):digest(__file__)}
    def load(name,status=None):
        p=root/'results'/name;require(p.is_file(),'Nonzero full44 prerequisite missing: '+name)
        r=json.loads(p.read_text())
        if status:require(r.get('status')==status,'Unaccepted nonzero full44 prerequisite: '+name)
        require(isinstance(r.get('files'),dict) and r['files'],'Missing exact prerequisite bindings')
        for n,h in r['files'].items():
            require(n not in files or files[n]==h,'Conflicting prerequisite binding')
            if n not in files: require(digest(n)==h,'Changed nonzero prerequisite evidence: '+n)
            files[n]=h
        files[str(p)]=digest(p);return r
    native=load(NATIVE,NATIVE_STATUS);native_scope(native)
    if mode==1:
        csr=load(CSR,ENCODED_STATUS);encoded_scope(csr,0)
        require(csr['files'].get(str(root/'results'/NATIVE))==files[str(root/'results'/NATIVE)],'CSR accepted a different native baseline')
    for name,status in COMMON.items():
        r=load(name,status)
        if name.startswith('paired_binary_nonzero_axi_structure'):
            require([(m['graph_mode'],m['models'],m['pointers'],m['transactions']) for m in r['modes']]==[(0,30,44,4),(1,30,44,4)],'Partial paired wrapper structure')
        elif name.startswith('paired_axi_rebase_dpi_regression'):
            expected={'completion_mem':(32,65536),'state_mem':(64,65),'site_scratch_mem':(64,163840),'node_meta_mem':(64,4),'tree_meta_mem':(64,5),'batch_input_mem':(64,16)}
            require(len(r['models'])==12 and {(m['graph_mode'],m['bundle']):(m['data_bits'],m['depth']) for m in r['models']}=={(g,b):d for g in [0,1] for b,d in expected.items()},'Incomplete native/DPI model matrix')
            for m in r['models']:
                require(m['pages']==4 and m['native_reference'] and m['dpi_registration_verified'] and m['response_cycles_compared'],'Incomplete model behavior proof')
                if m['bundle']=='batch_input_mem':require(m['readonly_full_page_words_read']==64 and m['readonly_write_and_zero_strobe_rejected'],'Partial readonly coverage')
                else:require(m['all_output_words_verified']==m['depth']*4,'Partial output comparison')
        elif name.startswith('paired_binary_fsm_candidates'):
            require((r['shared_pointer_ports'],r['shared_axi_models'],r['transactions_per_mode'],r['identical_cpp_sources'])==(44,30,4,41) and [c['graph_mode'] for c in r['candidates']]==[0,1],'Partial original matched pair')
        elif name.startswith('fsm_binary_four'):
            require(r['samples']==1280 and r['input_level_cases']==64 and r['all_seven_states_observed'],'Partial four-state regression')
    prefix='hls_binary_fsm' if mode==0 else 'hls_compact_binary_fsm'
    for name,status in [(prefix+'_candidate_edit_audit_20261025_v1.json','binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked'),(prefix+'_state_relation_audit_20261025_v1.json','actual_candidate_legal_state_decoders_and_named_transition_relations_exhaustively_checked')]:
        report=load(name,status);require(len(report['modules'])==(43 if mode==0 else 45),'Partial legal-state/edit proof')
    return files
