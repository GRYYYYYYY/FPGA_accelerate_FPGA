"""Validate the current full paired-graph, full30, and original search evidence."""
import json
from pathlib import Path
from check_vitis_kernel import digest, require
from paired_binary_rtl_prerequisites_v1 import validate as validate_pair

ROOT = Path(__file__).resolve().parents[1]
REPORTS = {
    'snapshot_dpi_rtl_audit_20261025_v3.json':
        'full30_snapshot_dpi_rtl_original_c_and_every_complete_output_word_independently_verified',
    'search_axi_dpi_replay_audit_20261025_v3.json':
        'full_declared_depth_two_transaction_dpi_replay_cycles_all_output_bytes_and_original_c_oracle_independently_verified',
}


def validate_prerequisites(directory):
    files = validate_pair(directory.parent)
    files[str(Path(__file__).resolve())] = digest(__file__)
    for name,status in REPORTS.items():
        path = directory/name
        require(path.is_file(),'Read-control serialized prerequisite missing: '+name)
        report = json.loads(path.read_text())
        require(report.get('status')==status,'Unaccepted read-control predecessor: '+name)
        if name.startswith('snapshot'):
            require(report.get('rtl_verified') is True and report.get('transactions')==30 and report.get('pointers')==13 and report.get('models')==10,
                    'Incomplete original full30 acceptance')
            cycles = report.get('cycles',[])
            require(len(cycles)==30 and all(isinstance(value,int) and value>0 for value in cycles),'Incomplete full30 cycles')
        else:
            require(report.get('cycles')==[2132461,12404] and report.get('transactions')==2 and report.get('models')==7 and report.get('output_files')==5,
                    'Wrong original search-core oracle')
        bindings = report.get('files')
        require(isinstance(bindings,dict) and bindings,'Missing exact read-control predecessor bindings')
        for source,checksum in bindings.items():
            require(source not in files or files[source]==checksum,'Conflicting predecessor bindings')
            if source not in files:
                require(digest(source)==checksum,'Changed read-control predecessor evidence: '+source)
            files[source] = checksum
        files[str(path)] = digest(path)
    return files
