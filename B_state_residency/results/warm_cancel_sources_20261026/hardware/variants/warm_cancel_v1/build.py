"""Delay native coordinator completion until warm services retire."""
from pathlib import Path
HERE=Path(__file__).parent
BASE=Path('/tmp/B_state_residency_offer_20261025/warm_system_v2/sources')
def rep(s,a,b):assert s.count(a)==1,(a,s.count(a));return s.replace(a,b)
def ports(s):i=s.index(')(\n')+3;return s[:i]+'input wire wm_services_retired,output wire wm_config_busy,\n'+s[i:]
def make():
 s=ports((BASE/'residency_system.sv').read_text());s=rep(s,'assign wm_rec_offer=', 'assign wm_config_busy=cf_busy||cf_rsp_valid;\nassign wm_rec_offer=')
 s=rep(s,'.normal_retired(f_normal_retired&&as_retired)', '.normal_retired(f_normal_retired&&as_retired&&(!wm_on||wm_services_retired))');(HERE/'residency_system.sv').write_text(s)
 s=ports((BASE/'search_residency_system.sv').read_text());s=rep(s,')backend(',')backend(.wm_services_retired(wm_services_retired),.wm_config_busy(wm_config_busy),');(HERE/'search_residency_system.sv').write_text(s)
 s=(BASE/'recovery_coordinator.sv').read_text()
 a='''    LABELS:if(labels_done&&backend_drained&&normal_retired)begin
     if(stopped||fail_now)state<=FAILWAIT;
     else begin current_version<=new_version;current_query<=new_query;current_price<=new_price;journal_count<=0;complete(0);end
    end'''
 b='''    LABELS:begin
     if(stopped||fail_now)state<=FAILWAIT;
     else if(labels_done&&backend_drained&&normal_retired)begin current_version<=new_version;current_query<=new_query;current_price<=new_price;journal_count<=0;complete(0);end
    end'''
 s=rep(s,a,b);(HERE/'recovery_coordinator.sv').write_text(s)
 s=(BASE/'query_residency_system.sv').read_text();s=rep(s,'wire wm_on;', 'wire wm_retired,wm_config_busy;wire wm_on;')
 s=rep(s,')inner(',')inner(.wm_services_retired(wm_retired),.wm_config_busy(wm_config_busy),')
 s=rep(s,'wire wm_retired=f_normal_retired', 'assign wm_retired=f_normal_retired')
 s=rep(s,'&&!wm_label_busy&&!as_busy','&&!wm_label_busy&&!wm_config_busy&&!as_busy');(HERE/'query_residency_system.sv').write_text(s)
if __name__=='__main__':make()
