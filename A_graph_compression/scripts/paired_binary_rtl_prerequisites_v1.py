"""Require actual accepted full44 RTL results from both encoded graph modes."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {
    'compressed_bus64_binary_fsm_rtl_audit_20261025_v1.json':
        'binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified',
    'compressed_compact_bus64_binary_fsm_rtl_audit_20261025_v1.json':
        'compact_binary_fsm_full44_four_transaction_dpi_rtl_original_c_and_complete_snapshots_independently_verified',
}


def validate(root=ROOT):
    files = {str(Path(__file__).resolve()):digest(__file__)}
    for name,status in REPORTS.items():
        path = root/'results'/name
        require(path.is_file(),'Paired full44 RTL prerequisite missing: '+name)
        report = json.loads(path.read_text())
        require(report.get('status')==status,'Unaccepted paired full44 RTL prerequisite: '+name)
        require(report.get('ports')==44 and report.get('models')==30 and len(report.get('snapshots',[]))==4,
                'Incomplete full44 interface/output acceptance')
        require(report.get('candidate_encoding_changed') is True,'Wrong unencoded predecessor')
        cycles = report.get('cycles',[])
        require(len(cycles)==4 and all(isinstance(value,int) and value>0 for value in cycles),'Incomplete actual transaction cycles')
        bindings = report.get('files')
        require(isinstance(bindings,dict) and bindings,'Missing exact predecessor bindings')
        for source,checksum in bindings.items():
            require(source not in files or files[source]==checksum,'Conflicting paired acceptance evidence')
            if source not in files:
                require(digest(source)==checksum,'Changed paired full44 RTL evidence: '+source)
            files[source] = checksum
        files[str(path)] = digest(path)
    return files
