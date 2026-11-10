# Research interface envelope, not a board/platform constraint file.
# The same BUFG output edge is the reference for upstream/downstream budgets.
create_clock -name core_clk -period 10.000 [get_ports clk]
set b_inputs [get_ports -filter {DIRECTION == IN && NAME != clk}]
set b_outputs [get_ports -filter {DIRECTION == OUT}]
set b_reference [get_pins b_clock/O]
set_input_delay -clock core_clk -reference_pin $b_reference -max 2.000 $b_inputs
set_input_delay -clock core_clk -reference_pin $b_reference -min 0.500 $b_inputs
set_output_delay -clock core_clk -reference_pin $b_reference -max 2.000 $b_outputs
set_output_delay -clock core_clk -reference_pin $b_reference -min -0.500 $b_outputs
