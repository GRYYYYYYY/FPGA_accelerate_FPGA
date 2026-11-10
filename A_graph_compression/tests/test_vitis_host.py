"""Offline ABI and corruption tests; no XRT device is opened."""
import json
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
HOST=ROOT/'build/vitis_graph_host_20261023_v2'
BUNDLE=ROOT/'data/derived/vitis_graph_kernel_20261023_v2'

class HostContractTests(unittest.TestCase):
    def run_host(self,manifest,mode,success):
        p=subprocess.run([str(HOST),'--preflight',str(manifest),mode],capture_output=True,text=True)
        self.assertEqual(p.returncode==0,success,p.stdout+p.stderr)
        return p

    def test_full_verified_workloads(self):
        for mode in ['csr','compact']:
            d=json.loads(self.run_host(BUNDLE/mode/'board.txt',mode,True).stdout)
            self.assertEqual((d['cases'],d['requests'],d['records'],d['expected_failed_requests']),
                             (10,274736,1100754,53762))

    def test_corrupt_fixture_and_descriptor_rejected(self):
        image,config,case=(BUNDLE/'csr/board.txt').read_text().splitlines()[0].split()
        original=Path(case).read_bytes()
        with tempfile.TemporaryDirectory() as tmp:
            d=Path(tmp);manifest=d/'manifest.txt';bad=d/'bad.bin';cfg=d/'config.bin'
            for label,offset,value in [('too_many_requests',0,65537),('capacity',4,1048577),
                                        ('records',8,1048576),('failed',12,65537)]:
                with self.subTest(label=label):
                    data=bytearray(original);struct.pack_into('<I',data,offset,value);bad.write_bytes(data)
                    manifest.write_text(f'{image} {config} {bad}\n');self.run_host(manifest,'csr',False)
            for data in [original[:-4],original+b'\x00'*4]:
                bad.write_bytes(data);self.run_host(manifest,'csr',False)
            n=struct.unpack_from('<I',original)[0]
            for offset,value in [(16+4*n,1),(16+4*n+4,1025),(16+4*n+8,5)]:
                data=bytearray(original);struct.pack_into('<I',data,offset,value);bad.write_bytes(data)
                self.run_host(manifest,'csr',False)
            data=bytearray(Path(config).read_bytes());struct.pack_into('<I',data,4,0);cfg.write_bytes(data)
            manifest.write_text(f'{image} {cfg} {case}\n');self.run_host(manifest,'csr',False)
            self.run_host(BUNDLE/'csr/board.txt','compact',False)
            manifest.write_text((BUNDLE/'csr/board.txt').read_text()+(BUNDLE/'compact/board.txt').read_text())
            self.run_host(manifest,'csr',False)

    def test_readback_mutations_rejected(self):
        code=r'''
#include "host_contract.hpp"
#include <iostream>
using namespace board_graph;
int main(){
    Case c{1,8,1,0,{7},{0,1,0},{7,8,9,10,11,12,13,14}};
    std::vector<uint32_t> r(result_words,sentinel),o(output_words,sentinel);
    std::copy(c.results.begin(),c.results.end(),r.begin());
    std::copy(c.output.begin(),c.output.end(),o.begin());
    uint32_t count[2]={1,0};compare(c,r,o,count);
    unsigned rejected=0;
    auto bad=[&](){try{compare(c,r,o,count);}catch(const std::runtime_error&){++rejected;}};
    ++count[0];bad();--count[0];++count[1];bad();--count[1];
    ++r[0];bad();--r[0];++r[2];bad();--r[2];
    ++o[7];bad();--o[7];++o[8];bad();--o[8];
    ++r[3];bad();--r[3];++r.back();bad();--r.back();
    ++o.back();bad();--o.back();r.pop_back();bad();
    std::cout<<"READBACK_MUTATIONS_REJECTED "<<rejected<<"\n";
    return rejected==10?0:1;
}
'''
        with tempfile.TemporaryDirectory() as tmp:
            source=Path(tmp)/'test.cpp';exe=Path(tmp)/'test';source.write_text(code)
            subprocess.run(['g++','-std=c++17','-O2','-Wall','-Wextra','-Werror','-I',str(ROOT/'hardware/vitis'),str(source),'-o',str(exe)],check=True,capture_output=True,text=True)
            p=subprocess.run([str(exe)],check=True,capture_output=True,text=True)
            self.assertIn('READBACK_MUTATIONS_REJECTED 10',p.stdout)

if __name__=='__main__':unittest.main()
