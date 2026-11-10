#!/usr/bin/env python3
"""Verify matched encoding policy and full bus capacities for both graph modes."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    output = ROOT/'results/paired_binary_fsm_candidates_preparation_audit_20261025_v1.json'
    require(not output.exists(), 'Refuse overwrite')
    files = {str(Path(__file__).resolve()):digest(__file__)}

    def read_bound(path):
        report = json.loads(path.read_text())
        for source, checksum in report['files'].items():
            require(digest(source)==checksum, 'Changed paired-candidate evidence '+source)
            require(source not in files or files[source]==checksum,'Conflicting paired binding')
            files[source] = checksum
        files[str(path)] = digest(path)
        return report

    baseline = read_bound(ROOT/'results/compressed_batch_csr_compact_global64_comparison_20261025_v1.json')
    require(baseline['status']=='integrated_csr_compact_global64_controlled_hls_comparison_verified_rtl_and_board_pending', 'Original source-pair comparison missing')
    require(baseline['identical_source_files']==41 and baseline['pointer_ports']==44 and baseline['memory_bundles']==30, 'Different original pair')
    transform = ROOT/'scripts/transform_hls_fsm_binary_v1.py'
    rows, bus_matrices = [], []
    for mode, stem in [(0,'hls_binary_fsm_candidate_20261025_v1'),(1,'hls_compact_binary_fsm_candidate_20261025_v1')]:
        plan_path = ROOT/'data/derived'/stem/'plan.json'
        plan = read_bound(plan_path)
        require(plan['files'][str(transform)]==digest(transform), 'Encoding implementation differs across graph modes')
        prefix = 'hls_binary_fsm' if mode==0 else 'hls_compact_binary_fsm'
        edit = read_bound(ROOT/'results'/(prefix+'_candidate_edit_audit_20261025_v1.json'))
        relation = read_bound(ROOT/'results'/(prefix+'_state_relation_audit_20261025_v1.json'))
        require(edit['status']=='binary_fsm_candidate_exact_edits_and_legal_state_encoding_map_independently_checked', 'Missing candidate edit audit')
        require(relation['status']=='actual_candidate_legal_state_decoders_and_named_transition_relations_exhaustively_checked', 'Missing real-state relation audit')
        expected = {m['module'] for m in plan['modules']}
        require(expected=={m['module'] for m in edit['modules']}=={m['module'] for m in relation['modules']}, 'Candidate audited module set differs')
        conversion_name = 'compressed_bus64_dpi_models_preflight_20261025_v1' if mode==0 else 'compressed_compact_bus64_dpi_models_preflight_20261025_v1'
        conversion_path = ROOT/'data/derived'/conversion_name/'plan.json'
        conversion = read_bound(conversion_path)
        matrix = {m['bundle']:(m['width_bits'],m['declared_depth'],m['pages']) for m in conversion['models']}
        require(len(matrix)==30 and conversion['transactions']==4 and all(v[2]==4 for v in matrix.values()), 'Incomplete full bus matrix')
        bus_matrices.append(matrix)
        mode_path = BASE/'compressed_batch_bus64_dpi_rtl_v3/plan.json' if mode==0 else ROOT/'data/derived/hls_compact_binary_fsm_inputs_20261025_v1/plan.json'
        mode_plan = read_bound(mode_path)
        require(mode_plan['graph_mode']==mode and mode_plan['transactions']==4 and len(mode_plan['models'])==30 if mode==0 else mode_plan['graph_mode']==mode and mode_plan['transactions']==4 and mode_plan['models']==30, 'Staged graph mode/scope differs')
        require(mode_plan['ports']==44 if mode==0 else mode_plan['pointers']==44, 'Pointer scope changed')
        rows.append(dict(graph_mode=mode, candidate=str(plan_path), changed_fsm_modules=len(expected), retained_files=len(plan['retained']),
            legal_states=relation['legal_states_checked'], state_predicate_pairs=relation['decoder_state_pairs_checked'],
            full_rtl_executed=False, policy='state i -> binary integer i-1; unsupported modules unchanged'))
    require(bus_matrices[0]==bus_matrices[1], 'Widths/depths/pages differ between graph modes')
    atomic(output,dict(status='both_graph_modes_matched_binary_fsm_candidate_preparations_verified_full_rtl_pending',
        candidates=rows, shared_pointer_ports=44, shared_axi_models=30, transactions_per_mode=4,
        shared_bus_width_depth_pages=bus_matrices[0], identical_cpp_sources=41, encoding_implementation_sha256=digest(transform),
        files=files, rtl_verified=False, physical_verified=False, board_verified=False,
        limits=['Matched preparation/structural mapping evidence only; both full transaction trials remain required',
                'Original negative onehot compilation results retained separately',
                'No candidate resource, clock, simulation-memory reduction, board throughput or speedup measurement']))
    print('Both graph modes matched:44 pointers/30 AXI models/all original depths/4pages; candidate RTL pending')


if __name__=='__main__':
    main()
