# Native backend exclusion specialization

The native authority reader and the transaction-fence owner callback lane9
guarantee that request READY and response VALID cannot overlap. The source-bound
composition is in results/recovery_backend_exclusion_20261027.json; this is not
a generic AXI property or a complete formal proof.

Four production files change on the restored route_block CRC baseline.
EXCLUSIVE_BACKEND_RESPONSES defaults to zero in the coordinator and the two
wrappers with external authority inputs. Only query_residency_system, which
instantiates the proven native authority and fence, enables it. Enabled mode
removes irrelevant READY terms from unexpected-response detection. No state
transition, reset, timeout, response retirement or error latch is modified.
The independent NORMAL-admission candidate is not included.

Validation must preserve default-mode request-cycle reply handling, exercise
nonzero journal recovery and authority/owner replies, and independently check
the full native interfaces without forcing signals. Full CRC pressure replay
must match all 27 reference files and simulation finish time exactly; its
additional monitor must observe both request and reply handshakes and reject
overlap or unknown overlap conditions outside coordinator cold reset.

The full-root structural result remains pending. Local source identities or
passing behavioral tests cannot establish absence of remaining loops, timing
closure, arbitrary backend compatibility when explicitly enabled, or board speed.
