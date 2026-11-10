from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
RETRY=ROOT/'hardware/variants/label_crc_retry_v1/build_tb.py'
BASE=ROOT/'hardware/variants/label_baseline_warm_v1/build_tb.py'
def make():
 b=runpy.run_path(str(RETRY));b['make'].__globals__['BASE']=BASE
 return b['make']()
if __name__=='__main__':(HERE/'tb_retry.sv').write_text(make())
