"""Exercise independent audit rejection gates without touching live artifacts."""
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from check_vitis_kernel import digest
from check_vitis_miss_weighted import audit

class WeightedAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.bundle=self.root/'bundle';self.bundle.mkdir();self.runs={}
        fixture=self.root/'fixture.json'
        fixture.write_text(json.dumps({'cases':[{'label':'sample','nodes':[7,7],'sample_edges':2}],'limitations':[]}))
        manifests={}
        for mode in ['csr','compact']:
            directory=self.root/mode;directory.mkdir();case=directory/'sample.bin'
            case.write_bytes(struct.pack('<4I',2,1048576,2,0))
            manifest=directory/'rtl.txt';manifest.write_text(f'image config {case}\n');manifests[mode]=manifest
        for label in ['csr','compact','tile_cache']:
            original=self.root/(label+'_original');project=self.root/(label+'_project')
            for base in [original,project]:
                rtl=base/'solution/syn/verilog';rtl.mkdir(parents=True);(rtl/'graph_accel.v').write_text('module graph_accel; endmodule\n')
            report=project/'solution/sim/report';(report/'verilog').mkdir(parents=True)
            (report/'graph_accel_cosim.rpt').write_text('| Verilog | Pass |\n')
            (report/'verilog/result.transaction.rpt').write_text('transaction 0: 100\n')
            work=self.bundle/label;work.mkdir();(work/'copied_project.json').write_text('{}')
            manifest=manifests['csr' if label=='csr' else 'compact'];case=manifest.parent/'sample.bin'
            (work/'cosim.log').write_text((f'CASE_PASS {case} requests=2 records=2 failed=0\nGRAPH_EXPAND_PASS cases=1\n')*2+'VITIS_STRATIFIED_COSIM_COMPLETE\n')
            self.runs[label]={'original':str(original),'project':str(project),'manifest':str(manifest)}
            self.receipt(label)
        files={str(p):digest(p) for p in [fixture,*manifests.values(),*[p.parent/'sample.bin' for p in manifests.values()]]}
        (self.bundle/'plan.json').write_text(json.dumps({'files':files,'fixture_plan':str(fixture),'runs':self.runs}))
    def tearDown(self):self.tmp.cleanup()
    def receipt(self,label,code=0):
        work=self.bundle/label
        (work/'receipt.json').write_text(json.dumps({'exit_code':code,'log_sha256':digest(work/'cosim.log')}))
    def test_positive(self):
        r=audit(self.bundle);self.assertEqual(r['status'],'matched_known_miss_weighted_rtl_verified');self.assertEqual(r['comparisons'][0]['tile_cache_over_csr'],1)
    def test_failures(self):
        work=self.bundle/'compact';project=Path(self.runs['compact']['project'])
        cases=[(work/'cosim.log',lambda s:s.replace('VITIS_STRATIFIED_COSIM_COMPLETE','MISSING'),True),
               (work/'cosim.log',lambda s:s+'ERROR: failure\n',True),
               (work/'cosim.log',lambda s:s.replace('requests=2','requests=1',1),True),
               (work/'cosim.log',lambda s:s.replace('GRAPH_EXPAND_PASS cases=1\n','',1),True),
               (work/'cosim.log',lambda s:s+'unexpected\n',False),
               (project/'solution/sim/report/graph_accel_cosim.rpt',lambda s:s.replace('Pass','Fail'),False),
               (project/'solution/sim/report/verilog/result.transaction.rpt',lambda s:'transaction 1: 100\n',False),
               (project/'solution/sim/report/verilog/result.transaction.rpt',lambda s:'transaction 0: 0\n',False),
               (project/'solution/sim/report/verilog/result.transaction.rpt',lambda s:s+s,False),
               (project/'solution/syn/verilog/graph_accel.v',lambda s:s+'// changed\n',False),
               (Path(self.runs['compact']['manifest']),lambda s:s+'\n',False)]
        for path,mutate,refresh in cases:
            before=path.read_text()
            with self.subTest(path=str(path),mutation=cases.index((path,mutate,refresh))):
                path.write_text(mutate(before))
                if refresh:self.receipt('compact')
                with self.assertRaises((ValueError,KeyError)):audit(self.bundle)
                path.write_text(before);self.receipt('compact')
        self.receipt('compact',1)
        with self.assertRaises(ValueError):audit(self.bundle)

if __name__=='__main__':unittest.main()
