"""Strict numeric parsing, actual 64-bit payload retention, and unknown handling."""
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]

class NativeSiteInputsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory()
        cls.binary=Path(cls.tmp.name)/'inputs'
        subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror',
                        str(ROOT/'tests/native_site_inputs_driver.cpp'),'-o',str(cls.binary)],check=True)

    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()

    def test_actual_mode_payloads(self):
        converted=[]
        for mode in ('csr','compact'):
            folder=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1'
            symbols=json.loads((folder/'symbols.json').read_text())
            raw=subprocess.run([str(self.binary),str(folder/'sites.txt')],capture_output=True,text=True,check=True)
            actual=json.loads(raw.stdout)
            self.assertEqual(actual['resources'],len(symbols['resources']))
            self.assertEqual(actual['values'],len(symbols['values']))
            expected=sorted([[r['tile_id'],r['pip_id'],[r['signal_resources'],r['configuration_bits'],r['configuration_values']]]
                            for r in symbols['requirements'].values()])
            self.assertEqual(actual['requirements'],expected)
            self.assertEqual(len(actual['fixed'][1]),1100)
            self.assertTrue(any(mask==2**64-1 for _,mask,_ in actual['fixed'][1]))
            converted.append(actual['fixed'])
        self.assertEqual(*converted)

    def test_reject_malformed_payloads(self):
        # Valid small payload: one fixed mask, one tested pseudo PIP.
        good='NATIVE_SITES_V1 2 1 2 1 0 18446744073709551615 0 0 0 1 7 8 1 1 1 0 3 2 1 1 0 1 1'
        cases={
            'negative':good.replace('18446744073709551615','-1'),
            'overflow':good.replace('18446744073709551615','18446744073709551616'),
            'fraction':good.replace('18446744073709551615','1.0'),
            'id_overflow':good.replace('7 8','4294967296 8'),
            'bad_mask':good.replace('0 3 2','0 1 2'),
            'resource_domain':good.replace('7 8 1 1','7 8 1 2'),
            'value_domain':good.replace('1 1 0 1 1','1 1 1 1 1'),
            'pseudo_domain':good[:-1]+'2',
            'truncated':good.rsplit(' ',1)[0],
            'trailing':good+' junk',
            'schema':good.replace('V1','V2'),
        }
        path=Path(self.tmp.name)/'input.txt'
        path.write_text(good)
        subprocess.run([str(self.binary),str(path)],check=True,capture_output=True)
        for name,text in cases.items():
            with self.subTest(name=name):
                path.write_text(text)
                result=subprocess.run([str(self.binary),str(path)],capture_output=True,text=True)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(result.stdout)

if __name__=='__main__':unittest.main()
