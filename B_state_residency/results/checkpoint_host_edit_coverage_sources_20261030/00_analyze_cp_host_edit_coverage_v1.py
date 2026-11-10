"""Locate the host-edit coverage gap in restored full-system stimuli."""
from pathlib import Path
import hashlib
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]
BASE = Path('/tmp/B_state_residency_offer_20261025')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def classify_tb(text):
    tasks = list(re.finditer(r'\btask\s+label_write\b.*?endtask', text, re.S))
    assert len(tasks) == 1
    body = tasks[0].group(0)
    outside = text[:tasks[0].start()] + text[tasks[0].end():]
    assert len(re.findall(r'\blabel_write\b', text)) == 1
    assert not re.search(r'\blabel_write\b', outside)
    assert re.findall(r'\bhost_io_write\s*(?:<=|=)\s*([^;]+);', body) == ['1']
    assert re.findall(r'\bhost_io_write\s*(?:<=|=)\s*([^;]+);', outside) == ['0', '0']
    assert not re.search(r'\b(force|release)\s+[\w.]*host_io_write\b', text)
    for expression in [
        'assign f_sv[8]=host_io_valid;assign host_io_ready=f_sr[8];',
        'assign f_sp[19456+:1]=host_io_write;',
        'host_io_valid=1;host_io_node=n;host_io_field=field;host_io_write=1;host_io_value=value;',
        'do @(posedge clk);while(!host_io_ready);',
    ]:
        assert expression in text, expression
    return dict(label_write_declarations=1, label_write_calls=0,
        host_io_write_assignments_outside_unused_task=['0', '0'],
        high_assignment_only_in_unused_task=True,
        task_sha256=hashlib.sha256(body.encode()).hexdigest())


def main():
    prefile = ROOT / 'results/checkpoint_edit_matrix_preflight_20261030.json'
    pre = json.loads(prefile.read_text()); assert len(pre['cases']) == 7
    bound = [Path(__file__).resolve(), prefile]
    stimuli = []
    references = [Path(c['reference']) for c in pre['cases']]
    references.append(BASE / 'checkpoint_edit_system_crc_pressure_v1')
    for ref in references:
        mfile = ref / 'manifest.json'; afile = ref / 'source_bound_audit.json'
        receipt = ROOT / 'results' / f'{ref.name}_restore_20261025.json'
        m = json.loads(mfile.read_text()); a = json.loads(afile.read_text()); r = json.loads(receipt.read_text())
        assert m['status'] == 'observed' and a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
        assert a['manifest_sha256'] == sha(mfile) and r['audit_sha256'] == sha(afile)
        tb = ref / 'sources/tb_query_fault.sv'
        assert sha(tb) == m['sources']['tb_query_fault.sv']['sha256']
        item = classify_tb(tb.read_text())
        item.update(reference=str(ref), tb_sha256=sha(tb), audit_sha256=sha(afile), restore_sha256=sha(receipt))
        stimuli.append(item); bound.extend([mfile, afile, receipt, tb])
    physical = BASE / 'checkpoint_edit_route_recovery_v1'
    pmfile = physical / 'manifest.json'; pm = json.loads(pmfile.read_text())
    assert pm['status'] == 'observed' and pm['stage'] == 'complete'
    wrapper = physical / 'sources/query_residency_system.sv'
    controller = physical / 'sources/query_lifecycle.sv'
    for f in [wrapper, controller]:
        assert sha(f) == pm['inputs']['sources/' + f.name]
    requirements = {
        str(wrapper): [
            'wire host_base=!wm_owned&&!qc_busy&&!qc_fault&&!pc_owned&&!as_cfg_lease;',
            'assign f_sr=b_f_sr&host_mask;',
            '.host_label_edit(f_sv[8]&&f_sr[8]&&f_sp[19456])',
            'if(qc_cp_restore)qc_pending<=1;',
            'if(qc_import_held&&qc_cp_status==0)qc_pending<=0;',
        ],
        str(controller): [
            'if(sequence_seen&&!owned&&host_label_edit)label_state_dirty<=1;',
            '(label_state_dirty&&!cp_stage[7][7])',
            'sequence_seen<=cp_stage[7][6];label_state_dirty<=cp_stage[7][7];last_sequence<=cp_stage[8];',
            'cp_stage[7]<={24\'d0,label_state_dirty,sequence_seen,active_price,active_query};',
        ],
    }
    for filename, expressions in requirements.items():
        text = Path(filename).read_text()
        for expression in expressions:
            assert expression in text, expression
    bound.extend([pmfile, wrapper, controller])
    measured = []
    for name in ['checkpoint_edit_system_crc_pressure_v1', 'checkpoint_matrix_off_full_v1',
                 'checkpoint_matrix_off_pressure_v1', 'checkpoint_matrix_on_full_v1']:
        afile = BASE / name / 'source_bound_audit.json'
        rp = ROOT / 'results' / f'{name}_restore_20261025.json'
        a = json.loads(afile.read_text()); r = json.loads(rp.read_text())
        assert a['status'] == r['status'] == 'passed' and r['audit_byte_identical']
        assert r['audit_sha256'] == sha(afile)
        assert a['checkpoint_edit_exclusion']['edit'] == 0
        measured.append(dict(target=name, audit_sha256=sha(afile), restore_sha256=sha(rp),
            coverage=a['checkpoint_edit_exclusion']))
        bound.extend([afile, rp])
    out = ROOT / 'results/checkpoint_host_edit_coverage_20261030.json'
    freeze = ROOT / 'results/checkpoint_host_edit_coverage_sources_20261030'
    assert not out.exists() and not freeze.exists()
    bound = list(dict.fromkeys(bound))
    report = dict(status='restored_stimulus_gap_identified_not_new_functional_result',
        bound={str(f): sha(f) for f in bound}, source_expressions=requirements,
        reference_stimuli=stimuli, observed_cp_cases_at_analysis=measured,
        conclusion='The original full-system stimulus leaves host_io_write at zero: its only assignment to one is in an uncalled label_write task. This explains observed host-edit coverage zero; the native interface is not structurally tied off.',
        distinction='Controller/internal query label writes are not external host_label_edit. The native CP-safe/host-edit exclusion remains a separate wiring property, and the existing CP unit test has direct edit coverage.',
        proposed_real_port_extension=[
            'Use a separate copied fixture and target after the four real queries and final checkpoint export, with old stimuli preserved and the checkpoint lease released.',
            'Save the clean ten-word ledger and its independently checked CRC before editing; require last_sequence=180330 and the original context.',
            'Read the real source-node label through lane8, then call label_write on the sequence field with the same value. Require one actual accepted host write, balanced reply, cp_safe=0 and no simultaneous query ownership.',
            'Require label_state_dirty to become one without changing last_sequence or route slots; never force or directly assign DUT state.',
            'Acquire the real checkpoint lease, export the now-dirty ten-word ledger, and require only the dirty flag to differ from the saved clean image while sequence/context remain equal.',
            'Import the original clean ledger using its correct CRC and context. Observe CP_CHECK has no CRC/metadata/drift reason to fail except clearing an already-dirty flag; require status1 and unchanged live ledger.',
            'The failed import leaves qc_pending asserted. Import the correct dirty ledger, require success and pending clear while label_state_dirty stays one, then release the real lease.',
            'Compare a separately run reference and CP extension, including all AXI/DDR artifacts, new exact event cycles and nonempty edit coverage, before archive/actual restore/freeze.',
        ],
        pitfalls=['Do not inject host_label_edit directly or fabricate a pulse behind the real handshake.',
            'Do not claim new query rejection proves the dirty flag: all four route slots are occupied at this fixture endpoint, an independent rejection condition.',
            'Do not leave failed-import pending set and then call a host task that the wrapper correctly blocks.',
            'Same-value host writes still intentionally invalidate the ledger; this is not a no-op for authorization state.',
            'No existing eight-case result, fixture, runner, auditor or bound queue is changed.'],
        production_rtl_changed=False, new_testbench_created=False, new_solver_started=False,
        limits='Static classification of eight restored reference stimuli plus four already restored CP observations at analysis time. Remaining CP cases may still be running; no new edit scenario, full matrix completion or timing benefit is claimed.')
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    bound.append(out); freeze.mkdir(); files = {}
    for i, f in enumerate(bound):
        name = f'{i:02d}_{f.name}'; shutil.copyfile(f, freeze / name)
        files[name] = dict(source=str(f), sha256=sha(f)); assert sha(freeze / name) == files[name]['sha256']
    (freeze / 'manifest.json').write_text(json.dumps(dict(status='frozen', files=files,
        scope='Coverage gap and source-bound extension design, not simulation acceptance.'), indent=2, sort_keys=True) + '\n')
    print('HOST_EDIT_COVERAGE_GAP', len(stimuli), 'stimuli', len(measured), 'observed CP cases', len(files), 'frozen files')


if __name__ == '__main__':
    main()
