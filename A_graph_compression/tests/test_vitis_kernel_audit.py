import copy
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
import zipfile
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'scripts'))
from check_vitis_kernel import validate_abi,validate_case_log,validate_packaged_rtl

class KernelAuditTests(unittest.TestCase):
    def test_wrong_packaged_rtl_rejected(self):
        directory=ROOT/'build/vitis_graph_csr_20261023_v2/solution/syn/verilog'
        with zipfile.ZipFile(ROOT/'data/derived/vitis_graph_kernel_20261023_v2/csr/graph_accel.xo') as archive:
            validate_packaged_rtl(archive,directory)
            names=[n for n in archive.namelist() if '/hdl/verilog/' in n and n.endswith('.v')]
            with tempfile.TemporaryDirectory() as tmp:
                p=Path(tmp)/'bad.xo'
                for mutation in ['missing','changed']:
                    with zipfile.ZipFile(p,'w') as bad:
                        for i,n in enumerate(names):
                            if i==0 and mutation=='missing':continue
                            bad.writestr(n,archive.read(n)+(b'//changed' if i==0 else b''))
                    with zipfile.ZipFile(p) as bad:
                        with self.assertRaises(ValueError):validate_packaged_rtl(bad,directory)

    def test_csim_log_missing_changed_duplicate(self):
        folder=ROOT/'data/derived/vitis_graph_kernel_20261023_v2/csr'
        log=(folder/'synth.log').read_text()
        cases=validate_case_log(log,folder/'full.txt',1)
        self.assertEqual(len(cases),11)
        count=cases[0]['requests']
        for changed in [log.replace('CASE_PASS ','CASE_LOST ',1),log.replace(f'requests={count}',f'requests={count+1}',1),log+log,
                        log.replace('GRAPH_EXPAND_PASS cases=11','GRAPH_EXPAND_PASS cases=10')]:
            with self.assertRaises(ValueError):validate_case_log(changed,folder/'full.txt',1)

    def test_abi_mutations(self):
        root=ET.Element('root');kernel=ET.SubElement(root,'kernel',name='graph_accel')
        ports=ET.SubElement(kernel,'ports');ET.SubElement(ports,'port',name='m_axi_graph',mode='master')
        ET.SubElement(ports,'port',name='s_axi_control',mode='slave');args=ET.SubElement(kernel,'args')
        names=['image','config','requests','output','result','counts','request_count','output_capacity_words']
        for i,name in enumerate(names):
            ET.SubElement(args,'arg',id=str(i),name=name,addressQualifier=str(i<6 and 1 or 0),
                          size=str(8 if i<6 else 4),offset=str(16+12*i),port='m_axi_graph' if i<6 else 's_axi_control')
        validate_abi(ET.tostring(root))
        for index,key,value in [(0,'name','bad'),(5,'id','6'),(6,'addressQualifier','1'),(0,'size','4'),
                                (0,'offset','15'),(1,'offset','16'),(0,'port','missing'),(0,'port','s_axi_control')]:
            bad=copy.deepcopy(root);bad.find('./kernel/args')[index].set(key,value)
            with self.assertRaises(ValueError):validate_abi(ET.tostring(bad))
        args.remove(args[-1])
        with self.assertRaises(ValueError):validate_abi(ET.tostring(root))

if __name__=='__main__':unittest.main()
