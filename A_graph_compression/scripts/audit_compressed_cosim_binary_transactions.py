#!/usr/bin/env python3
"""Validate actual binary TV framing, four full-depth transactions per model."""
import json,os,tempfile,re
from pathlib import Path
from check_vitis_kernel import digest
ROOT=Path(__file__).resolve().parents[1]
def main():
    capacity=ROOT/'results/compressed_batch_cosim_model_capacity_20261025_v1.json'
    data=json.loads(capacity.read_text());rows=[];files={}
    tv=Path('/tmp/A_graph_compression_recovery_20261025_v1/compressed_batch_cosim_project/solution/sim/tv/cdatafile')
    for model in data['models']:
        for direction in ['autotvin','autotvout']:
            p=tv/f'c.search_batch_trace_top_v2.{direction}_{model["bundle"]}.dat'
            if not p.exists():
                assert direction=='autotvout',p
                continue
            count=0
            with p.open('rb') as probe: is_text=probe.read(14).startswith(b'[[[runtime]]]')
            if is_text:
                text=p.read_text();assert text.strip().endswith('[[[/runtime]]]')
                blocks=re.findall(r'\[\[transaction\]\]\s+(\d+)\s*\n(.*?)\[\[/transaction\]\]',text,re.S)
                assert len(blocks)==4
                for i,(index,body) in enumerate(blocks):
                    assert int(index)==i
                    words=body.split();assert len(words)==model['depth'],(p,len(words),model['depth'])
                    assert all(re.fullmatch(r'0x[0-9a-fA-F]+',w) and int(w,16).bit_length()<=model['data_bits'] for w in words)
                files[str(p)]=digest(p)
                rows.append(dict(path=str(p),format='text',transactions=4,depth=model['depth'],payload_bytes_per_transaction=model['bytes_per_transaction'],file_bytes=p.stat().st_size))
                continue
            with p.open('rb') as f:
                while True:
                    header=f.read(8);assert len(header)==8,(p,'missing depth/end marker')
                    depth=int.from_bytes(header,'big')
                    if depth==0x5a5aa5a50f0ff0f0:
                        assert not f.read(1),(p,'trailing bytes');break
                    assert depth==model['depth'],(p,depth,model['depth'])
                    size=depth*(model['data_bits']//8)
                    assert f.tell()+size<=p.stat().st_size,(p,'truncated payload')
                    f.seek(size,1);count+=1
            assert count==4,(p,count)
            files[str(p)]=digest(p)
            rows.append(dict(path=str(p),transactions=count,depth=depth if count==0 else model['depth'],payload_bytes_per_transaction=model['bytes_per_transaction'],file_bytes=p.stat().st_size))
    for p in [capacity,Path(__file__).resolve()]:files[str(p)]=digest(p)
    target=ROOT/'results/compressed_batch_cosim_binary_transactions_20261025_v1.json'
    assert not target.exists()
    report=dict(status='all_generated_text_and_binary_memory_transaction_files_have_four_complete_declared_depth_payloads',files=files,transactions=rows,limits=['Binary framing and size verification only; RTL execution remains pending'])
    fd,tmp=tempfile.mkstemp(dir=target.parent)
    with os.fdopen(fd,'w') as f:json.dump(report,f,indent=2);f.write('\n');f.flush();os.fsync(f.fileno())
    os.replace(tmp,target);print(report['status'],len(rows))
if __name__=='__main__':main()
