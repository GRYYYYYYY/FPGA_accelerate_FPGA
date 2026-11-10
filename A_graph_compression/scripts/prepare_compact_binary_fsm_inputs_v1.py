#!/usr/bin/env python3
"""Stage complete compact RTL/ROM and previously checked DPI models, without compiling."""
import json
import shutil
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')


def main():
    reports = [ROOT/'results/compressed_batch_compact_bus64_guarded_setup_audit_20261025_v1.json',
               ROOT/'results/compressed_compact_bus64_dpi_storage_preflight_audit_20261025_v1.json']
    files = {str(Path(__file__).resolve()):digest(__file__)}
    for path in reports:
        report = json.loads(path.read_text())
        for source, checksum in report['files'].items():
            require(digest(source)==checksum, 'Changed compact preparation evidence '+source)
            files[source] = checksum
        files[str(path)] = digest(path)
    parent = BASE/'compressed_batch_compact_bus64_rtl_guarded_v1'
    guarded = json.loads((parent/'plan.json').read_text())
    conversion_path = ROOT/'data/derived/compressed_compact_bus64_dpi_models_preflight_20261025_v1/plan.json'
    conversion = json.loads(conversion_path.read_text())
    require(guarded['graph_mode']==conversion['graph_mode']==1 and guarded['transactions']==conversion['transactions']==4, 'Different original compact scope')
    require(len(conversion['models'])==30, 'Incomplete compact AXI model matrix')
    output = ROOT/'data/derived/hls_compact_binary_fsm_inputs_20261025_v1'
    output.mkdir(exist_ok=False)
    directory = output/'verilog'
    directory.mkdir()
    sources = sorted(p for p in (parent/'sim/verilog').iterdir() if p.is_file() and p.suffix in ('.v','.sv','.dat'))
    for source in sources:
        checksum = digest(source)
        target = directory/source.name
        shutil.copyfile(source,target)
        require(digest(target)==checksum,'Copied full source differs')
        files[str(source)] = checksum
        files[str(target)] = checksum
    for model in conversion['models']:
        source = Path(model['path'])
        target = directory/source.name
        require(digest(target)==model['before_sha256'] and digest(source)==model['after_sha256'], 'Different compact DPI storage model')
        shutil.copyfile(source,target)
        require(digest(target)==model['after_sha256'], 'Converted storage model differs')
        files[str(target)] = digest(target)
    require({p.name for p in directory.iterdir()}=={p.name for p in sources}, 'Full RTL/ROM/model set changed')
    files[str(conversion_path)] = digest(conversion_path)
    atomic(output/'plan.json',dict(status='full_compact_dpi_sources_staged_for_matched_encoding_candidate_only',
        graph_mode=1, transactions=4, pointers=44, models=30, source_files=len(sources), files=files,
        original_guarded_sim=str(parent/'sim'), rtl_executed=False,
        limits=['DUT and ROM copied byte-identically; only independently audited backing-store model conversions applied',
                'All original capacities/pages/guards retained; no xelab, HLS synthesis or RTL simulation']))
    print('Staged compact mode1 complete source files',len(sources),'DPI models30; no compilation')


if __name__=='__main__':
    main()
