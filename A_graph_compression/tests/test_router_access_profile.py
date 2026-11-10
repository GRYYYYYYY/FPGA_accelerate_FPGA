import copy
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_router_access_profile import read_profile,image_degrees


class AccessProfileAuditTests(unittest.TestCase):
    def setUp(self):
        self.directory=tempfile.TemporaryDirectory();self.addCleanup(self.directory.cleanup)
        self.path=Path(self.directory.name)/'profile.tsv'
        self.degrees=[0,4,-1,642,8]
        self.rows=[[0,2,1,1,0,0],[1,5,3,2,0,4],[2,3,0,0,3,-1],[3,1,0,1,0,642],[4,0,0,0,0,-2]]

    def write(self,rows,header='ROUTER_ACCESS_V1\t5\t0',extra=''):
        self.path.write_text(header+'\n'+''.join('\t'.join(map(str,row))+'\n' for row in rows)+extra)

    def check(self):return read_profile(self.path,self.degrees,0,4,4,8)

    def test_valid_counts(self):
        self.write(self.rows);p=self.check()
        self.assertEqual(p['totals'],{'visits':11,'hits':4,'misses':4,'unknown':3,'visited_nodes':4,'edges_returned':662,'edges_decoded_on_misses':650})
        self.assertEqual(p['top_nodes_by_visits'][0]['node'],1)
        self.assertEqual(p['strata']['degree_5_8']['visited_nodes'],0)

    def test_corruption_rejected(self):
        mutations=[(0,0,1),(0,1,-1),(0,1,2**64),(0,2,-1),(0,3,0),(0,5,1),
                   (1,1,4),(1,4,1),(2,2,1),(2,5,0),(3,5,641),(4,5,8),
                   (1,1,'5.0')]
        for row,column,value in mutations:
            with self.subTest(row=row,column=column,value=value):
                rows=copy.deepcopy(self.rows);rows[row][column]=value;self.write(rows)
                with self.assertRaises((ValueError,AssertionError)):self.check()
        for rows,header,extra in [(self.rows[:-1],'ROUTER_ACCESS_V1\t5\t0',''),
                                 (self.rows,'ROUTER_ACCESS_V1\t5\t1',''),
                                 (self.rows,'ROUTER_ACCESS_V1\t5\t0','extra\n')]:
            self.write(rows,header,extra)
            with self.assertRaises((ValueError,AssertionError)):self.check()
        self.write(self.rows)
        with self.assertRaises((ValueError,AssertionError)):read_profile(self.path,self.degrees,0,3,4,8)
        with self.assertRaises((ValueError,AssertionError)):read_profile(self.path,self.degrees,0,4,4,9)

    def test_actual_image_degree_domain(self):
        degrees=image_degrees(ROOT/'data/derived/region_all_nets_cap8_20261022_v1/compact.agr')
        self.assertEqual(len(degrees),274732)
        self.assertEqual(degrees.count(-1),53759)
        self.assertEqual(sum(max(d,0) for d in degrees),1100754)
        self.assertEqual(max(degrees),642)


if __name__=='__main__':unittest.main()
