import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from resident_router_memory_plan import allocate,MIB


def arg(name,depth=8,bundle='mem'):
    return dict(name=name,pointer=True,element_bytes=8,depth=depth,payload_bytes=8*depth,bundle=bundle)


class Sharing(unittest.TestCase):
    def test_transitive_bundle_group_and_single_allocation(self):
        r=allocate({'a':[arg('x'),arg('y')],'b':[arg('x'),arg('z')]},[['a.x','b.x']])
        self.assertEqual(r['unique_buffers'],3)
        self.assertEqual(r['total_requested_bytes'],3*4096)
        self.assertEqual(len(set(r['layouts']['hbm_shared_buffers'].values())),1)

    def test_large_key_buffer_requires_multiple_channels(self):
        r=allocate({'a':[arg('keys',260*MIB//8)]},[])
        self.assertEqual(r['hbm_channels_used'],2)
        self.assertEqual(r['total_requested_bytes'],260*MIB)

    def test_rejects_invalid_sharing_and_capacity(self):
        for kernels,aliases in [
            ({'a':[arg('x'),arg('y')]},[['a.x','a.y']]),
            ({'a':[arg('x')],'b':[arg('x',9)]},[['a.x','b.x']]),
            ({'a':[arg('x')]},[['a.x','b.x']]),
            ({'a':[arg('x',bundle='m'+str(i))|{'name':'x'+str(i)} for i in range(33)]},[]),
        ]:
            with self.assertRaises(ValueError):allocate(kernels,aliases)
        with self.assertRaises(ValueError):allocate({'a':[arg('x')]},[],alignment=3)
        with self.assertRaises(ValueError):allocate({'a':[arg('x')]},[],reserve=-1)


if __name__=='__main__':unittest.main()
