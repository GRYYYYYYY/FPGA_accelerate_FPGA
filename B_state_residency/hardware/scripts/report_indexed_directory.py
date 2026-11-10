"""Final integrity audit for standalone indexed directory RTL evidence."""
from pathlib import Path
import json
import re
import sys
from make_indexed_directory import generate
from report_codec_timing import digest, require, summary

ROOT = Path(__file__).resolve().parents[2]


def resource_counts(path):
    text = path.read_text()
    result = {}
    # Use the FIRST top-level resource table, not the later unmapped SLR table.
    for label in ['CLB LUTs', 'CLB Registers', 'Register as Latch', 'Block RAM Tile', 'RAMB36/FIFO', 'RAMB18', 'DSPs']:
        match = re.search(r'^\|\s*' + re.escape(label) + r'\*?\s*\|\s*([\d.]+)\s*\|', text, re.M)
        require(match is not None, 'Missing resource: ' + label)
        result[label] = float(match[1])
    return result


def main():
    out = Path(sys.argv[1]).resolve()
    sim = json.loads((out / 'manifest.json').read_text())
    require(sim['status'] == 'passed', 'Simulation incomplete')
    require(digest(out / 'manifest.json') == json.loads((out / 'completion_audit.json').read_text())['manifest_sha256'], 'Simulation manifest changed')
    for name, expected in sim['sources'].items():
        require(digest(ROOT / name) == expected, 'Changed live source: ' + name)
        require(digest(out / 'sources' / Path(name).name) == expected, 'Changed frozen source: ' + name)
    for name, expected in sim['artifacts'].items():
        require(digest(out / name) == expected, 'Changed simulation artifact: ' + name)
    parent_path = ROOT / 'results/rtl_memory_endpoint_20261023/manifest.json'
    require(digest(parent_path) == '6c22b2762a8e22dbfeb940ac41727c65aa2caf2e5f68e1c0a0061380535ecccb', 'Changed parent endpoint manifest')
    parent = json.loads(parent_path.read_text())
    old = ROOT / 'hardware/rtl/backing_frame_directory_lookup.sv'
    require(digest(old) == parent['files'][str(old)], 'Changed frozen linear baseline')
    require(generate(old.read_text()) == (out / 'sources/backing_frame_directory_indexed.sv').read_text(), 'Non-mechanical baseline changes')
    vectors = Path(sim['vector_manifest']['path'])
    require(digest(vectors) == sim['vector_manifest']['sha256'], 'Vector manifest changed')
    vm = json.loads(vectors.read_text())
    for name, expected in vm['inputs'].items():
        require(digest(Path(name)) == expected, 'Vector provenance changed')
    for name, expected in vm['source'].items():
        require(digest(Path(name)) == expected, 'Vector oracle changed')
    for name, expected in vm['artifacts'].items():
        require(digest(vectors.parent / name) == expected, 'Changed vectors')
    for size, row in sim['cases'].items():
        require(row['status'] == 'passed' and all(c['exit_code'] == 0 for c in row['commands']), 'Simulation stage failed')
        log = (out / size / 'simulate.log').read_text()
        require(log.count('TEST_PASS indexed_directory ') == 1 and 'Fatal:' not in log and '$finish' in log, 'Simulation verdict invalid')
        require(row['counters']['checks'] == vm[size + '_commands'], 'Incomplete command coverage')
    require(sim['cases']['small']['counters']['wraps'] >= 2, 'Wrap guard untested')
    require(sim['cases']['large']['counters']['overflow'] > 0, 'No actual bounded overflow exercised')
    negative = json.loads((out / 'negative_guards/manifest.json').read_text())
    require(negative['status'] == 'passed' and len(negative['cases']) == 4, 'Negative controls incomplete')
    require(digest(out / 'negative_guards/manifest.json') == json.loads((out / 'negative_guards/completion_audit.json').read_text())['manifest_sha256'], 'Negative manifest changed')
    require(negative['parent_manifest_sha256'] == digest(out / 'manifest.json'), 'Negative parent changed')
    for name, expected in negative['source'].items():
        require(digest(Path(name)) == expected, 'Negative driver changed')
    for name, row in negative['cases'].items():
        require(row['status'] == 'detected' and all(c['exit_code'] == 0 for c in row['commands'][:2]), 'Invalid negative control')
        for filename, expected in row['artifacts'].items():
            require(digest(out / 'negative_guards' / name / filename) == expected, 'Changed negative evidence')
        log = (out / 'negative_guards' / name / 'simulate.log').read_text()
        require(row['first_failure'] in log and 'TEST_PASS' not in log, 'Negative verdict absent')
    synthesis = out / 'synthesis'
    completion = json.loads((synthesis / 'completion.json').read_text())
    require(completion['exit_code'] == 0, 'Synthesis source failed')
    script = Path(completion['source'])
    require(digest(script) == completion['source_sha256'] == digest(synthesis / script.name), 'Synthesis script changed')
    log = (synthesis / 'synthesis_session.log').read_text()
    require(log.count('\nB_INDEXED_SYNTH_DONE\n') == 1 and not re.search(r'^ERROR:', log, re.M), 'Synthesis did not finish')
    require(completion['LD_PRELOAD'] == '/lib/x86_64-linux-gnu/libc.so.6' and digest(Path(completion['LD_PRELOAD'])) == completion['libc_sha256'], 'Changed allocator environment')
    resources = {}; timings = {}
    for variant in ['lookup', 'indexed']:
        require((synthesis / (variant + '.dcp')).stat().st_size > 10000, 'Missing checkpoint')
        resources[variant] = resource_counts(synthesis / (variant + '_utilization.rpt'))
        timings[variant] = summary(synthesis / (variant + '_timing.rpt'))
        require(resources[variant]['Register as Latch'] == 0 and resources[variant]['RAMB36/FIFO'] > 0, 'Memory implementation unsuitable')
    # Explicit resource witness catches parsing of the zero-filled SLR section.
    require(resources['lookup']['CLB Registers'] == 500 and resources['indexed']['CLB Registers'] == 606, 'Wrong resource table')
    result = {'status': 'passed', 'scope': 'Standalone directory RTL semantics and synthesis; not endpoint integration, routed timing, full trace, or board acceleration.',
              'resources': resources, 'resource_delta': {key: resources['indexed'][key] - resources['lookup'][key] for key in resources['lookup']},
              'prelayout_timing': timings, 'behavior': {key: row['counters'] for key, row in sim['cases'].items()},
              'large_reference_simulated': False, 'negative_controls': {key: row['first_failure'] for key, row in negative['cases'].items()},
              'board_performance': None, 'simulation_manifest_sha256': digest(out / 'manifest.json'),
              'negative_manifest_sha256': digest(out / 'negative_guards/manifest.json'),
              'vector_manifest_sha256': digest(vectors), 'baseline_parent_sha256': digest(parent_path),
              'synthesis': completion, 'warnings': re.findall(r'^WARNING:.*$', log, re.M)}
    result['behavior']['large']['ref_cycles'] = None  # TB mirror is NOT a baseline measurement.
    scripts = [Path(__file__).resolve(), ROOT / 'hardware/scripts/report_codec_timing.py']
    result['audit_sources'] = {str(p): digest(p) for p in scripts}
    result['synthesis_artifacts'] = {p.name: digest(p) for p in synthesis.iterdir() if p.is_file()}
    (out / 'final_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
    audit = {'status': 'passed', 'manifest_sha256': digest(out / 'final_manifest.json')}
    (out / 'final_audit.json').write_text(json.dumps(audit, indent=2) + '\n')
    print(json.dumps(audit))
    print(json.dumps(resources))


if __name__ == '__main__':
    main()
