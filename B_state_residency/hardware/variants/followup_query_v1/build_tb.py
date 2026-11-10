"""Verification-only iteration2 natural query with real warm/overflow images."""
from pathlib import Path
import re,json
ROOT=Path(__file__).resolve().parents[3]
def make():
 s=(ROOT/'hardware/variants/natural_stages_v1/tb_natural_stages.sv').read_text()
 for a,b in {65185:66893,150697:204279,16506:170782,2717:26422,308:822}.items():s=re.sub(r'(?<![0-9])'+str(a)+r'(?![0-9])',str(b),s)
 for a,b in [('expand_xmin=38;expand_xmax=46;expand_ymin=283;expand_ymax=295','expand_xmin=23;expand_xmax=31;expand_ymin=279;expand_ymax=291'),('out_config[351:320]!=38','out_config[351:320]!=23'),('out_config[383:352]!=46','out_config[383:352]!=31'),('out_config[415:384]!=283','out_config[415:384]!=279'),('out_config[447:416]!=295','out_config[447:416]!=291'),('expand_sequence=1;','expand_sequence=180327;'),('out_config[31:0]!=1','out_config[31:0]!=180327'),("32'd1,32'(poll_node)","32'd180327,32'(poll_node)"),('owner_cfg_capacity=0;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool','owner_cfg_capacity=53734;owner_cfg_pool=owner_cfg_primary+145424192;owner_cfg_allocator=owner_cfg_pool+859776'),(".size0(64'd145424256)",".size0(64'd146284032)"),('poll_i!=73','poll_i!=171'),('expand_i!=72','expand_i!=170'),('candidate_i!=271','candidate_i!=849'),('commits!=171','commits!=421'),('offers!=171','offers!=421'),('physical_expands!=72','physical_expands!=170'),('metadata_calls!=271','metadata_calls!=849')]:
  assert a in s,a;s=s.replace(a,b)
 return s
if __name__=='__main__':(Path(__file__).parent/'tb_followup_query.sv').write_text(make())
