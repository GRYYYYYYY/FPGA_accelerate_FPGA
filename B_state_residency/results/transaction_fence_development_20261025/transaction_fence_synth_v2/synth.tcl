set_param general.maxThreads 2
read_verilog -sv {/tmp/B_state_residency_offer_20261025/transaction_fence_synth_v2/sources/transaction_fence.sv}
read_verilog -sv {/tmp/B_state_residency_offer_20261025/transaction_fence_synth_v2/sources/transaction_fence_bound.sv}
synth_design -mode out_of_context -top transaction_fence_bound -part xcu280-fsvh2892-2L-e
report_utilization -file {/tmp/B_state_residency_offer_20261025/transaction_fence_synth_v2/utilization.rpt}
write_checkpoint -force {/tmp/B_state_residency_offer_20261025/transaction_fence_synth_v2/synth.dcp}
write_verilog -force {/tmp/B_state_residency_offer_20261025/transaction_fence_synth_v2/synth.v}
puts TRANSACTION_FENCE_SYNTH_DONE
