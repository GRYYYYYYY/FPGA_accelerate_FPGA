from pathlib import Path
from collections import Counter
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'scripts'))
from make_search_geometry_vectors import oracle,make

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/search_geometry_unit_v3_20261024';m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 for name,digest in m['sources'].items():assert sha(out/'sources'/name)==digest
 assert sha(Path(m['original_source']))==m['original_source_sha256']
 s=Path(m['original_source']).read_text();a=s.index('        int deltaX = std::abs(childX - sinkX);',s.index('    void evaluateCostAndPush('));b=s.index('        float hBase =',a)
 assert (out/'sources/original_geometry.inc').read_text()==s[a:b]
 assert sha(ROOT/'scripts/verify_search_geometry_unit_v3.py')==m['runner_sha256']==sha(out/'runner.py')
 assert sha(ROOT/'scripts/make_search_geometry_vectors.py')==sha(out/'make_vectors.py')
 for p in (ROOT/'hardware/hls/search_geometry/v1').iterdir():assert sha(p)==sha(out/'sources'/p.name)
 assert [c['stage']for c in m['commands']]==['vectors','build','verify','probe_build','original_ub_probe']
 assert [c['exit_code']for c in m['commands']][:-1]==[0]*4 and m['commands'][-1]['exit_code']!=0
 assert 'signed integer overflow: 1 + 2147483647' in (out/'original_ub_probe.log').read_text()
 rows=make();lines=(out/'vectors.txt').read_text().splitlines();obs=(out/'observed.txt').read_text().splitlines()
 assert len(rows)==len(lines)==len(obs)==9496
 counts=Counter();statuses=Counter()
 for i,((g,x),line,observed)in enumerate(zip(rows,lines,obs)):
  expected=oracle(x);assert line==str(g)+' '+' '.join(f'{v&0xffffffff:08x}'for v in x+expected)
  v=observed.split();assert list(map(int,v[:2]))==[i,g] and [int(w,16)for w in v[2:]]==expected
  counts[g]+=1;statuses[expected[0]]+=1
 assert counts[0]==8192 and all(statuses[k]>0 for k in [0,1,2,4])
 neg=ROOT/'results/search_geometry_unit_20261024';nm=json.loads((neg/'manifest.json').read_text());assert nm['status']=='failed'
 for name,digest in nm['artifacts'].items():assert sha(neg/name)==digest
 assert nm['commands'][-1]['stage']=='original_ub_probe' and nm['commands'][-1]['exit_code']==0
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':9496,'original_defined_cases':8192,'groups':dict(counts),'statuses':dict(statuses),'original_UB_detected_at_O0':True,'original_O2_probe_optimized_without_diagnostic':True,'scope':'Scalar integer distance on defined original cases, plus explicit wide-arithmetic/sentinel fault policy; not yet RTL or whole search.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
