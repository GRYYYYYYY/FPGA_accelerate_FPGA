"""Bounded routing cannot count partial success or arbitrary failure as capacity evidence."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from site_capacity_experiment import allocation_failure, check_success, design


class SiteCapacityTests(unittest.TestCase):
    def test_only_precise_allocation_failure_is_accepted(self):
        self.assertEqual(allocation_failure(1,'NATIVE_SITE_PROGRESS 0 256\nstd::bad_alloc\n'),'address_space_allocation_failed')
        for code,log in [(0,'std::bad_alloc\n'),(-9,''),(1,'bad fixture\n'),(1,'ERROR\nstd::bad_alloc\n')]:
            with self.subTest(code=code,log=log),self.assertRaises(ValueError):allocation_failure(code,log)

    def test_full_scope_and_all_semantics_are_required(self):
        job={'mode':'csr','execution':'direct'}
        ref={'routes':[{'net':i,'complete':True,'edges':[],'demands':[]} for i in range(1062)],
             'iterations':[{'unknown_sources':[42],'conflicts':[]}],'status':'routed'}
        raw={'execution':'direct','batches':[deepcopy(ref),deepcopy(ref)],'export_ms':[1,1]}
        self.assertEqual(check_success(raw,ref,job),'two_complete_batches_equivalent')
        for kind in ('missing_batch','wrong_round','wrong_edge','wrong_demand','wrong_mode','missing_net'):
            bad=deepcopy(raw)
            if kind=='missing_batch':bad['batches'].pop()
            elif kind=='wrong_round':bad['batches'][1]['iterations'][0]['unknown_sources']=[]
            elif kind=='wrong_edge':bad['batches'][0]['routes'][0]['edges']=[[1,2,3]]
            elif kind=='wrong_demand':bad['batches'][1]['routes'][0]['demands']=[7]
            elif kind=='wrong_mode':bad['execution']='expanded'
            else:bad['batches'][0]['routes'].pop()
            with self.subTest(kind=kind),self.assertRaises(ValueError):check_success(bad,ref,job)
        self.assertEqual(len(design()),6)
        self.assertEqual({(j['mode'],j['execution'],j['limit_mib']) for j in design()},
            {(m,e,b) for m,e in [('csr','direct'),('compact','direct'),('compact','expanded')] for b in (3072,4096)})


if __name__=='__main__':unittest.main()
