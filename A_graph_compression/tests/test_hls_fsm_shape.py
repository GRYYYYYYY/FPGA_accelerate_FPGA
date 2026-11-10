import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_hls_fsm_shape_v3 import audit_module, ShapeError


FIXTURE = '''
parameter ap_ST_fsm_state1 = 2'd1;
parameter ap_ST_fsm_state2 = 2'd2;
(* fsm_encoding = "none" *) reg [1:0] ap_CS_fsm;
reg [1:0] ap_NS_fsm;
initial begin
#0 ap_CS_fsm = 2'd1;
end
assign ap_CS_fsm_state1 = ap_CS_fsm[32'd0];
assign ap_CS_fsm_state2 = ap_CS_fsm[32'd1];
always @ (posedge ap_clk) begin
    if (ap_rst == 1'b1) begin
        ap_CS_fsm <= ap_ST_fsm_state1;
    end else begin
        ap_CS_fsm <= ap_NS_fsm;
    end
end
always @ (*) begin
    case (ap_CS_fsm)
        ap_ST_fsm_state1 : begin
            if (go == 1'b1) begin
                ap_NS_fsm = ap_ST_fsm_state2;
            end else begin
                ap_NS_fsm = ap_ST_fsm_state1;
            end
        end
        ap_ST_fsm_state2 : begin
            ap_NS_fsm = ap_ST_fsm_state1;
        end
        default : begin
            ap_NS_fsm = 'bx;
        end
    endcase
end
'''


class StateShapeTests(unittest.TestCase):
    def test_known_initialization_and_total_transition_shapes(self):
        result = audit_module(FIXTURE)
        self.assertEqual(result['states'], 2)
        self.assertTrue(result['every_legal_state_branch_assigns_a_named_legal_next_state'])
        audit_module(FIXTURE.replace('if (ap_rst ==', 'if (ap_rst_n_inv =='))

    def test_reject_unsafe_or_unrecognized_shapes(self):
        mutations = {
            'wrong_codebook': FIXTURE.replace("state2 = 2'd2", "state2 = 2'd3"),
            'conditional_initialization': FIXTURE.replace('initial begin\n#0', 'initial begin\nif (go) begin\n#0').replace("= 2'd1;\nend", "= 2'd1;\nend\nend"),
            'wrong_decode': FIXTURE.replace("state1 = ap_CS_fsm[32'd0]", "state1 = ap_CS_fsm[32'd1]"),
            'missing_legal_case': FIXTURE.replace('ap_ST_fsm_state2 : begin\n            ap_NS_fsm = ap_ST_fsm_state1;\n        end', ''),
            'out_of_range_target': FIXTURE.replace('ap_NS_fsm = ap_ST_fsm_state2;', 'ap_NS_fsm = ap_ST_fsm_state3;'),
            'incomplete_transition': FIXTURE.replace('end else begin\n                ap_NS_fsm = ap_ST_fsm_state1;\n            end', 'end'),
            'changed_unknown_default': FIXTURE.replace("ap_NS_fsm = 'bx;", 'ap_NS_fsm = ap_ST_fsm_state1;'),
            'external_state_read': FIXTURE+'\nassign observation = |ap_CS_fsm;\n',
            'different_clock': FIXTURE.replace('posedge ap_clk', 'negedge ap_clk'),
        }
        for label, text in mutations.items():
            with self.subTest(label=label), self.assertRaises(ShapeError):
                audit_module(text)


if __name__ == '__main__':
    unittest.main()
