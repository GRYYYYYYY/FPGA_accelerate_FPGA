from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 s=s.replace('module candidate_offer_engine #','module candidate_capture_engine #',1)
 s=s.replace('candidate_commit_query_core #','candidate_capture_query_core #',1)
 s=s.replace(' core(\n',' core(\n.frame_version(query_version),.frame_design(design_id),\n',1)
 assert '.frame_version(query_version)'in s
 return s
if __name__=='__main__':
 p=Path(__file__).parent;(p/'candidate_capture_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_offer_v1/candidate_offer_engine.sv').read_text()))
