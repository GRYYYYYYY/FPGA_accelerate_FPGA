import json
from pathlib import Path
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from experiment_status import collect,workflow

class StatusTests(unittest.TestCase):
    def test_successful_elaboration_does_not_hide_failed_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'local'
            for folder,status,stage in [
                ('compressed_batch_compact_rtl_guarded_v1','prepared','elaborated_rtl_execution_pending'),
                ('compressed_batch_compact_rtl_guarded_execution_v1','failed','postcheck'),
                ('compressed_batch_compact_guarded_final_audit_v1','failed','wait_existing_execution'),
            ]:
                path=base/folder;path.mkdir(parents=True)
                (path/'state.json').write_text(json.dumps(dict(status=status,stage=stage,owner_pid=123)))
            tasks={r['task']:r for r in collect(root,base,root/'proc')['tasks']}
            self.assertEqual(tasks['compact_batch']['status'],'prepared')
            self.assertEqual(tasks['compact_batch_execution']['status'],'failed')
            self.assertEqual(tasks['compact_batch_final_audit']['status'],'failed')

    def test_existing_foreign_pid_does_not_prove_original_owner_live(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);state=root/'job';state.mkdir();proc=root/'proc/123';proc.mkdir(parents=True)
            (state/'state.json').write_text(json.dumps(dict(status='running',stage='elaborate',owner_pid=123)))
            (proc/'stat').write_text('123 (foreign) '+' '.join(['S']+['0']*18+['99']+['0']*4))
            (proc/'cmdline').write_bytes(b'python3\0foreign.py\0')
            result=workflow('original',state,'expected_original.py',root/'proc')
            self.assertFalse(result['owner_verified'])
            self.assertEqual(result['status'],'owner_missing_or_mismatched_no_terminal_receipt')

    def test_resource_abort_sidecar_overrides_historical_running(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);incident=root/'data/derived/bus64_physical_resource_abort_20261025_v1';incident.mkdir(parents=True)
            (incident/'terminal.json').write_text(json.dumps(dict(physical_pid=1924562)))
            result=collect(root,root/'local',root/'proc')
            row=next(r for r in result['tasks'] if r['task']=='integrated_physical_original')
            self.assertEqual(row['status'],'resource_aborted')
            self.assertFalse(row['pid_currently_exists'])
            self.assertFalse(result['completion_proven'])

    def test_stopped_compiler_is_reported_while_python_owner_waits(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);base=root/'local';job=base/'compressed_batch_compact_rtl_guarded_v1';job.mkdir(parents=True)
            (job/'state.json').write_text(json.dumps(dict(status='running',stage='elaborate',owner_pid=123)))
            for pid,mode,command in [(123,'S','python3 scripts/run_compressed_batch_compact_rtl_guarded.py '),(456,'T','xelab full_top ')]:
                proc=root/'proc'/str(pid);proc.mkdir(parents=True)
                (proc/'stat').write_text(str(pid)+' (test) '+' '.join([mode]+['0']*18+['99']+['0']*4))
                (proc/'cmdline').write_bytes(command.replace(' ','\0').encode())
            controller=root/'data/derived/compact_rtl_memory_serialization_20261025_v1';controller.mkdir(parents=True)
            (controller/'state.json').write_text(json.dumps(dict(status='running',stage='waiting',owner_pid=789,target=dict(pid=456,start_ticks='99',command='xelab full_top '))))
            result=collect(root,base,root/'proc')
            row=next(r for r in result['tasks'] if r['task']=='compact_batch')
            self.assertTrue(row['compiler_identity_verified'])
            self.assertEqual(row['status'],'process_suspended')

if __name__=='__main__':unittest.main()
