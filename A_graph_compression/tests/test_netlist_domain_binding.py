"""Independent evaluation must retain the original frozen training bank."""
from copy import deepcopy
from pathlib import Path
import sys
import unittest

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from netlist_experiment import domain_paths


class DomainBindingTests(unittest.TestCase):
    def setUp(self):
        self.cfg={'output_dir':'new_domain','training_bank_sha256':'bank'}
        self.capture={'scope_kind':'independent_endpoint_region','config_sha256':'new_config',
            'training_bank_sha256':'bank','training':{'path':'old_domain/training.tsv'},
            'graph':{'path':'new_domain/region.tsv'},'source_selection':{'path':'new_domain/roots.txt'}}
        self.bank={'bank_file_sha256':'bank','config_sha256':'original_config'}

    def test_independent_domain_uses_original_training_and_new_rows(self):
        paths=domain_paths(ROOT,self.cfg,self.capture,'new_config',self.bank,'bank')
        self.assertEqual(paths,(ROOT/'old_domain/training.tsv',ROOT/'new_domain/region.tsv',
                                ROOT/'new_domain/roots.txt',True))

    def test_config_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'capture/config'):
            domain_paths(ROOT,self.cfg,self.capture,'wrong_config',self.bank,'bank')

    def test_different_frozen_bank_rejected(self):
        capture=deepcopy(self.capture);capture['training_bank_sha256']='another_bank'
        with self.assertRaisesRegex(ValueError,'different frozen bank'):
            domain_paths(ROOT,self.cfg,capture,'new_config',self.bank,'bank')

    def test_original_domain_still_requires_original_config(self):
        with self.assertRaisesRegex(ValueError,'bank/config'):
            domain_paths(ROOT,self.cfg,{},'new_config',self.bank,'bank')


if __name__=='__main__':unittest.main()
