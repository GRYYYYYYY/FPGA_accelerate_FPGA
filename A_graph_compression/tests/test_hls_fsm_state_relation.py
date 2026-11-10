import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_hls_fsm_state_relation_v1 import check_pair
from transform_hls_fsm_binary_v1 import transform
from test_hls_fsm_shape import FIXTURE


class StateRelationTests(unittest.TestCase):
    def test_exhaustive_small_state_domain(self):
        candidate,_ = transform(FIXTURE)
        result = check_pair(FIXTURE,candidate)
        self.assertEqual(result['states'],2)
        self.assertEqual(result['decoder_state_pairs_checked'],4)
        self.assertEqual(result['named_transition_assignments_checked'],3)

    def test_codebook_predicate_transition_and_reset_corruption_rejected(self):
        candidate,_ = transform(FIXTURE)
        mutations = {
            'aliased_state': candidate.replace("state2 = 1'd1", "state2 = 1'd0"),
            'wrong_predicate': candidate.replace("state1 = (ap_CS_fsm == 1'd0)", "state1 = (ap_CS_fsm == 1'd1)"),
            'unknown_transition': candidate.replace('ap_NS_fsm = ap_ST_fsm_state2;', 'ap_NS_fsm = ap_ST_fsm_state3;'),
            'changed_condition': candidate.replace("go == 1'b1", "go != 1'b0"),
            'lost_unknown_default': candidate.replace("ap_NS_fsm = 'bx;", 'ap_NS_fsm = ap_ST_fsm_state1;'),
            'wrong_reset': candidate.replace('ap_CS_fsm <= ap_ST_fsm_state1;', 'ap_CS_fsm <= ap_ST_fsm_state2;'),
            'wrong_initial': candidate.replace("#0 ap_CS_fsm = 1'd0;", "#0 ap_CS_fsm = 1'd1;"),
        }
        for name,text in mutations.items():
            with self.subTest(name=name),self.assertRaises(ValueError):
                check_pair(FIXTURE,text)


if __name__=='__main__':
    unittest.main()
