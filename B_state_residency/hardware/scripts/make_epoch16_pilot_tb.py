"""Parameter-only epoch16 actual-value pilot checker."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
def render():
 return (ROOT/'results/record_epoch6_pilot_20261024/pilot/sources/tb_epoch6_endpoint_checkpoint_stream.sv').read_text().replace('epoch6_endpoint_checkpoint_stream','epoch16_endpoint_checkpoint_stream').replace('.EPOCH_BITS(SMALL?2:6)','.EPOCH_BITS(SMALL?2:16)')
if __name__=='__main__':assert (ROOT/'hardware/tb/tb_epoch16_endpoint_checkpoint_stream.sv').read_text()==render();print('EPOCH16_PILOT_CHECKER_RECONSTRUCTION_PASS')
