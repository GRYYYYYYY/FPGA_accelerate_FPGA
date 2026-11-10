"""Keep negotiation/provider semantics, substituting explicit word key storage."""
from snapshot_routes_transform import transform_routes as snapshot_routes,transform_runtime as snapshot_runtime

def transform_routes(text):
    return snapshot_routes(text).replace('search_snapshot_route_adapter.hpp','search_word_snapshot_route_adapter.hpp').replace('snapshot_route::','word_snapshot_route::')

def transform_runtime(text):
    return snapshot_runtime(text).replace('snapshot_route::','word_snapshot_route::').replace('controller_adapter::','word_controller_adapter::')
