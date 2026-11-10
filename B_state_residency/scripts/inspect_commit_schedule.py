from pathlib import Path
import json,hashlib
ROOT=Path(__file__).resolve().parents[1]
def main():
 p=ROOT/'results/commit_inputs_20261025';m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed';actions={};lookahead=[];e=d=None
 for line in(p/'vectors.txt').read_text().splitlines():
  t=line.split()
  if t[0]=='E':e=list(map(int,t[1:]))
  elif t[0]=='D':d=list(map(int,t[1:]))
  elif t[0]=='A':
   action=int(t[4]);actions[action]=actions.get(action,0)+1
   if action==2:lookahead.append({'expansion':e[0],'parent':e[1],'raw_children':e[5],'filtered_children':e[7],'connection':d[0],'sink':d[1],'net':d[2],'route_sequence':d[3],'child_ordinal':int(t[1]),'child':int(t[2]),'remaining_filtered_siblings':e[7]-int(t[1])-1})
 r={'status':'observed','input_manifest_sha256':hashlib.sha256((p/'manifest.json').read_bytes()).hexdigest(),'actions':actions,'lookahead':lookahead,'implication':'Current lookahead case has no remaining parent siblings. It cannot establish immediate recursion before later sibling decisions. Add explicit multiple-child recursion-order stress before claiming scheduler equivalence.'}
 (ROOT/'results/commit_schedule_gap_20261025.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
