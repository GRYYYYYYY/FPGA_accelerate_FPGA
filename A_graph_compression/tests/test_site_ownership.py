import unittest
from site_ownership import resolve_owners


class SiteOwnershipTests(unittest.TestCase):
    def snapshot(self):
        return {'nets':{'n':{'segments':['n','child/n'],'type':'SIGNAL','nodes':['a'],'pips':[]},
                        'g':{'segments':['g'],'type':'GROUND','nodes':['z'],'pips':['p']},
                        'g_alias':{'segments':['g_alias'],'type':'GROUND','nodes':['z'],'pips':['p']}}}

    def test_alias_and_static_names(self):
        r=resolve_owners(self.snapshot(),['child/n','GLOBAL_LOGIC0'])
        self.assertEqual(r['child/n']['canonical_nets'],['n'])
        self.assertEqual(r['GLOBAL_LOGIC0']['canonical_nets'],['g','g_alias'])

    def test_placeholder_is_not_free(self):
        r=resolve_owners(self.snapshot(),['GLOBAL_USEDNET','unknown'])
        self.assertEqual(r['GLOBAL_USEDNET']['kind'],'unknown_occupied')
        self.assertEqual(r['unknown']['kind'],'unresolved')

    def test_inconsistent_static_aliases_rejected(self):
        s=self.snapshot();s['nets']['g_alias']['nodes']=['other']
        with self.assertRaises(ValueError):resolve_owners(s,['GLOBAL_LOGIC0'])
