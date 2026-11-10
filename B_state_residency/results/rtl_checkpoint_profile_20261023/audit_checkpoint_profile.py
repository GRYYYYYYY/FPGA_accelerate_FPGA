from pathlib import Path
import csv,json,hashlib,statistics
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'results/rtl_checkpoint_profile_20261023'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=json.loads((OUT/'manifest.json').read_text());assert m['status']=='passed'
assert sha(OUT/'manifest.json')==json.loads((OUT/'completion_audit.json').read_text())['manifest_sha256']
for path,digest in m['sources'].items():assert sha(Path(path))==digest==sha(OUT/'sources'/Path(path).name)
for name,digest in m['artifacts'].items():assert sha(OUT/name)==digest
rows=[{k:int(v) for k,v in row.items()} for row in csv.DictReader((OUT/'checkpoint_cycles.csv').open())]
assert [r['checkpoint'] for r in rows]==list(range(1,9))
stages=['begin_send','begin_wait','drain','finish_send','finish_wait','memory_send','memory_wait','query_send','query_wait']
for r in rows:
 assert sum(r[s] for s in stages)+1==r['response_cycles']
 assert r['consume_cycles']-r['response_cycles']==4
summary={key:{'min':min(r[key] for r in rows),'max':max(r[key] for r in rows),'mean':statistics.mean(r[key] for r in rows),'sum':sum(r[key] for r in rows)} for key in ['response_cycles','consume_cycles',*stages]}
base=ROOT/'results/rtl_retained_multipage_20261023';bm=json.loads((base/'manifest.json').read_text());assert bm['status']=='passed'
for path,digest in bm['sources'].items():
 if Path(path).suffix=='.sv':assert m['sources'][path]==digest
for d in [OUT,base]:
 log=(d/'simulate.log').read_text();assert 'RETAINED_MULTIPAGE_PASS pages=4 fields=5 checkpoints=8 transfers=36 checks=221 tag_wraps=4' in log and '$finish called at time : 354420 ns' in log and 'Fatal:' not in log
result={'status':'passed','summary_cycles':summary,'manifest_sha256':sha(OUT/'manifest.json'),'baseline_manifest_sha256':sha(base/'manifest.json'),'source_sha256':sha(Path(__file__)),'scope':'Passive timing for 8 checkpoints after dirty flush/release, four-page directed behavioral test with periodic scheduling. Excludes preflush, full router, platform latency.'}
(OUT/'profile_audit.json').write_text(json.dumps(result,indent=2)+'\n');(OUT/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(json.dumps(summary,indent=2))
