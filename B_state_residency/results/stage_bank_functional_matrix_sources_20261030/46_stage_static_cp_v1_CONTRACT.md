# Isolated CP stage write experiment

Default STATIC_STAGE_WRITES=0 retains the old writer. Enabled mode uses the
previous nested capture/import control tree with static per-word processes.
No path, route-label, or native-publication changes are included. No new reset
initialization, state or cycle is added. CRC, cancellation, drift, stream index,
last-word validation and publication remain unchanged.

This is a structural diagnostic candidate, not a selected fix. Compare original
and enabled RTL and functional netlists under the unchanged import/reset/export
probe. A passing narrow probe does not replace checkpoint unit, full-system,
four-state, parameter, or matched timing validation.
