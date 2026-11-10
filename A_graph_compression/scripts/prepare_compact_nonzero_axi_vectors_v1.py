#!/usr/bin/env python3
"""Prepare all44 relocated pointer vectors; no DUT/model change or flow launch."""
import json
from pathlib import Path
import re

from check_vitis_kernel import digest, require

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/A_graph_compression_recovery_20261025_v1')
TRIAL = BASE/'compact_native_stack_recovery_v3'
OFFSET = 4096  # Preserve the low12 address bits, including AXI4KiB burst boundaries.


def main():
    out = ROOT/'data/derived/compact_nonzero_axi_vectors_20261029_v1'
    report = ROOT/'results/compact_nonzero_axi_vectors_preparation_20261029_v1.json'
    require(not out.exists() and not report.exists(), 'Refuse overwrite')
    diagnosis_path = ROOT/'results/compact_native_v3_postcheck_diagnosis_20261029_v1.json'
    diagnosis = json.loads(diagnosis_path.read_text())
    require(diagnosis['status'] == 'full4tx_rtl_completed_but_original_postcheck_failed'
            and diagnosis['rtl_verified'] is False, 'Different original incident')
    files = {str(diagnosis_path): digest(diagnosis_path)}
    for filename, status in [
        ('compact_native_first_search_replay_audit_20261029_v1.json',
         'saved_failed_rtl_first_search_inputs_match_original_C_search_oracle_when_host_pointers_nonnull'),
        ('compact_null_pointer_cone_audit_20261029_v1.json',
         'original_synthesized_null_pointer_cone_executed_16_cases_verified')]:
        p = ROOT/'results'/filename; proof = json.loads(p.read_text())
        require(proof['status'] == status, 'Missing diagnostic proof')
        files[str(p)] = digest(p)
    inventory_path = ROOT/'hardware/vitis/compressed_batch_rtl_full_depth_inventory.json'
    allocation_path = ROOT/'results/compressed_batch_compact_cosim_allocations_20261025_v1.json'
    inventory = json.loads(inventory_path.read_text())
    allocation = json.loads(allocation_path.read_text())
    ports = {p['name']: p for p in inventory['ports']}
    require(len(ports) == 44 and len(allocation['allocations']) == 30, 'Incomplete interface')
    files[str(inventory_path)] = digest(inventory_path)
    files[str(allocation_path)] = digest(allocation_path)
    rows = {}; groups = []
    for group in allocation['allocations']:
        bundles = {ports[r['name']]['bundle'] for r in group['regions']}
        require(len(bundles) == 1, 'Mixed AXI bundles')
        bundle = next(iter(bundles))
        for region in group['regions']:
            name = region['name']; port = ports[name]
            require(name not in rows and 0 <= region['start'] < region['end'] <= 2**64-OFFSET, 'Bad allocation')
            require(region['end']-region['start'] >= port['payload_bytes'], 'Capacity shrunk')
            vector_name = name+'_r' if name in ['image', 'config'] else name
            source = TRIAL/'sim/tv/cdatafile'/('c.search_batch_trace_top_v2.autotvin_'+vector_name+'.dat')
            sha = digest(source)
            require(sha == diagnosis['files'][str(source)], 'Actual pointer input changed')
            text = source.read_text()
            found = re.findall(r'\[\[transaction\]\]\s+(\d+)\s+(0x[0-9a-fA-F]+)\s+\[\[/transaction\]\]', text)
            require([int(i) for i, _ in found] == list(range(4)), 'Wrong four-transaction vector')
            require([int(v, 16) for _, v in found] == [region['start']]*4, 'Pointer differs from actual allocation')
            tokens = re.findall(r'0x[0-9a-fA-F]+', text)
            require(len(tokens) == 4, 'Unexpected pointer data')
            shifted = re.sub(r'0x[0-9a-fA-F]+', lambda m: '0x'+format(int(m[0], 16)+OFFSET, '0'+str(len(m[0])-2)+'x'), text)
            restored = re.sub(r'0x[0-9a-fA-F]+', lambda m: '0x'+format(int(m[0], 16)-OFFSET, '0'+str(len(m[0])-2)+'x'), shifted)
            require(restored == text, 'Relocation changed framing or non-address data')
            target = out/'cdatafile'/source.name
            rows[name] = dict(port_id=port['id'], bundle=bundle, depth=port['depth'], payload_bytes=port['payload_bytes'],
                              source=str(source), source_sha256=sha, relocated=str(target),
                              original_address=region['start'], relocated_address=region['start']+OFFSET,
                              readonly=region['readonly'], _text=shifted)
            files[str(source)] = sha
        model = TRIAL/'sim/verilog'/('AESL_axi_master_'+bundle+'.v')
        require(digest(model) == diagnosis['files'][str(model)], 'Original AXI model changed')
        files[str(model)] = digest(model)
        groups.append(dict(bundle=bundle, original_model=str(model),
                           region_names=[r['name'] for r in group['regions']],
                           required_future_mapping='AXI physical address minus4096 at memory-model boundary; preserve original payload index, depth,4pages, output format and RO guards'))
    require(set(rows) == set(ports), 'Missing pointer')
    out.mkdir(); (out/'cdatafile').mkdir()
    for row in rows.values():
        target = Path(row['relocated']); target.write_text(row.pop('_text'))
        files[str(target)] = digest(target)
    files[str(Path(__file__).resolve())] = digest(__file__)
    result = dict(status='full44_nonzero_pointer_vectors_prepared_only', offset_bytes=OFFSET, transactions=4,
                  pointers=44, models=30, pointer_vectors=rows, model_mapping_requirements=groups, files=files,
                  dut_modified=False, models_modified=False, execution_entry_prepared=False, rtl_executed=False,
                  prerequisites_remaining=['Implement and independently verify the AXI address adapter, including boundary/unknown/RO rejection and all30 original memory models.',
                                           'Check original RTL/ROM unchanged and all44 port depths/4pages/C payload files and original oracle retained.',
                                           'New isolated full4tx native RTL trial and original C postcheck plus four full snapshot comparisons; no reuse of the failed acceptance status.',
                                           'Rebind downstream typed prerequisites only to actually accepted new-version evidence.'],
                  limits=['Prepared vectors alone cannot run against the original zero-based models.',
                          'No failed report or active process modified, no large compile launched, no startup memory gate reinstated.'])
    with report.open('x') as f: json.dump(result, f, indent=2); f.write('\n')
    print(result['status'], len(rows), len(groups))


if __name__ == '__main__':
    main()
