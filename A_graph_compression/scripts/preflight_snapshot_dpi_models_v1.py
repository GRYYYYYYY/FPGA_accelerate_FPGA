#!/usr/bin/env python3
"""Preflight storage conversion for the unchanged30-transaction snapshot target."""
import json
import os
import re
from pathlib import Path
from check_vitis_kernel import digest,require
from transform_axi_memory_dpi_v2 import transform
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    source=BASE/'snapshot_rtl_local_project/solution/sim/verilog'
    parent=BASE/'snapshot_rtl_local_recovery/plan.json';original=json.loads(parent.read_text())
    setup_path=ROOT/'results/resident_snapshot_rtl_setup_20261024_v1.json';setup=json.loads(setup_path.read_text())
    require(original['transactions']==setup['transactions']==30 and len(setup['memory_vectors'])==12 and all(v['transactions']==30 for v in setup['memory_vectors'].values()),'Different snapshot transaction/bundle vector scope')
    top=ROOT/'hardware/vitis/search_resident_snapshot_top.cpp'
    require(len(re.findall(r'#pragma HLS INTERFACE m_axi port=',top.read_text()))==13,'Different pointer interface')
    require(digest(top) in [h for p,h in original['files'].items() if p.endswith('/search_resident_snapshot_top.cpp')],'Changed original snapshot top')
    paths=sorted(source.glob('AESL_axi_master_*.v'));require(len(paths)==10,'Different snapshot AXI model matrix')
    out=ROOT/'data/derived/snapshot_dpi_models_preflight_20261025_v1';out.mkdir(exist_ok=False)
    a_dir=out/'input/verilog';b_dir=out/'converted/verilog';a_dir.mkdir(parents=True);b_dir.mkdir(parents=True)
    files={str(p):digest(p) for p in [parent,setup_path,top,Path(__file__).resolve(),ROOT/'scripts/transform_axi_memory_dpi_v2.py']}
    models=[];capacity=0
    for p in paths:
        require(digest(p)==original['copied'][str(p)],'Original full-depth model changed '+p.name)
        before=p.read_text();after,ledger=transform(before)
        a=a_dir/p.name;b=b_dir/p.name;l=out/(p.stem+'.edits.json')
        a.write_text(before);b.write_text(after);l.write_text(json.dumps(ledger,indent=2)+'\n')
        bundle=ledger['bundle']
        width=int(re.search(r'parameter\s+'+bundle+r'_DATA_BITWIDTH\s*=\s*32\x27d\s*(\d+)',before)[1])
        depth=int(re.search(r'parameter\s+'+bundle+r'_mem_depth\s*=\s*32\x27d\s*(\d+)',before)[1])
        require(ledger['pages']==4,'Different transaction page count')
        capacity+=width//4*depth*ledger['pages']
        for path in [p,a,b,l]:files[str(path)]=digest(path)
        models.append(dict(path=str(b),ledger=str(l),before_sha256=digest(a),after_sha256=digest(b),pages=ledger['pages'],bundle=bundle,width_bits=width,declared_depth=depth))
    report=dict(status='snapshot_30_transaction_13_pointer_10_model_storage_preflight_only',
                original_sim=str(a_dir.parent),transactions=30,pointers=13,models=models,files=files,
                declared_four_state_backing_bytes=capacity,
                limits=['Only AXI storage text converted; DUT, ROM and transaction data untouched; no simulation performed',
                        'Four memory pages per model remain unchanged;30 is transaction count',
                        'Full30-transaction DUT execution, original C postcheck and independent complete-state acceptance remain required',
                        'Backing bytes do not bound compiler memory usage'])
    temporary=out/'plan.tmp'
    with temporary.open('x') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,out/'plan.json');print(report['status'],capacity)
if __name__=='__main__':main()
