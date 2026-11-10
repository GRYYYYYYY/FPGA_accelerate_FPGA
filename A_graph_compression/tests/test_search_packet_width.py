"""Reject missing/malformed RTL width declarations; no hardware result claim."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_search_packet_width import rtl_input_width
class Width(unittest.TestCase):
    def test_actual_parameter_format(self):
        self.assertEqual(rtl_input_width('parameter    C_M_AXI_INPUT_MEM_DATA_WIDTH = 512;'),512)
        self.assertEqual(rtl_input_width('parameter C_M_AXI_INPUT_MEM_DATA_WIDTH=64;'),64)
        for t in ['parameter C_M_AXI_INPUT_MEM_DATA_WIDTH=64; parameter C_M_AXI_INPUT_MEM_DATA_WIDTH=512;', '', 'input [63:0] m_axi_input_mem_RDATA;', 'parameter C_M_AXI_INPUT_MEM_DATA_WIDTH = x;']:
            with self.assertRaises(ValueError):rtl_input_width(t)
if __name__=='__main__':unittest.main()
