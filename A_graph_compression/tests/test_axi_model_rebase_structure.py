import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_compact_nonzero_axi_models_v1 import wrap
from check_compact_nonzero_axi_models_v1 import audit_model


class RebaseStructure(unittest.TestCase):
    def test_full_real_model_and_corruptions(self):
        path = Path('/tmp/A_graph_compression_recovery_20261025_v1/compact_native_stack_recovery_v3/sim/verilog/AESL_axi_master_batch_input_mem.v')
        original = path.read_text(); candidate = wrap(original, 'batch_input_mem')
        self.assertEqual(audit_model(original, candidate, 'batch_input_mem')['address_translations'], 2)
        mutations = [
            candidate.replace("AWADDR - 64'd4096", "AWADDR - 64'd4095", 1),
            candidate.replace('.TRAN_batch_input_mem_WDATA(TRAN_batch_input_mem_WDATA)', '.TRAN_batch_input_mem_WDATA(0)', 1),
            candidate.replace('.FIFO_DEPTH(FIFO_DEPTH)', '.FIFO_DEPTH(1)', 1),
            candidate.replace('.awready(TRAN_batch_input_mem_AWREADY)', '.awready(0)', 1),
            candidate.replace('A_RO_WRITE_VIOLATION', 'silenced_readonly_failure', 1),
            candidate.replace("parameter batch_input_mem_mem_depth = 32'd 2;", "parameter batch_input_mem_mem_depth = 32'd 1;", 1),
            candidate.replace(') address_guard (', ') disconnected_guard (', 1),
            candidate+'\ninitial force original_model.write_processing = 0;\n',
        ]
        for damaged in mutations:
            self.assertNotEqual(candidate, damaged)
            with self.subTest(mutation=mutations.index(damaged)), self.assertRaises(ValueError):
                audit_model(original, damaged, 'batch_input_mem')


if __name__ == '__main__': unittest.main()
