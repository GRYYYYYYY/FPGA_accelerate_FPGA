#!/usr/bin/env python3
"""Prepare exact complete sources; do not launch a compiler or create the trial."""
import json
from pathlib import Path
import re
from compact_nonzero_native_contract_v2 import *


def main():
    require(not PREP.exists() and not PREPORT.exists() and not OUT.exists(),'Refuse overwrite/restart')
    files,vectors,models=evidence()
    mapping={str(Path('tv/cdatafile')/Path(r['source']).name):(r['relocated'],'pointer') for r in vectors['pointer_vectors'].values()}
    mapping.update({str(Path('verilog')/Path(m['source']).name):(m['target'],'model') for m in models['models']})
    manifest={}; old=json.loads((OLD/'plan.json').read_text())['copied']
    for name,record in old.items():
        relative=Path(name).relative_to(OLD/'sim')
        if not selected(relative): continue
        require(digest(name)==record['sha256'],'Original source changed '+name)
        source,kind=mapping.get(str(relative),(name,'unchanged'))
        manifest[str(relative)]=dict(source=str(source),sha256=digest(source),kind=kind,original=name,original_sha256=record['sha256'])
        files[name]=record['sha256'];files[str(source)]=digest(source)
    # Retain every original project line, appending only the checked wrapper guard.
    project='verilog/search_batch_trace_top_v2.prj'; original=Path(manifest[project]['source']).read_text()
    for line in original.splitlines():
        if not line.strip(): continue
        m=re.fullmatch(r'sv (?:work|xil_defaultlib) "([^"/]+)"',line)
        require(m is not None and 'verilog/'+m[1] in manifest,'Unbound project source')
    for rel,record in manifest.items():
        if Path(rel).suffix in ['.v','.sv','.svh'] and record['kind']=='unchanged':
            require(re.search(r'\bAESL_AXI_MASTER_\w+\s*\.',Path(record['source']).read_text()) is None,'External memory-model internal hierarchy reference needs review')
    PREP.mkdir()
    p=PREP/'search_batch_trace_top_v2.prj';p.write_text(original+'sv xil_defaultlib "axi_model_rebase_guard_v1.sv"\n')
    manifest[project].update(source=str(p),sha256=digest(p),kind='project_guard_append');files[str(p)]=digest(p)
    guard=ROOT/'hardware/vitis/axi_model_rebase_guard_v1.sv'
    manifest['verilog/axi_model_rebase_guard_v1.sv']=dict(source=str(guard),sha256=digest(guard),kind='guard')
    for name in ['compact_nonzero_native_contract_v2.py','prepare_compact_nonzero_native_trial_v2.py','run_compact_nonzero_native_rtl_v2.py','check_compact_nonzero_native_rtl_v2.py','supervise_compact_nonzero_native_rtl_v2.py','check_vitis_kernel.py','check_compact_nonzero_axi_models_v1.py','owned_sim_resource_policy_v1.py']:
        p=ROOT/'scripts'/name;files[str(p)]=digest(p)
    result=dict(status='nonzero_native_full4tx44pointers30models_entry_prepared',files=files,manifest=manifest,commands=commands(),
                transactions=4,pointers=44,models=30,dut_unchanged=True,original_payloads_unchanged=True,
                runtime_as_bytes=RUNTIME_AS,stack_bytes=STACK,core_bytes=0,compiler_as_bytes=COMPILER_AS,resource_policy=POLICY,free_memory_gate_removed_by_user=True,
                startup_gate_removed_by_user=True,rtl_executed=False,compiled_snapshot_reused=False,
                compiler_original_peak_rss_kib=158275628,
                limits=['Original compiler O0/mt-off preserved, with AS tightened from unlimited to192GiB; default timescale retained.',
                        'Original compiler RSS was about151GiB; no assertion that current shared memory or original policy guarantees completion.',
                        'No shared free/cache memory gate; new actual cgroup OOM events stop only the owned process group. No automatic retry or cache clearing.',
                        '4tx/44-pointer full C oracle and four946498280-byte snapshots remain mandatory.'])
    with PREPORT.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    verify_preparation();print(result['status'],len(manifest),'files')


if __name__=='__main__': main()
