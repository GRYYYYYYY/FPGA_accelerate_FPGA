"""Native/Python negotiated site conflicts and incremental penalties."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from site_netlist_routing import DemandLedger
from site_search import EMPTY,merge_demands


@unittest.skipUnless(shutil.which('g++'),'g++ required')
class NativeSiteLedgerTests(unittest.TestCase):
    def test_all_conflict_kinds_masked_compatibility_and_incremental_cost(self):
        def demands(signals,bits,values):
            return merge_demands(EMPTY,{'signal_resources':['r'+str(r) for r in signals],
                'configuration_bits':[('r'+str(r),m,v) for r,m,v in bits],
                'configuration_values':[('r'+str(r),v) for r,v in values]})
        actions=[
            (False,1,demands([1],[(0,1,0)],[(0,7)])),
            (False,2,demands([1],[(0,1,0)],[(0,7)])),
            (False,2,demands([2],[(0,1,1)],[(0,8)])),
            (False,3,demands([],[(0,0,0)],[(0,7)])),
            (False,1,demands([1],[(0,3,0)],[(0,7)])),
            (True,2,EMPTY),(True,1,EMPTY),(True,3,EMPTY)]
        ledger=DemandLedger();history={(0,'r1'):3,(1,'r0'):5,(2,'r0'):7}
        probe=demands([1],[(0,3,1)],[(0,8)]);before=demands([1],[(0,1,1)],[]);expected=[]
        for release,owner,requirement in actions:
            if release:ledger.release(owner)
            else:ledger.replace(owner,requirement)
            expected.append({'conflicts':[[key[0],int(key[1][1:]),users] for key,users in sorted(ledger.conflicts().items())],
                'penalties':[ledger.penalty(4,EMPTY,probe,2,history),ledger.penalty(4,before,probe,2,history),
                             ledger.penalty(4,probe,probe,2,history),ledger.penalty(1,EMPTY,probe,2,history)]})
        with tempfile.TemporaryDirectory() as tmp:
            binary=Path(tmp)/'ledger'
            subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                str(ROOT/'tests/native_site_ledger_driver.cpp'),'-o',str(binary)],check=True)
            actual=subprocess.run([str(binary)],text=True,capture_output=True,check=True)
        self.assertEqual(json.loads(actual.stdout),expected)
        self.assertEqual(expected[1]['conflicts'],[[0,1,[1,2]]])
        self.assertEqual(expected[3]['conflicts'],[[1,0,[1,2]],[2,0,[1,2,3]]])
        self.assertTrue(all(r['penalties'][2]==0 for r in expected))
        self.assertFalse(expected[-1]['conflicts'])


if __name__=='__main__':unittest.main()
