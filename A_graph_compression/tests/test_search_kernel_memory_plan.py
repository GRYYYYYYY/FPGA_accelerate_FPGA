"""Production ABI/capacity checks and intentionally invalid static layouts."""
import copy
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import search_kernel_memory_plan as p


class MemoryPlanTests(unittest.TestCase):
    def setUp(self):
        self.args = p.parse_source(p.SOURCE)
        self.maps = p.layouts(self.args)

    def test_actual_production_sizes_and_two_xmls(self):
        expected = {'image': 134217728, 'config': 128, 'roots': 4194304,
                    'packet': 33554432, 'heap': 3145728, 'slots': 8388608,
                    'records': 41943040, 'keys': 272629760, 'unknown_nodes': 131072,
                    'unknown_pips': 8806032, 'path': 16777216, 'meta': 16, 'result': 648}
        self.assertEqual({a['name']: a['payload_bytes'] for a in self.args if a['pointer']}, expected)
        self.assertEqual([(a['id'], a['name']) for a in self.args if not a['pointer']],
                         [(2, 'image_words'), (5, 'packet_words')])
        self.assertEqual(p.validate_xml(self.args, p.XMLS['csr']),
                         p.validate_xml(self.args, p.XMLS['compact']))
        for mapping in self.maps.values():
            plan = p.validate_layout(self.args, mapping)
            self.assertEqual(plan['total_payload_bytes'], sum(expected.values()))
            self.assertEqual(plan['total_requested_bytes'], sum(((n + 4095) // 4096) * 4096
                                                                for n in expected.values()))
            self.assertEqual(p.read_connectivity(p.connectivity(mapping)), mapping)

    def test_single_channel_rejects_production_keys(self):
        mapping = {a['name']: 'HBM[0]' for a in self.args if a['pointer']}
        with self.assertRaisesRegex(ValueError, 'BO exceeds group capacity: keys'):
            p.validate_layout(self.args, mapping, reserve_bytes=0)

    def test_two_shared_channels_fit_only_without_selected_reserve(self):
        mapping = {a['name']: 'HBM[0:1]' for a in self.args if a['pointer']}
        p.validate_layout(self.args, mapping, reserve_bytes=0)
        with self.assertRaisesRegex(ValueError, 'aggregate requests plus reserve'):
            p.validate_layout(self.args, mapping)

    def test_aggregate_overflow_with_every_individual_bo_fitting(self):
        args = [dict(id=i, name=f'b{i}', pointer=True, bundle=f'm{i}', payload_bytes=200 * p.MIB)
                for i in range(3)]
        with self.assertRaisesRegex(ValueError, 'aggregate requests plus reserve'):
            p.validate_layout(args, {a['name']: 'HBM[0:1]' for a in args}, reserve_bytes=0)

    def test_overlap_disallowed(self):
        for group in ('HBM[3:4]', 'HBM[0:1]', 'HBM[0:0]'):
            mapping = dict(self.maps['hbm_shared'])
            mapping['image'] = group
            with self.subTest(group=group), self.assertRaisesRegex(ValueError, 'overlapping memory groups'):
                p.validate_layout(self.args, mapping)

    def test_shared_bundle_requires_identical_mapping(self):
        mapping = dict(self.maps['hbm_split'])
        mapping['roots'] = 'HBM[8]'
        with self.assertRaisesRegex(ValueError, 'shared AXI bundle'):
            p.validate_layout(self.args, mapping)

    def test_missing_extra_scalar_mappings(self):
        for change in ('missing', 'extra', 'scalar'):
            mapping = dict(self.maps['ddr_shared'])
            if change == 'missing':
                del mapping['keys']
            else:
                mapping['requests' if change == 'extra' else 'image_words'] = 'DDR[0]'
            with self.subTest(change=change), self.assertRaisesRegex(ValueError, 'memory mapping'):
                p.validate_layout(self.args, mapping)

    def test_invalid_channels(self):
        for group in ('HBM[32]', 'HBM[-1]', 'HBM[4:2]', 'HBM[01]', 'DDR[2]',
                      'DDR[0:1]', 'PLRAM[0]', 'HBM[0]\n'):
            with self.subTest(group=group), self.assertRaises(ValueError):
                p.pool(group)

    def test_rounding_and_exact_capacity(self):
        args = [dict(id=0, name='a', pointer=True, bundle='m', payload_bytes=256 * p.MIB)]
        p.validate_layout(args, {'a': 'HBM[0]'}, reserve_bytes=0)
        args[0]['payload_bytes'] += 1
        with self.assertRaisesRegex(ValueError, 'BO exceeds'):
            p.validate_layout(args, {'a': 'HBM[0]'}, reserve_bytes=0)
        for alignment in (0, -1, 3, True):
            with self.subTest(alignment=alignment), self.assertRaises(ValueError):
                p.validate_layout(self.args, self.maps['ddr_shared'], alignment=alignment)

    def test_duplicate_config_and_wrong_kernel(self):
        config = p.connectivity(self.maps['ddr_shared'])
        for bad in (config + f'sp={p.CU}.keys:DDR[0]\n', config.replace(p.KERNEL, 'graph_accel')):
            with self.assertRaises(ValueError):
                p.read_connectivity(bad)

    def test_xml_corruptions(self):
        tree = ET.parse(p.XMLS['csr'])
        def arg_mutation(root, name, value):
            root.find('kernel/args/arg').set(name, value)
        mutations = [lambda r: arg_mutation(r, 'id', '1'),
                     lambda r: arg_mutation(r, 'name', 'requests'),
                     lambda r: arg_mutation(r, 'addressQualifier', '0'),
                     lambda r: arg_mutation(r, 'port', 'M_AXI_KEY_MEM'),
                     lambda r: arg_mutation(r, 'size', '0x4'),
                     lambda r: arg_mutation(r, 'offset', '0x1c'),
                     lambda r: r.find('kernel').set('hwControlProtocol', 'ap_ctrl_hs'),
                     lambda r: r.find('kernel/args').remove(r.find('kernel/args/arg'))]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'bad.xml'
            for index, mutate in enumerate(mutations):
                root = copy.deepcopy(tree.getroot())
                mutate(root)
                ET.ElementTree(root).write(path)
                with self.subTest(index=index), self.assertRaises(ValueError):
                    p.validate_xml(self.args, path)

    def test_source_interface_changes_detected(self):
        source = p.SOURCE.read_text()
        changes = [source.replace('uint64_t* heap', 'uint16_t* heap'),
                   source.replace('port=keys offset=slave', 'port=lost offset=slave'),
                   source.replace('port=keys offset=slave bundle=key_mem',
                                  'port=keys offset=slave bundle=wrong_mem')]
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'top.cpp'
            for index, change in enumerate(changes):
                path.write_text(change)
                with self.subTest(index=index), self.assertRaises(ValueError):
                    p.validate_xml(p.parse_source(path), p.XMLS['csr'])


if __name__ == '__main__':
    unittest.main()
