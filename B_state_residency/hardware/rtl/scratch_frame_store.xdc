# Exploratory synthesis constraint only; no routed timing or board clock claim.
create_clock -name core_clk -period 10.000 [get_ports clk]
