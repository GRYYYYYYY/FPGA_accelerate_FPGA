"""Replace preparation-only hex snapshots by exact per-bit four-state records."""
from pathlib import Path
import hashlib
import json
from prepare_config_publication_unit_benches_v1 import instrument

ROOT=Path(__file__).resolve().parents[1]
TARGET=ROOT/'hardware/tests/config_native_publication_units_v2'
OLD='"BANK %0d %0t %h %h"'
NEW='"BANK %0d %0t %b %b"'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    report=ROOT/'results/config_publication_unit_benches_v2_preparation_20261030.json'
    old_report=ROOT/'results/config_publication_unit_benches_preparation_20261030.json'
    previous=json.loads(old_report.read_text())
    assert previous['status']=='five_observation_unit_benches_prepared_not_compiled_or_simulated'
    for path,digest in previous['bound'].items():
        assert sha(path)==digest
    prepared={};cases={}
    for name,case in previous['cases'].items():
        old=Path(case['testbench']);source=Path(case['source'])
        assert sha(old)==case['testbench_sha256'] and sha(source)==case['source_sha256']
        native=name.startswith('native_');mode=name.split('_',1)[1]
        rebuilt,top=instrument(source.read_text(),native,mode)
        assert rebuilt==old.read_text() and rebuilt.count(OLD)==1
        text=rebuilt.replace(OLD,NEW)
        assert text.replace(NEW,OLD)==rebuilt
        prepared[name]=text;cases[name]=dict(case)
    assert not TARGET.exists() and not report.exists();TARGET.mkdir()
    for name,text in prepared.items():
        path=TARGET/(name+'.sv');path.write_text(text)
        cases[name].update(testbench=str(path),testbench_sha256=sha(path))
    # Widths follow the complete concatenations, including every output port.
    state_bits=sum([3,1,1,4,32,32,32,2304,1,2304,64,32])
    output_bits=sum([1,1,1,64,32,32,32,2304,2304,1,1,1,1,6,2304,6,1,4,32,1,1,6,6,64,32])
    assert state_bits==4810 and output_bits==7238
    # A single hexadecimal X/Z digit cannot preserve each partly-known bit.
    binary_negative_controls=[['000x','010x'],['00z0','01z0']]
    assert all(left!=right for left,right in binary_negative_controls)
    bound=[Path(__file__).resolve(),ROOT/'scripts/prepare_config_publication_unit_benches_v1.py',old_report]
    bound += [Path(c['testbench']) for c in previous['cases'].values()]
    bound += [Path(c['source']) for c in previous['cases'].values()]
    report.write_text(json.dumps(dict(status='five_binary_four_state_unit_benches_prepared_not_compiled_or_simulated',
        bound={str(p):sha(p) for p in dict.fromkeys(bound)},cases=cases,
        exact_comparisons=previous['exact_comparisons'],state_bits=state_bits,output_bits=output_bits,
        binary_distinction_examples=binary_negative_controls,
        supersedes_for_cycle_comparison=str(old_report),v1_sources_preserved=True,
        original_stimulus_unchanged=True,production_candidate_generated=False,new_solver_started=False,
        trace_contract='BANK cycle time plus4810 internal-state bits and7238 output bits printed with%b. Every bit preserves0/1/X/Z; exact full-line/cycle equality required. Sample100ps after NBA, before original tick #1. v1 hex copies must not be used as complete mixed-four-state evidence.',
        scope='Verification-only copies and static width/source checks, not SV compile, actual formatter observation, simulation, candidate equivalence or timing benefit. Candidate generation remains gated on actual restored generic/native probes.'),indent=2,sort_keys=True)+'\n')
    print('CONFIG_PUBLICATION_BINARY_UNIT_BENCHES_PREPARED',len(cases),state_bits,output_bits,'NO_RTL_RUN')


if __name__=='__main__':
    main()
