"""Synthetic readback records test the independent checker, not real hardware."""
from array import array
import copy
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_vitis_readback import audit,check_raw,RESULT_WORDS,OUTPUT_WORDS,SENTINEL

class ReadbackAuditTests(unittest.TestCase):
    def test_full_readback_and_mutations(self):
        image,config,fixture=(ROOT/'data/derived/vitis_graph_kernel_20261023_v2/csr/rtl.txt').read_text().splitlines()[0].split()
        data=Path(fixture).read_bytes();n,capacity,written,failed=struct.unpack_from('<4I',data)
        raw=bytearray(struct.pack('<4I',written,failed,n,capacity))
        raw.extend(data[16+4*n:16+16*n]);raw.extend(struct.pack('<I',SENTINEL)*(RESULT_WORDS-3*n))
        raw.extend(data[16+16*n:]);raw.extend(struct.pack('<I',SENTINEL)*(OUTPUT_WORDS-8*written))
        with tempfile.TemporaryDirectory() as tmp:
            directory=Path(tmp);rp=directory/'batch_0.bin';rp.write_bytes(raw)
            check_raw(rp,fixture)
            for offset in [0,16,16+12*n,16+4*RESULT_WORDS,16+4*(RESULT_WORDS+8*written),len(raw)-4]:
                mutated=bytearray(raw);mutated[offset]^=1;rp.write_bytes(mutated)
                with self.assertRaises(ValueError):check_raw(rp,fixture)
            rp.write_bytes(raw[:-4])
            with self.assertRaises(ValueError):check_raw(rp,fixture)
            rp.write_bytes(raw)
            manifest=directory/'manifest.txt';manifest.write_text(f'{image} {config} {fixture}\n')
            row={'repeat':0,'case':0,'written':written,'failed':failed,'fixture_load_ms':1,
                 'batch_h2d_ms':1,'kernel_wall_ms':1,'d2h_ms':1,'validation_ms':1,'export_ms':1,'batch_wall_ms':7}
            summary={'status':'hardware_batches_readback_verified','mode':'csr','memory':'DDR[0]',
                     'repetitions':1,'cases_per_repeat':1,'completed_batches':1,'argument_memory_groups':[0]*6,
                     'device_bdf':'synthetic-test','device_name':'synthetic-test','xclbin_uuid':'synthetic-test',
                     'input_preflight_ms':1,'device_open_load_ms':1,'allocation_ms':1,'graph_h2d_ms':1,'application_wall_ms':12}
            sp=directory/'summary.json';bp=directory/'batches.jsonl'
            sp.write_text(json.dumps(summary));bp.write_text(json.dumps(row)+'\n')
            result=audit(directory,manifest,1,'csr','DDR[0]');self.assertEqual(len(result['batches']),1)
            for key,value in [('repeat',1),('written',written+1),('kernel_wall_ms',float('nan')),('batch_wall_ms',5)]:
                bad=dict(row);bad[key]=value;bp.write_text(json.dumps(bad)+'\n')
                with self.assertRaises(ValueError):audit(directory,manifest,1,'csr','DDR[0]')
            bp.write_text(json.dumps(row)+'\n')
            for key,value in [('memory','HBM[0]'),('completed_batches',0),('device_bdf',''),('application_wall_ms',10)]:
                bad=dict(summary);bad[key]=value;sp.write_text(json.dumps(bad))
                with self.assertRaises(ValueError):audit(directory,manifest,1,'csr','DDR[0]')

if __name__=='__main__':unittest.main()
