"""Serialize full50 after actual acceptance of both current nonzero graph modes."""
import json
from pathlib import Path
from binary_nonzero_full44_prerequisites_v2 import validate, encoded_scope, NATIVE, CSR, COMPACT, ROOT
from check_vitis_kernel import digest, require


def validate_predecessors(root=ROOT):
    bindings=validate(1,root)
    path=root/'results'/COMPACT
    report=json.loads(path.read_text());encoded_scope(report,1)
    require(isinstance(report.get('files'),dict) and report['files'],'Missing compact evidence')
    for name in [NATIVE,CSR]:
        p=str(root/'results'/name)
        require(report['files'].get(p)==bindings[p],'Compact accepted a different predecessor')
    for p,h in report['files'].items():
        require(p not in bindings or bindings[p]==h,'Conflicting accepted evidence')
        if p not in bindings:require(digest(p)==h,'Changed compact acceptance evidence')
        bindings[p]=h
    bindings[str(path)]=digest(path)
    return bindings
