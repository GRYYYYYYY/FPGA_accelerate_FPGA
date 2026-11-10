"""Rebuild the exact frozen bank before opening the evaluation graph in each compact worker."""
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[1]
sys.path[:0] = [str(ROOT/'src'), str(ROOT/'adapters')]
from import_vivado import read_export
from heldout import fit_bank, object_digest
from real_experiment import write_new
from check_vitis_kernel import digest, require

TRAINING_STAGES = {'training_load_ms', 'training_fit_ms', 'training_freeze_ms'}


def prepare_training(plan, mode, output, timed):
    require(plan.get('training_inclusive') is True, 'Missing training-inclusive protocol')
    if mode == 'csr':
        for name in sorted(TRAINING_STAGES):
            timed(name, None)
        return dict(applied=False, sources=0, templates=0, started_ns=0, fitted_ns=0, frozen_ns=0)
    require(mode == 'compact', 'Unknown representation')
    started = time.monotonic_ns()
    graph = timed('training_load_ms', lambda: read_export(plan['training_source']))
    bank = timed('training_fit_ms', lambda: fit_bank(graph))
    fitted = time.monotonic_ns()
    require(len(graph['roots']) == 3761 and len(bank['templates']) == 440, 'Different complete training scope')
    require(object_digest(bank) == plan['training_bank_object_sha256'], 'Rebuilt bank semantics changed')

    def freeze():
        write_new(output/'bank.json', bank)
        require(digest(output/'bank.json') == plan['training_bank_file_sha256'], 'Rebuilt bank bytes changed')
    timed('training_freeze_ms', freeze)
    return dict(applied=True, sources=3761, templates=440, started_ns=started, fitted_ns=fitted,
                frozen_ns=time.monotonic_ns(), source_sha256=digest(plan['training_source']),
                bank_sha256=digest(output/'bank.json'), bank_object_sha256=object_digest(bank))


def validate_training(plan, job, output, report):
    require(plan.get('training_inclusive') is True, 'Missing training-inclusive protocol')
    record = report['training']
    require(type(record['evaluation_read_start_ns']) is int and record['evaluation_read_start_ns'] > 0,
            'Missing evaluation-read ordering')
    if job['mode'] == 'csr':
        require(record == dict(applied=False, sources=0, templates=0, started_ns=0, fitted_ns=0,
                               frozen_ns=0, evaluation_read_start_ns=record['evaluation_read_start_ns']),
                'CSR incorrectly trained or charged')
        require(all(report['stage_ms'][k] == 0 for k in TRAINING_STAGES) and not (output/'bank.json').exists(),
                'CSR training must be unnecessary/zero')
        return
    require(job['mode'] == 'compact' and record['applied'] is True and record['sources'] == 3761 and
            record['templates'] == 440, 'Incomplete compact training')
    clocks = [record[k] for k in ['started_ns', 'fitted_ns', 'frozen_ns', 'evaluation_read_start_ns']]
    require(all(type(t) is int and t > 0 for t in clocks) and clocks == sorted(clocks), 'Training was not frozen before evaluation')
    require(all(report['stage_ms'][k] > 0 for k in TRAINING_STAGES), 'Missing measured training stage')
    require(record['source_sha256'] == plan['files'][plan['training_source']] == digest(plan['training_source']),
            'Changed training source')
    bank = output/'bank.json'
    require(record['bank_sha256'] == digest(bank) == plan['training_bank_file_sha256'], 'Changed consumed trained bank')
    require(record['bank_object_sha256'] == object_digest(json.loads(bank.read_text())) == plan['training_bank_object_sha256'],
            'Changed trained bank semantics')
    require(report['artifacts'].get('bank.json') == digest(bank), 'Trained bank not bound as consumed artifact')
