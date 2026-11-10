"""Widen only the TB route-slot observer and keep legacy arrays q1/q2-only."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/B_state_residency_offer_20261025/third_warm_full_v1')


def make():
    manifest = json.loads((BASE / 'manifest.json').read_text())
    s = (BASE / 'sources/tb_query_fault.sv').read_text()
    assert hashlib.sha256(s.encode()).hexdigest() == manifest['sources']['tb_query_fault.sv']['sha256']
    old = 'wire actual_route_slot=system.inner.backend.f_broute_payload[1];'
    assert s.count(old) == 1
    s = s.replace(old, 'wire[1:0]actual_route_slot=system.inner.backend.f_broute_payload[2:1];')
    old = 'else begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end'
    assert s.count(old) == 1
    s = s.replace(old, 'else if(actual_route_slot==1)begin saved2[count2]<=system.inner.backend.route_join.o_node;count2<=count2+1;end')
    return s


if __name__ == '__main__':
    (HERE / 'tb_third_warm.sv').write_text(make())
