"""Reject incomplete/mislabelled physical captures and falsified XSim traces."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_clock_semantics_capture import parse, inspect
from run_clock_primitive_sim import audit_trace


class ClockEvidenceTests(unittest.TestCase):
    def test_real_physical_capture_and_rejections(self):
        folder=ROOT/'data/netlist/clock_semantics_capture_20261023_v3'
        baseline_text=(folder/'baseline.tsv').read_text();probe_text=(folder/'probe.tsv').read_text()
        baseline=parse(baseline_text,'baseline');probe=parse(probe_text,'probe')
        request=json.loads((ROOT/'results/clock_row_probe_input_20261023_v1.json').read_text())
        result=inspect(baseline,probe,request)
        self.assertEqual(len(result['connected_pins_reporting_is_used_zero']),4)
        for change in ('mislabel','missing_completion','missing_pin','duplicate_record'):
            text=probe_text
            if change=='mislabel':text=text.replace('meta\tstage\tprobe','meta\tstage\tbaseline')
            elif change=='missing_completion':text=text.replace('complete\tprobe\n','')
            elif change=='missing_pin':text='\n'.join(line for line in text.splitlines() if not line.startswith('bel_pin\tBUFCE_ROW_FSR_X21Y6/BUFCE/I\t'))+'\n'
            else:text=text.replace('complete\tprobe','site\tBUFCE_ROW_FSR_X21Y6\tBUFCE_ROW_FSR\ncomplete\tprobe')
            with self.subTest(change=change),self.assertRaises(ValueError):parse(text,'probe')
        for change in ('owner','unknown_constant','node','configuration'):
            bad=copy.deepcopy(probe)
            if change=='owner':next(iter(bad['net_link'].values()))[2]='wrong-net'
            elif change=='unknown_constant':next(iter(bad['net_link'].values()))[3]='POWER'
            elif change=='node':next(iter(bad['node_link'].values()))[2]='wrong-node'
            else:bad['config'][('BUFCE_ROW_FSR_X21Y6/BUFCE','CONFIG.CE_TYPE')][2]='SYNC'
            with self.subTest(change=change),self.assertRaises(ValueError):inspect(baseline,bad,request)

    def test_real_xsim_trace_and_rejections(self):
        trace=(ROOT/'data/derived/clock_primitive_sim_20261023_v1/stage_2.log').read_text()
        self.assertEqual(audit_trace(trace),{'parameter_cases':16,'behavioral_samples':192})
        samples=[line for line in trace.splitlines() if line.startswith('CLOCK_SAMPLE ')]
        for change in ('missing_pass','duplicate_sample','missing_sample','wrong_stimulus','forged_expected','fatal'):
            bad=trace
            if change=='missing_pass':bad=bad.replace('TEST_PASS clock_primitive_semantics cases=16 samples=192','')
            elif change=='duplicate_sample':bad+='\n'+samples[0]+'\n'
            elif change=='missing_sample':bad=bad.replace(samples[0]+'\n','')
            elif change=='wrong_stimulus':bad=bad.replace(samples[0],samples[0].replace(' i=0 ',' i=1 '))
            elif change=='forged_expected':bad=bad.replace(samples[0],samples[0].replace('expected=0 actual=0','expected=1 actual=1'))
            else:bad+='\nFatal: injected failure\n'
            with self.subTest(change=change),self.assertRaises(ValueError):audit_trace(bad)


if __name__=='__main__':unittest.main()
