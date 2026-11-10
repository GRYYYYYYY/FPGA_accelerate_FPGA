"""Fixed-capacity epoch payload/clear tradeoff; analytical, not synthesis."""
from pathlib import Path
import hashlib,json,argparse
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser();ap.add_argument('output',type=Path);a=ap.parse_args();out=a.output;out.mkdir()
 vp=ROOT/'results/small_checkpoint_vectors_full_20261023/manifest.json';v=json.loads(vp.read_text())
 assert v['status']=='passed' and v['counts']['11']==38 and v['counts']['12']==28
 directory=ROOT/'hardware/rtl/backing_frame_directory_small.sv'
 endpoint=ROOT/'hardware/rtl/memory_scratch_endpoint_small.sv'
 text=directory.read_text();assert 'epoch<=1;clear_index<=0;clear_response<=1' in text
 assert 'if(op==11 && q_status==0)state<=M_RECYCLE_SEND;' in endpoint.read_text()
 rows=[];slots=1<<18;frames=163840
 for bits in range(1,9):
  period=(1<<bits)-1;epoch=1;clears=0
  for _ in range(v['counts']['11']):
   if epoch==period:epoch=1;clears+=1
   else:epoch+=1
  assert clears==38//period
  payload=slots*(18+bits)+frames*28
  rows.append({'epoch_bits':bits,'reuse_period_recycles':period,'full_clear_passes_including_reset':1+clears,'clear_cycles_including_reset':slots*(1+clears),'additional_clear_cycles_vs_epoch8':slots*clears,'index_payload_bits':slots*(18+bits),'total_payload_bits':payload,'ideal_RAM36_bit_capacity_lower_bound':(payload+36863)//36864,'metadata_bytes_saved_vs_epoch8':slots*(8-bits)//8})
 result={'status':'analytical_model','frames':frames,'hash_slots':slots,'query_recycles':38,'checkpoint_TX_only_recycles':28,'rows':rows,'sources':{str(p):sha(p) for p in [vp,directory,endpoint,Path(__file__).resolve()]},'limitations':['Counts CLEAR_INDEX cycles only, not total endpoint latency.','Checkpoint RECYCLE_TX retains epoch and backing; it does not count as a full recycle.','RAM36 bit-capacity lower bounds ignore packing and ports; actual resource savings require synthesis.','No RTL configuration changed; narrower epochs require wrap regression at chosen configuration.']}
 (out/'manifest.json').write_text(json.dumps(result,indent=2)+'\n');(out/Path(__file__).name).write_bytes(Path(__file__).read_bytes())
 for row in rows:print(row)
if __name__=='__main__':main()
