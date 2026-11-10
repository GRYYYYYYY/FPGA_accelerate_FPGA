#!/usr/bin/env python3
"""Preflight all full-batch AXI backing models without copying or reducing DUT/TV."""
import json
import os
import re
from pathlib import Path
from check_vitis_kernel import digest,require
from transform_axi_memory_dpi_v2 import transform

ROOT=Path(__file__).resolve().parents[1]
LOCAL=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def main():
    guarded=LOCAL/'compressed_batch_bus64_rtl_guarded_v1'
    parent=json.loads((guarded/'plan.json').read_text())
    setup_path=ROOT/'results/compressed_batch_bus64_full_depth_cosim_setup_20261025_v1.json'
    require(digest(setup_path)==parent['setup_sha256'],'Setup proof changed')
    setup=json.loads(setup_path.read_text());guards={r['bundle']:r for r in parent['models']}
    source=Path(parent['cwd']);paths=sorted(source.glob('AESL_axi_master_*.v'))
    require(len(paths)==30 and parent['transactions']==4 and parent['graph_mode']==0,'Different full-batch scope')
    out=ROOT/'data/derived/compressed_bus64_dpi_models_preflight_20261025_v1'
    out.mkdir(exist_ok=False)
    original=out/'input/verilog';target=out/'converted/verilog'
    original.mkdir(parents=True);target.mkdir(parents=True)
    files={str(setup_path):digest(setup_path),str(guarded/'plan.json'):digest(guarded/'plan.json'),str(Path(__file__).resolve()):digest(Path(__file__).resolve()),str(ROOT/'scripts/transform_axi_memory_dpi_v2.py'):digest(ROOT/'scripts/transform_axi_memory_dpi_v2.py')}
    models=[];capacity=0
    for path in paths:
        bundle=path.stem.removeprefix('AESL_axi_master_')
        if bundle in guards:expected=guards[bundle]['guarded_sha256']
        else:
            matches=[h for p,h in setup['files'].items() if p.endswith('/sim/verilog/'+path.name)]
            require(len(matches)==1,'Missing unguarded original model binding '+bundle);expected=matches[0]
        require(digest(path)==expected,'Changed prepared model '+bundle)
        before=path.read_text();after,ledger=transform(before)
        a=original/path.name;b=target/path.name;l=out/(path.stem+'.edits.json')
        a.write_text(before);b.write_text(after);l.write_text(json.dumps(ledger,indent=2)+'\n')
        width=int(re.search(r'parameter\s+'+bundle+r'_DATA_BITWIDTH\s*=\s*32\x27d\s*(\d+)',before)[1])
        depth=int(re.search(r'parameter\s+'+bundle+r'_mem_depth\s*=\s*32\x27d\s*(\d+)',before)[1])
        require(ledger['pages']==4 and 32<=width<=64,'Different bus/page matrix')
        capacity+=width//8*depth*ledger['pages']
        for p in [path,a,b,l]:files[str(p)]=digest(p)
        models.append(dict(path=str(b),ledger=str(l),before_sha256=digest(a),after_sha256=digest(b),pages=ledger['pages'],width_bits=width,declared_depth=depth,bundle=bundle))
    plan=dict(status='all_30_full_batch_models_storage_conversion_preflight_only_no_rtl_execution',
              original_sim=str(original.parent),models=models,files=files,transactions=4,
              declared_model_payload_bytes_all_pages=capacity,
              limits=['No DUT/ROM/TV files changed or copied; only exact model storage conversion preflight',
                      'Full search-core DPI replay must pass before using these changes for batch RTL acceptance',
                      'All original full-depth four-transaction original C postchecks and complete snapshot/trace oracles remain required'])
    temporary=out/'plan.tmp'
    with temporary.open('x') as f:json.dump(plan,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,out/'plan.json')
    print(plan['status'],len(models),capacity)
if __name__=='__main__':main()
