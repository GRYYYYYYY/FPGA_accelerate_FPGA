"""Actual G4 restore after natural sole-owner release and an accepted graph R error."""
from pathlib import Path
import json,hashlib
HERE=Path(__file__).resolve().parent
BASE=Path('/tmp/B_state_residency_offer_20261025/fourth_system_full_v2')

def make():
    m=json.loads((BASE/'manifest.json').read_text());s=(BASE/'sources/tb_query_fault.sv').read_text()
    assert hashlib.sha256(s.encode()).hexdigest()==m['sources']['tb_query_fault.sv']['sha256']
    def change(a,b):
        nonlocal s
        assert a in s,a
        s=s.replace(a,b)
    change('reg g3_warm_mode=0;', 'reg g4_warm_mode=0;reg g3_warm_mode=0;')
    for field,old,new in [('version',"g3_warm_mode?32'd5:32'd3","g4_warm_mode?32'd6:(g3_warm_mode?32'd5:32'd3)"),('query',"g3_warm_mode?2'd3:2'd1","g4_warm_mode?2'd0:(g3_warm_mode?2'd3:2'd1)"),('price',"g3_warm_mode?4'd5:4'd3","g4_warm_mode?4'd6:(g3_warm_mode?4'd5:4'd3)")]:
        change(f'.wm_source_{field}({old})',f'.wm_source_{field}({new})')
    change("g3_warm_mode?32'd19:(wm_enable?32'd18:32'd17)","g4_warm_mode?32'd20:(g3_warm_mode?32'd19:(wm_enable?32'd18:32'd17))")
    # Keep the original first prepare at exactly the same point in the G4 trace.
    start=s.index('task fourth_query;begin');split=s.index(' $fclose(fd_gold);',start)
    prep=s[start:split].replace('task fourth_query;begin','task fourth_prepare;begin')+'end endtask\n'
    end=s.index('end endtask',split)+len('end endtask')
    query='task fourth_query;begin\n'+''' for(integer x=0;x<156;x=x+1)g4_saved_path[x]=cap_path_image[x];
 for(integer x=0;x<10;x=x+1)g4_saved_query[x]=qcp_image[x];
 g4_saved_pcrc=g3_pcrc;g4_saved_qcrc=g3_qcrc;g4_saved_lcrc=g3_lcrc;g4_saved_count=g3_lcount;
 fourth_prepare;
'''+s[split:end]
    inject=''' g4_warm_mode=1;replayed=0;armed=1;injection_seen=0;eligible_responses=0;fault_after=0;fault_case=3;wm_enable=1;warm_running=1;recovering=1;
 $fdisplay(trace,"FOURTH_FAULT_BEGIN %0d %0d %0d %0d",cycles,k_count,k_saved_checkpoint,system.controller.last_sequence);
 fault_query;
 if(qc_rsp_committed||qc_rsp_nodes||qc_rsp_acked||k_count!=3||rc_slots!=7||system.controller.last_sequence!=180330)$fatal(1,"G4 failed search/consumed sequence");
 $fdisplay(trace,"FOURTH_FAULT_DONE %0d %0d %0d %0d %0d %0d %0d %0d",cycles,poll_i,expand_i,candidate_i,commits,qc_rsp_status,qc_rsp_detail,system.controller.last_sequence);
 fourth_warm_restore;
 fourth_floor_probe;
 fourth_prepare;
 rc=$fseek(polls_fd,0,0);if(rc)$fatal(1,"fourth poll rewind");rc=$fseek(candidates_fd,0,0);if(rc)$fatal(1,"fourth candidate rewind");rc=$fseek(fd_gold,0,0);if(rc)$fatal(1,"fourth cost rewind");
 poll_i=0;expand_i=0;candidate_i=0;commits=0;outputs=0;offers=0;count2=0;physical_expands=0;metadata_calls=0;visited_reads=0;stopped=0;replayed=1;warm_running=0;
 $fdisplay(trace,"FOURTH_RETRY_BEGIN %0d",cycles);
 autonomous_query;'''
    assert query.count(' autonomous_query;')==1;query=query.replace(' autonomous_query;',inject)
    query=query.replace('query_version!=6||p_active_query!=0||p_active_price!=6','query_version!=7||p_active_query!=1||p_active_price!=7')
    query=query.replace('qcp_image[6]!=6', 'qcp_image[6]!=7').replace("qcp_image[7]!=32'h58", "qcp_image[7]!=32'h5d")
    query=query.replace('$display("FOURTH_PASS polls=', '$display("FOURTH_WARM_PASS polls=')
    s=s[:start]+prep+query+s[end:]
    # Reuse the verified raw-receipt/retirement flow with distinct saved G4 data.
    start=s.index('task third_warm_restore;');end=s.index('end endtask',start)+len('end endtask')
    restore=s[start:end].replace('third_warm_restore','fourth_warm_restore').replace('g3_saved','g4_saved').replace('THIRD_WARM','FOURTH_WARM').replace('G3','G4').replace('g3imports','g4imports')
    restore=restore.replace('as_recover_version=6;as_recover_query=0','as_recover_version=7;as_recover_query=1')
    restore=restore.replace("32'hc0030001","32'hc0040001").replace("64'h100000003","64'h100000004")
    restore=restore.replace('k_saved_checkpoint!=19','k_saved_checkpoint!=20').replace('k_corrected!=1','k_corrected!=3')
    restore=restore.replace('rc_slots!=3','rc_slots!=7').replace('last_sequence!=180328','last_sequence!=180329')
    restore=restore.replace('query_version!=6||p_active_query!=0||p_active_price!=6','query_version!=7||p_active_query!=1||p_active_price!=7')
    restore=restore.replace('owner_op(0,339193,1,1);','owner_op(0,990178,1,1);owner_op(0,339193,1,1);')
    extra=(HERE/'floor_probe.sv').read_text()
    decl='reg[31:0]g4_saved_path[0:155],g4_saved_query[0:9];reg[31:0]g4_saved_pcrc,g4_saved_qcrc,g4_saved_lcrc,g4_saved_count;\n'
    s=s.replace('task fourth_query;begin',decl+'task fourth_query;begin')
    return s.replace('\nendmodule','\n'+restore+'\n'+extra+'\nendmodule')

if __name__=='__main__':(HERE/'tb_fourth_warm.sv').write_text(make())
