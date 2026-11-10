#!/usr/bin/env python3
"""Freeze matched compact global64 physical inputs without launching Vivado."""
import json
import shutil
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    review = ROOT/'results/compressed_batch_compact_bus64_synthesis_review_20261025_v1.json'
    synthesis = json.loads(review.read_text())
    require(synthesis['status'] == 'compressed_batch_trace_compact_bus64_integrated_control_csim_synthesis_verified_rtl_pending', 'Wrong synthesis review')
    csr = ROOT/'data/derived/compressed_batch_bus64_physical_20261025_v1'
    reference = json.loads((csr/'plan.json').read_text())
    output = ROOT/'data/derived/compressed_batch_compact_bus64_physical_20261025_v1'
    output.mkdir(exist_ok=False)
    work = output/'compact'
    (work/'source').mkdir(parents=True)
    rtl = BASE/'compressed_batch_compact_bus64_hls_project/solution/syn/verilog'
    sources = sorted(p for p in rtl.iterdir() if p.suffix in ('.v', '.dat'))
    require(sources, 'Missing complete synthesized RTL/ROM set')
    generated = {}
    for source in sources:
        checksum = digest(source)
        require(synthesis['files'].get(str(source)) == checksum, 'Unbound synthesized file '+str(source))
        target = work/'source'/source.name
        shutil.copyfile(source, target)
        require(digest(target) == checksum, 'Copied RTL/ROM differs')
        generated[str(target)] = checksum
    for name in ('run_flow.tcl', 'clock.xdc'):
        source = csr/'csr'/name
        require(reference['generated'][str(source)] == digest(source), 'Changed original CSR physical flow')
        shutil.copyfile(source, work/name)
        require(digest(work/name) == digest(source), 'Paired physical flow differs')
        generated[str(work/name)] = digest(work/name)
    gates = [
        'search_axi_dpi_replay_audit_20261025_v3.json',
        'compressed_bus64_dpi_rtl_audit_20261025_v1.json',
        'snapshot_dpi_rtl_audit_20261025_v1.json',
        'compressed_compact_bus64_dpi_rtl_audit_20261025_v1.json',
    ]
    plan = dict(status='compact_global64_matched_physical_inputs_prepared_not_executed',
        inputs={str(review): digest(review), str(csr/'plan.json'): digest(csr/'plan.json'), str(Path(__file__).resolve()): digest(__file__)},
        generated=generated, source_rtl_files=len(sources), top=reference['top'], part=reference['part'],
        clock_ns=reference['clock_ns'], setup_uncertainty_ns=reference['setup_uncertainty_ns'], max_threads=reference['max_threads'],
        execution_gates=[str(ROOT/'results'/name) for name in gates], minimum_raw_free_bytes=184*1024**3,
        physical_executed=False, execution_entry_prepared=False,
        limits=['Frozen inputs only; no execution supervisor or Vivado session created',
                'Future execution entry must verify every accepted prerequisite status and file binding before launch',
                'Physical resource policy remains separate from simulator address-space policy',
                'OOC characterization cannot establish platform fit or board acceleration'])
    atomic(output/'plan.json', plan)
    # Independently re-read the complete output set and original files after copying.
    require({p.name for p in (work/'source').iterdir()} == {p.name for p in sources}, 'Incomplete output source set')
    for source in sources:
        require(digest(work/'source'/source.name) == synthesis['files'][str(source)], 'Post-copy source mismatch')
    for path, checksum in generated.items():
        require(digest(path) == checksum, 'Changed prepared artifact')
    audit = ROOT/'results/compressed_compact_bus64_physical_preparation_20261025_v1.json'
    require(not audit.exists(), 'Refuse overwrite')
    atomic(audit, dict(status=plan['status'], physical_executed=False, execution_entry_prepared=False,
        source_rtl_files=len(sources), matched_flow_bytes=True, execution_gates=plan['execution_gates'],
        files={str(output/'plan.json'): digest(output/'plan.json'), **plan['inputs'], **generated}, limits=plan['limits']))
    print(audit)


if __name__ == '__main__':
    main()
