# Frontier methodology evidence

Vivado 2022.2 text reports substitute for the Ross skill 2026.1+ JSON commands. No constraints were changed or waived. Research clock10ns only; external input/output budgets and platform clock context are absent. Standalone internal timing is not platform timing closure or a board measurement.

Observed checks:

{
  "timing": {
    "wns_ns": 1.336,
    "tns_ns": 0.0,
    "setup_failing_endpoints": 0,
    "setup_total_endpoints": 7740,
    "whs_ns": 0.039,
    "ths_ns": 0.0,
    "hold_failing_endpoints": 0,
    "hold_total_endpoints": 7740,
    "wpws_ns": 4.458,
    "tpws_ns": 0.0,
    "pulse_failing_endpoints": 0,
    "pulse_total_endpoints": 1968,
    "check_timing": {
      "no_clock": 0,
      "constant_clock": 0,
      "pulse_width_clock": 0,
      "unconstrained_internal_endpoints": 0,
      "no_input_delay": 98,
      "no_output_delay": 105,
      "multiple_clock": 0,
      "generated_clocks": 0,
      "loops": 0,
      "partial_input_delay": 0,
      "partial_output_delay": 0,
      "latch_loops": 0
    }
  },
  "methodology": {
    "synth": {
      "TIMING-18": {
        "severity": "Warning",
        "description": "Missing input or output delay",
        "count": 233
      }
    },
    "routed": {
      "TIMING-18": {
        "severity": "Warning",
        "description": "Missing input or output delay",
        "count": 233
      }
    }
  },
  "drc": {}
}
