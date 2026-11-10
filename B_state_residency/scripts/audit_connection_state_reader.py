from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for n,x in m['sources'].items():assert sha(out/'sources'/n)==x['sha256']
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert sha(out/'runner.py')==m['runner_sha256'] and len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 inp=ROOT/'results/connection_state_inputs_20261025';assert sha(inp/'connections.bin')==m['input_sha256'] and sha(inp/'source_bound_audit.json')==m['input_gate_sha256']
 table=(inp/'connections.bin').read_bytes();rows=[]
 for line in(out/'simulate.log').read_text().splitlines():
  if line.startswith('ROW '):
   _,idx,data=line.split();idx=int(idx);assert int(data,16)==int.from_bytes(table[idx*64:(idx+1)*64],'little');rows.append(idx)
 assert rows==list(range(0,180326,997))+[180325]
 log=(out/'simulate.log').read_text();assert 'CONNECTION_STATE_PASS real_rows=182 errors=7'in log and 'Fatal:'not in log
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'real_rows_checked':len(rows),'fault_or_invalid_cases':7,'scope':'Standalone RTL reader, raw64B AXI response and holds; not candidate integration, joined recovery, performance or board.'}
 (out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
