"""Corrupt temporary archive copies; never changes real export evidence."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from zipfile import ZipFile
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]


class ArchiveChecks(unittest.TestCase):
    def test_rejects_xml_width_and_rtl_corruption(self):
        original=ROOT/'data/derived/site_request_xo_20261024_v1'
        for mode,message in [('width','Archive AXI width differs from synthesis'),('rtl','Exported RTL/data byte mismatch')]:
            with self.subTest(mode=mode),tempfile.TemporaryDirectory() as directory:
                folder=Path(directory);plan=json.loads((original/'plan.json').read_text())
                xo=folder/'copy.xo'
                with ZipFile(plan['xo']) as source,ZipFile(xo,'w') as target:
                    changed=False
                    for name in source.namelist():
                        content=source.read(name)
                        if mode=='width' and name.endswith('/kernel.xml'):
                            xml=ET.fromstring(content);port=xml.find("kernel/ports/port[@name='M_AXI_INPUT_MEM']");port.set('dataWidth','32');content=ET.tostring(xml);changed=True
                        if mode=='rtl' and name.endswith('/hdl/verilog/search_site_request_top.v'):
                            content+=b'\n// changed archive bytes\n';changed=True
                        target.writestr(name,content)
                self.assertTrue(changed);plan['xo']=str(xo)
                (folder/'plan.json').write_text(json.dumps(plan))
                for name in ['state.json','receipt.json','export.log']:shutil.copyfile(original/name,folder/name)
                output=folder/'audit.json'
                run=subprocess.run([sys.executable,str(ROOT/'scripts/check_resident_component_xo_v2.py'),'--bundle',str(folder),'--output',str(output)],capture_output=True,text=True)
                self.assertNotEqual(run.returncode,0);self.assertIn(message,run.stderr);self.assertFalse(output.exists())


if __name__=='__main__':unittest.main()
