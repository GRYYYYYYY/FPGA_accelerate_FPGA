import copy
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
import snapshot_read_serial_prerequisites_v2 as contract


class SerialScopeTests(unittest.TestCase):
    def test_full_tree_required(self):
        good=dict(status='production_route_tree_full_depth_50_transactions_rtl_verified',transactions=50,
                  capacities=dict(nodes=1048576,path_edges=524288,state_words=65),production_synthesis='unchanged',cycles=[1]*50)
        contract.tree_scope(good)
        for field,value in [('transactions',4),('cycles',[1]*49),('cycles',[1]*49+[0]),('production_synthesis','changed'),('capacities',dict(nodes=64,path_edges=32,state_words=65))]:
            with self.subTest(field=field),self.assertRaises(ValueError):contract.tree_scope({**good,field:value})

    def test_complete_current_snapshot_required(self):
        good=dict(status=contract.SNAPSHOT_STATUS,rtl_verified=True,transactions=30,pointers=13,models=10,pages=4,readonly_models=8,
                  original_address_environment_unchanged=True,resource_policy=contract.POLICY,cycles=[1]*30)
        contract.snapshot_scope(good)
        for field,value in [('transactions',2),('pointers',12),('models',9),('pages',1),('readonly_models',7),('cycles',[1]*29),('cycles',[1]*29+[False]),('rtl_verified',False),('resource_policy','old')]:
            with self.subTest(field=field),self.assertRaises(ValueError):contract.snapshot_scope({**good,field:value})

    def test_missing_changed_or_conflicting_evidence_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);report=root/'report.json';payload=root/'payload';payload.write_text('ok')
            with self.assertRaises(ValueError):contract.merge_report(report,{})
            report.write_text(json.dumps(dict(files={str(payload):contract.digest(payload)})))
            contract.merge_report(report,{})
            with self.assertRaises(ValueError):contract.merge_report(report,{str(payload):'0'*64})
            payload.write_text('changed')
            with self.assertRaises(ValueError):contract.merge_report(report,{})

    def test_missing_actual_native_refuses_both(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);(root/'results').mkdir()
            for function in [contract.validate_snapshot,contract.validate_read]:
                with self.assertRaisesRegex(ValueError,'prerequisite missing: collision_safe_recovered_native'):
                    function(root)


if __name__=='__main__':unittest.main()
