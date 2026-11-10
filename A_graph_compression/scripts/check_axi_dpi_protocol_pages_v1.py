#!/usr/bin/env python3
"""Reconstruct every exported page byte independently of the SV scoreboard."""
import json
import os
from pathlib import Path
from check_vitis_kernel import digest, require

ROOT=Path(__file__).resolve().parents[1]
def main():
    proof=ROOT/'results/axi_dpi_protocol_pages_20261025_v1.json'
    result=json.loads(proof.read_text())
    files=dict(result['files'])
    for path,h in files.items():require(digest(path)==h,'Changed executed evidence '+path)
    expected=bytearray()
    all_bits=(1<<256)-1
    full=int('123456789abcdef00112233445566778899aabbccddeeff0a5a5a5a55a5a5a50',16)
    partial=int('fedcba98765432100123456789abcdef0123456789abcdef9876543210abcdef00',16)
    mask=sum(255<<(8*j) for j in range(32) if (0x5555aaaa>>j)&1)
    pages=[]
    for page in range(4):
        payload=bytearray()
        for word in range(64):
            value=0
            if word<4:
                a=(full+word+page*4096)&all_bits
                b=(partial+word+page*4096)&all_bits
                value=(a & (all_bits^mask)) | (b & mask)
            payload.extend(value.to_bytes(32,'big'))
        expected.extend((64).to_bytes(8,'big'));expected.extend(payload)
        pages.append(bytes(payload))
    require(len(set(pages))==4,'Page-specific stimuli not distinct')
    for label in ['native','dpi']:
        path=next(Path(p) for p in files if p.endswith('/rtldatafile/'+label+'.dat'))
        require(path.read_bytes()==bytes(expected),'Independent full-page byte oracle failed '+label)
    for p in [proof,Path(__file__).resolve()]:files[str(p)]=digest(p)
    report=dict(status='native_and_dpi_all_four_complete_page_exports_match_independent_python_byte_oracle',
                bytes_per_export=len(expected),pages=4,words_per_page=64,files=files,
                limits=['Supplementary small-depth 256-bit generated AXI model only',
                        'Full-depth whole-DUT replay, all target models and production transactions remain required'])
    target=ROOT/'results/axi_dpi_protocol_pages_oracle_20261025_v1.json'
    require(not target.exists(),'Refuse overwrite');temporary=target.with_suffix('.json.tmp')
    with temporary.open('x') as f:
        json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(temporary,target);print(report['status'])
if __name__=='__main__':main()
