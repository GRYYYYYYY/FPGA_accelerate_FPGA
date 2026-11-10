import copy
import hashlib
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from transform_hls_fsm_binary_v1 import transform
from check_hls_fsm_binary_v1 import check_delta
from test_hls_fsm_shape import FIXTURE


def replay(old, ledger):
    text = old
    for edit in reversed(ledger['edits']):
        text = text[:edit['start']]+edit['new']+text[edit['end']:]
    ledger['output_sha256'] = hashlib.sha256(text.encode()).hexdigest()
    return text


class BinaryMappingTests(unittest.TestCase):
    def test_complete_map_and_untouched_logic(self):
        new, ledger = transform(FIXTURE)
        result = check_delta(FIXTURE, new, ledger)
        self.assertEqual(result['states'], 2)
        self.assertEqual(result['candidate_width'], 1)
        self.assertIn("ap_NS_fsm = 'bx;", new)

    def test_semantically_wrong_but_hash_consistent_ledgers_rejected(self):
        new, ledger = transform(FIXTURE)
        for kind in ['state_constant', 'cs_width', 'ns_width', 'initial_state', 'state_decode']:
            with self.subTest(kind=kind):
                bad = copy.deepcopy(ledger)
                edit = next(e for e in bad['edits'] if e['kind']==kind)
                if kind=='state_decode':
                    edit['new'] = edit['new'].replace(' == ', ' === ')
                elif kind in ('cs_width','ns_width'):
                    edit['new'] = edit['new'].replace('[0:0]', '[1:0]')
                else:
                    edit['new'] = edit['new'].replace("1'd0", "1'd1")
                mutated = replay(FIXTURE, bad)
                with self.assertRaises(ValueError):
                    check_delta(FIXTURE, mutated, bad)

    def test_omitted_or_unlisted_modifications_rejected(self):
        new, ledger = transform(FIXTURE)
        missing = copy.deepcopy(ledger)
        missing['edits'].pop()
        with self.assertRaises(ValueError):
            check_delta(FIXTURE, replay(FIXTURE, missing), missing)
        changed = new.replace('posedge ap_clk', 'negedge ap_clk')
        ledger['output_sha256'] = hashlib.sha256(changed.encode()).hexdigest()
        with self.assertRaises(ValueError):
            check_delta(FIXTURE, changed, ledger)


if __name__=='__main__':
    unittest.main()
