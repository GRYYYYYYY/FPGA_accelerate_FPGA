"""Reuse full normal two-query stimulus on the unchanged, recovery-capable fabric join."""
from pathlib import Path
import importlib.util
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).parent

def make():
 p=ROOT/'hardware/variants/transaction_fence_join_v1/build_tb.py'
 spec=importlib.util.spec_from_file_location('fence_join_builder',p);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
 s=mod.make()
 normal=(ROOT/'hardware/variants/route_commit_join_drain_v2/tb_route_join_drain.sv').read_text()
 mark='initial begin\n trace=$fopen'
 # Keep hardware, recovery callbacks, initial checkpoint load and serial boot from the real fault fixture.
 # Replace only the stimulus after initial label import with the original full query/commit/ripup sequence.
 a=s.index(' control(1); // Durable import complete')
 b=normal.index(' for(query_index=0;query_index<2;query_index=query_index+1)begin')
 s=s[:a]+normal[b:]
 task=normal[normal.index('task route_command('):normal.index(mark)]
 s=s.replace(mark,task+'\n'+mark,1)
 # Final ownership/transport checks after normal CLOSE has retired.
 s=s.replace(' $fflush(trace);$fclose(trace);', ''' wait(f_normal_retired&&f_backend_idle&&f_all_drained&&f_phase==0);
 if(f_fault||k_fault||cf_fault||lr_fault||k_count!=10||k_full||k_target_reset||f_recovery_owned)$fatal(1,"normal final ownership/journal");
 $fdisplay(trace,"NF %0d %0d %0d %0d %0d %0d %0d %0d",cycles,k_count,g_reads,d_reads,t_reads,p_reads,owner_reads,cs_reads,q_reads);
 $fflush(trace);$fclose(trace);''')
 # Record packed requests at both sides; the independent audit checks no payload loss/duplication.
 s=s.replace('$fdisplay(trace,"FS %0d %0d",cycles,fx);', '$fdisplay(trace,"FS %0d %0d %0608h",cycles,fx,f_sp[fx*2432+:2432]);')
 s=s.replace('$fdisplay(trace,"FD %0d %0d %0d",cycles,f_phase,fx);', '$fdisplay(trace,"FD %0d %0d %0d %0608h",cycles,f_phase,fx,f_dp[fx*2432+:2432]);')
 return s
if __name__=='__main__':(HERE/'tb_transaction_fence_normal.sv').write_text(make())
