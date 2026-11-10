"""Freeze baseline and cached post modules with their identical real center RTL."""
from pathlib import Path
import json,shutil,hashlib,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();base=ROOT/'results/natural_query_rtl_v1';cached=ROOT/'results/parent_upstream_query_v2';sources=out/'sources';sources.mkdir()
 dependencies={}
 for name,p in [('baseline',base),('cached',cached)]:
  a=json.loads((p/'source_bound_audit.json').read_text());m=json.loads((p/'manifest.json').read_text());assert a['status']==m['status']=='passed' and a['manifest_sha256']==sha(p/'manifest.json');dependencies[name]=sha(p/'source_bound_audit.json')
  d=sources/name;d.mkdir();shutil.copyfile(p/'sources/postprev/postprev_inputs.sv',d/'postprev_inputs.sv')
 common=sources/'center';shutil.copytree(base/'sources/center',common)
 for p in common.iterdir():assert sha(p)==sha(cached/'sources/center'/p.name)
 m=dict(status='prepared',part='xcu280-fsvh2892-2L-e',period_ns=10.0,top='postprev_inputs',MAX_CYCLES=1048576,dependencies=dependencies,sources={str(p.relative_to(out)):sha(p)for p in sources.rglob('*')if p.is_file()},scope='Matched isolated OOC post modules including identical real center arithmetic. Research clock only; no board I/O budgets or whole-accelerator Fmax.')
 shutil.copyfile(__file__,out/Path(__file__).name)
 script=ROOT/'hardware/scripts/implement_parent_pair.tcl';s=script.read_text().replace('@OUT@',str(out));(out/'run.tcl').write_text(s);m['runner_sha256']=sha(out/'run.tcl');m['preparer_sha256']=sha(out/Path(__file__).name)
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');print(out)
if __name__=='__main__':main()
