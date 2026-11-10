import unittest
from site_resources import SiteResources, ConfigurationBits, SiteState
from lut_equation import truth_table


class SiteResourceTests(unittest.TestCase):
    def test_joint_transaction_is_atomic(self):
        s=SiteState(fixed_values=[('clock/CE_TYPE','ASYNC')])
        original={'signal_resources':['site/O'],'configuration_bits':[('INIT',3,1)],
                  'configuration_values':[('mux','D6')]}
        s.replace('a',original)
        s.replace('b',{'configuration_bits':[('INIT',1,1)]})
        with self.assertRaises(ValueError):
            s.replace('a',{'signal_resources':['other/O'],'configuration_bits':[('INIT',1,0)]})
        self.assertEqual(s.signals.by_net['a'],{'site/O':0})
        self.assertEqual(s.bits.by_net['a'],{'INIT':(3,1)})
        self.assertEqual(s.values['a'],{'mux':'D6'})
        with self.assertRaises(ValueError):
            s.replace('a',{'configuration_values':[('clock/CE_TYPE','SYNC')]})
        s.release('a');self.assertNotIn('a',s.bits.by_net)

    def test_same_mux_setting_can_share_but_output_cannot(self):
        s=SiteState();s.replace('a',{'signal_resources':['site/O'],'configuration_values':[('mux','D6')]})
        s.replace('b',{'configuration_values':[('mux','D6')]})
        self.assertTrue(s.conflicts('b',{'signal_resources':['site/O']}))
        self.assertTrue(s.conflicts('b',{'configuration_values':[('mux','D5')]}))

    def test_shared_lut_configuration_masks(self):
        s=ConfigurationBits()
        s.replace('lut6',[('site/LUT_INIT',0xff,0xa5)])
        s.replace('lut5',[('site/LUT_INIT',0x0f,0x05)])
        self.assertFalse(s.conflicts('other',[('site/LUT_INIT',0x100,0x100)]))
        self.assertTrue(s.conflicts('bad',[('site/LUT_INIT',0x0f,0x06)]))
        with self.assertRaises(ValueError):s.replace('bad',[('site/LUT_INIT',0x0f,0x06)])
        self.assertNotIn('bad',s.by_net)

    def test_fixed_configuration_and_atomic_replacement(self):
        s=ConfigurationBits([('site/INIT',3,1)])
        s.replace('a',[('site/INIT',4,4)])
        with self.assertRaises(ValueError):s.replace('a',[('site/INIT',3,2)])
        self.assertEqual(s.by_net['a'],{'site/INIT':(4,4)})
        s.release('a');self.assertEqual(s.by_net,{})

    def test_constant_configuration_without_cell_is_protected(self):
        s=SiteResources([('site/G6LUT','constant',truth_table('O6=0'))])
        self.assertTrue(s.conflicts('signal',[('site/G6LUT',truth_table('O6=A5'))]))
        with self.assertRaises(ValueError):s.replace('signal',[('site/G6LUT',truth_table('O6=A5'))])

    def test_same_equation_different_signal_cannot_share_output(self):
        s=SiteResources();s.replace('a',[('site/G6LUT',5)])
        self.assertTrue(s.conflicts('b',[('site/G6LUT',5)]))
        with self.assertRaises(ValueError):s.replace('b',[('site/G6LUT',5)])

    def test_physical_instances_and_atomic_reroute(self):
        s=SiteResources();s.replace('a',[('site0/G6LUT',5)])
        s.replace('b',[('site1/G6LUT',5)])
        with self.assertRaises(ValueError):s.replace('a',[('site1/G6LUT',6)])
        self.assertIn('a',s.dynamic['site0/G6LUT'])
        s.replace('a',[('site2/G6LUT',6)])
        self.assertNotIn('site0/G6LUT',s.dynamic)
        s.release('b');self.assertNotIn('site1/G6LUT',s.dynamic)

    def test_same_net_contradictory_configuration(self):
        s=SiteResources()
        with self.assertRaises(ValueError):s.replace('a',[('site/G6LUT',1),('site/G6LUT',2)])
        self.assertEqual(s.by_net,{})
