import pathlib,sys,tempfile,unittest
ROOT=pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_clock_connectivity import parse
class ClockConnectivityTests(unittest.TestCase):
    def test_observation_and_corruption(self):
        p=ROOT/'data/netlist/clock_connectivity_observation_20261023_v1/probe.tsv'
        text=p.read_text();self.assertEqual(len(parse(p,'probe')['observed_signal_pins']),4)
        alterations=[text.rsplit('complete\tprobe',1)[0],text.replace('SIGNAL','GND',1),
                     text.replace('net_count\tbel_pin\tBUFCE_ROW_FSR_X21Y6/BUFCE/CE\t0','net_count\tbel_pin\tBUFCE_ROW_FSR_X21Y6/BUFCE/CE\t1'),
                     text.replace('IS_GND\t0','IS_GND\t1',1),
                     text.replace('context\tBUFCE_ROW_FSR_X21Y6\trestored\t\t','context\tBUFCE_ROW_FSR_X21Y6\trestored\tBUFCE_ROW_FSR\t'),
                     text.replace('inversion_getter\tBUFCE_ROW_FSR_X21Y6\tmanual\tBUFCE_ROW_FSR_X21Y6/IINV\t\n',
                                  'inversion_getter\tBUFCE_ROW_FSR_X21Y6\tmanual\tBUFCE_ROW_FSR_X21Y6/IINV\t0\n')]
        with tempfile.TemporaryDirectory() as tmp:
            bad=pathlib.Path(tmp)/'bad.tsv'
            for i,changed in enumerate(alterations):
                with self.subTest(mutation=i):
                    self.assertNotEqual(text,changed);bad.write_text(changed)
                    with self.assertRaises(ValueError):parse(bad,'probe')
if __name__=='__main__':unittest.main()
