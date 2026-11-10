"""Accept only completed, byte-current independent RTL prerequisites."""
import json
from check_vitis_kernel import digest, require

EXPECTED = {
    'search_axi_dpi_replay_audit_20261025_v3.json':
        'full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified',
    'compressed_bus64_dpi_rtl_audit_20261025_v1.json':
        'compressed_bus64_full44_four_transaction_dpi_rtl_c_postcheck_and_complete_snapshots_independently_verified',
    'snapshot_dpi_rtl_audit_20261025_v1.json':
        'full30_snapshot_dpi_rtl_original_c_and_every_complete_output_word_independently_verified',
}


def validate_prerequisites(directory):
    bindings = {}
    for name, expected in EXPECTED.items():
        path = directory / name
        require(path.is_file(), 'Serial prerequisite missing: ' + name)
        report = json.loads(path.read_text())
        require(report.get('status') == expected, 'Unaccepted prerequisite: ' + name)
        files = report.get('files')
        require(isinstance(files, dict) and bool(files), 'Missing prerequisite bindings: ' + name)
        for source, checksum in files.items():
            require(digest(source) == checksum, 'Changed prerequisite evidence: ' + source)
            require(source not in bindings or bindings[source] == checksum,
                    'Conflicting prerequisite binding: ' + source)
            bindings[source] = checksum
        bindings[str(path)] = digest(path)
    return bindings
