puts RUNTIME_PROBE_BEGIN
set previous_time {}
for {set step 1} {$step<=100} {incr step} {
 set code [catch {run 10ns} message]
 if {[llength [info commands current_time]]} {set now_time [current_time]} else {set now_time unavailable}
 puts [list RUNTIME_PROBE_STEP $step actual_time $now_time catch_code $code message $message]
 puts [list RUNTIME_PROBE_CYCLES [get_value -radix hex /tb_candidate_offer/cycles]]
 puts [list RUNTIME_PROBE_VALUE armed [get_value -radix hex /stage_static_cp_shadow/armed]]
 puts [list RUNTIME_PROBE_VALUE reset_edges [get_value -radix hex /stage_static_cp_shadow/reset_edges]]
 puts [list RUNTIME_PROBE_VALUE checks [get_value -radix hex /stage_static_cp_shadow/checks]]
 puts [list RUNTIME_PROBE_VALUE cp_transfer_checks [get_value -radix hex /stage_static_cp_shadow/cp_transfer_checks]]
 puts [list RUNTIME_PROBE_VALUE ka_transfer_checks [get_value -radix hex /stage_static_cp_shadow/ka_transfer_checks]]
 puts [list RUNTIME_PROBE_VALUE pw_transfer_checks [get_value -radix hex /stage_static_cp_shadow/pw_transfer_checks]]
 if {$code || ($now_time ne {unavailable} && $now_time eq $previous_time)} {break}
 set previous_time $now_time
}
quit
