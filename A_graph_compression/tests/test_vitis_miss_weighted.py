import sys
from pathlib import Path
import struct
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from prepare_vitis_miss_weighted import weighted_nodes,validate_case,encode_case

class MissWeightedTests(unittest.TestCase):
    def test_zero_weights_and_reproducibility(self):
        nodes=weighted_nodes([0,1,0,3,0],10000,42)
        self.assertEqual(nodes,weighted_nodes([0,1,0,3,0],10000,42))
        self.assertEqual(set(nodes),{1,3})
        self.assertTrue(7200<nodes.count(3)<7800)
        self.assertEqual(weighted_nodes([0,9,0],12,0),[1]*12)
    def test_bad_weights(self):
        for weights,count in [([],1),([0,0],1),([-1,2],1),([1.5],1),([True],1),([1],0)]:
            with self.assertRaises(Exception):weighted_nodes(weights,count,0)
    def test_duplicate_payload_and_mutations(self):
        rows={1:(0,1,struct.pack('<8I',1,2,3,4,5,6,7,0)),2:(0,0,b'')}
        nodes=[1,1,2,1];data=encode_case(rows,nodes)
        validate_case(data,rows,nodes)
        for offset in [0,4,8,12,16,32,36,40,80]:
            changed=bytearray(data);changed[offset]^=1
            with self.assertRaises(Exception):validate_case(changed,rows,nodes)
        for changed in [data[:-1],data+b'\0',data[:8]]:
            with self.assertRaises(Exception):validate_case(changed,rows,nodes)
        with self.assertRaises(Exception):validate_case(data,rows,[1,2,1,1])

if __name__=='__main__':unittest.main()
