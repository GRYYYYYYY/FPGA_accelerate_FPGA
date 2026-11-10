from pathlib import Path
import hashlib,json,sys
out=Path(sys.argv[1]).resolve();session_log=Path(sys.argv[2]).resolve();lines=session_log.read_text(errors='replace').splitlines()
begins=[i for i,line in enumerate(lines)if line=='CANDIDATE_COST_SYNTH_BEGIN version=2022.2'];ends=[i for i,line in enumerate(lines)if line=='CANDIDATE_COST_SYNTH_DONE']
assert len(begins)==len(ends)==1 and begins[0]<ends[0]
text='\n'.join(lines[begins[0]:ends[0]+1])+'\n';target=out/'full_synthesis.log';assert not target.exists();target.write_text(text)
m={'sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'source_log':str(session_log),'begin_line':begins[0]+1,'end_line':ends[0]+1,'bytes':target.stat().st_size,'mechanism':'Unique exact BEGIN(version2022.2) and DONE lines in authoritative session log; completion history receipt separately bound by auditor'}
(out/'log_capture.json').write_text(json.dumps(m,indent=2)+'\n');print(json.dumps(m,indent=2))
