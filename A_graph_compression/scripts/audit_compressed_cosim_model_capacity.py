#!/usr/bin/env python3
"""Check generated AXI model capacity against all declared pointer payloads."""
import hashlib
import json
from pathlib import Path
import re
import os
import tempfile
ROOT=Path(__file__).resolve().parents[1]
def main():
    inventory=ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    ports=json.loads(inventory.read_text())['ports']
    directory=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_cosim_project/solution/sim/verilog')
    groups={}
    for p in ports:
        groups.setdefault(p['bundle'],[]).append(p)
    rows=[];files={}
    for bundle,members in sorted(groups.items()):
        path=directory/f'AESL_axi_master_{bundle}.v';text=path.read_text()
        def parameter(suffix):
            match=re.search(r'parameter\s+'+re.escape(bundle+suffix)+r"\s*=\s*32'd\s*(\d+)",text)
            if match is None:raise ValueError('Missing model parameter '+bundle+suffix)
            return int(match.group(1))
        width=parameter('_DATA_BITWIDTH');depth=parameter('_mem_depth')
        assert width%8==0
        required=sum(p['payload_bytes'] for p in members)
        actual=depth*(width//8)
        assert actual>=required,(bundle,actual,required)
        rows.append(dict(bundle=bundle,ports=[p['name'] for p in members],data_bits=width,depth=depth,bytes_per_transaction=actual,declared_payload_bytes=required))
        files[str(path)]=hashlib.sha256(path.read_bytes()).hexdigest()
    assert sum(len(r['ports']) for r in rows)==44 and len(rows)==30
    for p in [inventory,Path(__file__).resolve()]:files[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
    report=dict(status='all44_pointer_declared_payloads_fit_generated30_axi_models_static_check_only',models=rows,files=files,limits=['Capacity check only; actual transaction file counts and address allocation still require independent validation','No RTL execution or readonly-region write protection proved'])
    target=ROOT/'results/compressed_batch_cosim_model_capacity_20261025_v1.json'
    if target.exists():raise FileExistsError(target)
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as out:json.dump(report,out,indent=2);out.write('\n');out.flush();os.fsync(out.fileno())
    os.replace(tmp,target)
    print(report['status'])
if __name__=='__main__':main()
