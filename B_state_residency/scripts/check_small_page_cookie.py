"""72-bit small-page cookie contract; preserves all prior identity domains."""
import hashlib,json,random
from pathlib import Path
FIELDS=[('slot',5),('page',21),('query',2),('price',4),('generation',16),('transaction',16),('kind',1)]
def pack(values):
    result=0;shift=0
    for name,width in FIELDS:
        value=values[name]
        if not 0<=value<1<<width:raise ValueError(name)
        result|=value<<shift;shift+=width
    assert shift==65
    return result

def unpack(value):
    if not 0<=value<1<<65:raise ValueError('reserved bits or negative cookie')
    result={}
    for name,width in FIELDS:result[name]=value&((1<<width)-1);value>>=width
    return result

def main():
    rng=random.Random(20261023);samples=[{n:0 for n,w in FIELDS},{n:(1<<w)-1 for n,w in FIELDS}]
    samples += [{n:rng.randrange(1<<w) for n,w in FIELDS} for _ in range(10000)]
    for v in samples:assert unpack(pack(v))==v
    base=samples[0];kind=dict(base,kind=1)
    assert pack(base)!=pack(kind) and (pack(base)&((1<<64)-1))==(pack(kind)&((1<<64)-1))
    rejected=0
    for name,width in FIELDS:
        for bad in [-1,1<<width]:
            try:pack(dict(base,**{name:bad}))
            except ValueError:rejected+=1
            else:raise AssertionError(name)
    for bad in [-1,1<<65,1<<71]:
        try:unpack(bad)
        except ValueError:rejected+=1
        else:raise AssertionError('reserved')
    out=Path('results/small_page_cookie_contract_20261023');out.mkdir()
    src=Path(__file__);(out/src.name).write_bytes(src.read_bytes())
    result={'status':'passed','transport_bits':72,'identity_bits':65,'reserved_bits':7,'fields_low_to_high':FIELDS,'roundtrips':len(samples),'invalid_rejected':rejected,'old_64bit_truncation_collision_detected':True,'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'rtl_implemented':False}
    (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
