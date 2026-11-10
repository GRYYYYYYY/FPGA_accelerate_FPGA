# Bus-width ablation figure scope

`integrated_hls` compares the same integrated full44 batch at HLS synthesis only.
The all64 setting retains native 32-bit ports. It reduces the LUT estimate by
77.4807%, but its 3.715 ns clock estimate still exceeds the 3.650 ns effective
budget by 0.065 ns. Falling below a whole-device LUT reference does not establish
platform fit; shell resources and mapped implementation remain unverified.

`search_core_postroute` is a separate, smaller search-only CSR design. Its LUT
count changes from 105,963 to 81,235 and WNS from -1.389 ns to -0.382 ns. Both
designs still miss timing; neither is presented as an accepted platform design.
These figures do not compare resource counts across the two integration scopes.

No board throughput, bandwidth, power, acceleration, or statistical error bars
are inferred from these deterministic synthesis/implementation reports. Source
audits are recorded in manifest.json; plotting does not re-run semantic audits.
