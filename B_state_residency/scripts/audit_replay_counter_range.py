"""Check completed replay horizon against frozen testbench scheduling counter."""
from pathlib import Path
import json,hashlib,re
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=ROOT/'results/replay_counter_range_20261023';out.mkdir();rows=[]
 for name in ['rtl_small_checkpoint_stream_full_20261023','rtl_epoch6_checkpoint_stream_full_20261023','rtl_checkpoint_stream_cycle64_pilot_20261023']:
  folder=ROOT/'results'/name;mp=folder/'manifest.json';m=json.loads(mp.read_text());assert m['status']=='passed' and sha(mp)==json.loads((folder/'completion_audit.json').read_text())['manifest_sha256']
  tb=[Path(p) for p in m['sources'] if '/tb/' in p];assert len(tb)==1 and sha(tb[0])==m['sources'][str(tb[0])]
  text=tb[0].read_text();assert 'always #5 clk=~clk;' in text
  bits=64 if 'longint unsigned cycle=0;' in text else 32;assert bits==64 or 'integer cycle=0;' in text
  limit=2**64 if bits==64 else 2**31
  # One increment per rising edge, including reset; overestimate by one.
  cycles=m['end_ns']//10+1;assert cycles<limit
  rows.append({'result':name,'counter_bits':bits,'unsigned':bits==64,'conservative_elapsed_cycles':cycles,'first_bad_cycle':limit,'within_range':True,'manifest_sha256':sha(mp),'testbench_sha256':sha(tb[0])})
 result={'status':'passed','rows':rows,'source_sha256':sha(Path(__file__)),'scope':'Only observed completed simulation horizons; not a promise of safety for longer trajectories. Frozen evidence remains unchanged.'}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes());print(json.dumps(rows,indent=2))
if __name__=='__main__':main()
