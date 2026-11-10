# Immutable connection State reader

Initial serial non-timing CPU profile. Each global connection index addresses one 64B record, imported by prepare_connection_state.py from the original RRT and verbatim State initializer. Table format is in the input layout.json. This is initial configuration, not a recorded live routing State. Landmark is inactive in this profile; optional landmark support remains unfinished.

Configuration is immutable until reset, aligned64B, nonempty and address range checked. Requests bind query2, price4, complete version32 and design64, plus cookie/connection/net/sink/cross flags; profile revision is separately returned. Every accepted valid request reads one512bit AXI beat. Reply remains owned under backpressure. Row magic/identity/source range/cross flags/landmark boolean/reserved policy are checked. AXI id/response/last are checked.

Bad request or identity returns1/2 without AXI; malformed row3, bus4, abort/drift/timeout5 stop admission until reset. Abort/timeout does not withdraw ARVALID or abandon pending R. Logical reply can retire before physical drain; busy remains until both finish. Reset is allowed only under a caller-controlled bus reset/drain policy; no joined reset/reload claim.

reader_v4 XSim2022.2 gate reads182 real records (stride997 plus last) and checks all512bits against imported data, stalled address/reply stability, invalid index, stale full version, mismatched row, bus response error, abort during stalled AR, high16bit active-version drift, timeout and physical drain. Seven error scenarios are standalone checks, not exhaustive AXI/protocol verification. Input auditor separately checks all180326 records against independent original RRT grammar. No candidate integration or hardware speedup is established.
