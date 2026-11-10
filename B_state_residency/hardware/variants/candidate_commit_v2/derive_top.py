from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3]
def derive(s):
 p=ROOT/'hardware/variants/candidate_commit_v1/derive_top.py';spec=importlib.util.spec_from_file_location('commit_v1_transform',p);old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old);s=old.derive(s)
 needle='assign commit_req_valid=q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_cost_valid&&!commit_started;';assert s.count(needle)==1
 s=s.replace(needle,'assign commit_req_valid=!fault&&out_cost_status==0&&q_meta_valid&&raw_seen&&raw_out_valid&&out_action!=0&&out_cost_valid&&!commit_started;',1)
 s=s.replace('wire commit_busy,','wire k_reply_error=out_cost_valid&&out_cost_status!=0;\nwire commit_busy,',1)
 s=s.replace('assign fault=','assign fault=k_reply_error||',1).replace('if(commit_fault||commit_identity_error||k_fault','if(k_reply_error||commit_fault||commit_identity_error||k_fault',1)
 return s
if __name__=='__main__':Path(__file__).with_name('candidate_commit_engine.sv').write_text(derive((ROOT/'hardware/variants/candidate_cost23_v1/candidate_cost23_engine.sv').read_text()))
