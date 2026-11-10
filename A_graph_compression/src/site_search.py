"""Dijkstra over node/configuration states; no node-only label collapse.

Requires a verified requirement adapter. Unknown pseudo semantics must be
handled explicitly by that adapter; this core does not filter graph families.
"""
import heapq
from itertools import count
from site_resources import ConfigurationBits
from search_experiment import IncompleteDomain


def merge_demands(state, requirement):
    signals,bits,values = state
    signals = tuple(sorted(set(signals) | set(requirement.get('signal_resources',()))))
    bit_map = ConfigurationBits.normalize([*bits,*requirement.get('configuration_bits',())])
    value_map = dict(values)
    for field,value in requirement.get('configuration_values',()):
        if field in value_map and value_map[field] != value:
            raise ValueError('Incompatible configuration values')
        value_map[field] = value
    return (signals,tuple(sorted((k,*v) for k,v in bit_map.items())),tuple(sorted(value_map.items())))


EMPTY = ((),(),())


def verified_requirements(records, evidence):
    """Select only explicitly evidenced instances with complete requirements.

    Pattern probes and endpoint mappings do not certify every physical instance.
    Evidence is a mapping of PIP IDs to the full requirement payload verified
    for that instance; mismatches are errors, absent evidence stays unknown.
    """
    result = {}
    keys=('signal_resources','configuration_bits','configuration_values')
    for pip,proven in evidence.items():
        if pip not in records:raise ValueError('Evidence refers to missing PIP')
        record=records[pip]
        if record.get('additional_requirements'):
            raise ValueError('Incomplete requirements cannot be certified')
        payload={key:record.get(key,[]) for key in keys}
        if payload != {key:proven.get(key,[]) for key in keys}:
            raise ValueError('Verified requirement payload changed')
        result[pip]=payload
    return result


def search(provider, source, target, requirements, *, fixed_signals=None,
           fixed_bits=(), fixed_values=(), max_expansions=200000,
           blocked_nodes=(), blocked_pips=(), tree_nodes=None,
           initial_demands=EMPTY, site_state=None, net=None, edge_cost=None):
    """Unit edge cost, exact product states, explicit budget/unknown outcomes."""
    if max_expansions < 1:raise ValueError('Positive expansion budget required')
    if site_state is not None and net is None:raise ValueError('Net identity required for site ownership')
    fixed_signals = set(fixed_signals or ())
    blocked_nodes=set(blocked_nodes);blocked_pips=set(blocked_pips)
    roots=sorted(set(tree_nodes if tree_nodes is not None else [source]))
    if not roots or set(roots)&blocked_nodes or target in blocked_nodes:
        raise ValueError('Empty tree or protected terminal')
    fixed = ConfigurationBits(fixed_bits)
    fixed_values = dict(fixed_values)
    initial_demands=merge_demands(EMPTY,{'signal_resources':initial_demands[0],
        'configuration_bits':initial_demands[1],'configuration_values':initial_demands[2]})
    if (set(initial_demands[0])&fixed_signals or fixed.conflicts('candidate',initial_demands[1])
        or any(k in fixed_values and fixed_values[k]!=v for k,v in initial_demands[2])):
        raise ValueError('Initial tree conflicts with fixed site state')
    def payload(demands):
        return dict(zip(('signal_resources','configuration_bits','configuration_values'),demands))
    if site_state is not None and site_state.conflicts(net,payload(initial_demands)):
        raise ValueError('Initial tree conflicts with site ownership')
    starts={(node,initial_demands) for node in roots}
    distance={state:0 for state in starts};parent={};serial=count()
    queue=[(0,next(serial),state) for state in sorted(starts)]
    heapq.heapify(queue);expanded=0;unknown=set();unknown_sources=set();blocked=0
    while queue:
        cost,_,state=heapq.heappop(queue)
        if cost != distance[state]:continue
        node,demands=state
        if node==target:
            path=[];cursor=state
            while cursor not in starts:
                before,edge=parent[cursor];path.append(edge);cursor=before
            return {'status':'found','path':list(reversed(path)),'cost':cost,
                    'demands':demands,'expanded':expanded,'blocked':blocked,
                    'unknown_pips':sorted(unknown),'unknown_sources':sorted(unknown_sources)}
        if expanded>=max_expansions:
            return {'status':'budget_exhausted','expanded':expanded,'unknown_pips':sorted(unknown),
                    'unknown_sources':sorted(unknown_sources)}
        try:edges=provider.neighbors(node)
        except IncompleteDomain:
            unknown_sources.add(node);continue
        expanded+=1
        for edge,pip in edges:
            if (edge['dst'] in roots or edge['dst'] in blocked_nodes or edge['pip'] in blocked_pips
                or pip['attributes'].get('IS_EXCLUDED_PIP')=='1'
                or pip['attributes'].get('IS_TEST_PIP')=='1'):
                blocked+=1;continue
            requirement=requirements.get(edge['pip'])
            if requirement is not None and ('status' in requirement or requirement.get('additional_requirements')):
                raise ValueError('Search requires verified payloads, not diagnostic records')
            if requirement is None and pip['attributes'].get('IS_PSEUDO')=='1':
                unknown.add(edge['pip']);continue
            try:merged=merge_demands(demands,requirement or {})
            except ValueError:
                blocked+=1;continue
            if (set(merged[0]) & fixed_signals or fixed.conflicts('candidate',merged[1])
                or any(k in fixed_values and fixed_values[k]!=v for k,v in merged[2])
                or (site_state is not None and site_state.conflicts(net,payload(merged)))):
                blocked+=1;continue
            step=edge_cost(edge,pip,demands,merged) if edge_cost is not None else 1
            if not isinstance(step,(int,float)) or not (step>=1) or step==float('inf'):
                raise ValueError('Finite positive edge cost required')
            following=(edge['dst'],merged);new=cost+step
            if new < distance.get(following,float('inf')):
                distance[following]=new;parent[following]=(state,edge)
                heapq.heappush(queue,(new,next(serial),following))
    return {'status':'unknown_site_semantics' if unknown else 'incomplete_domain' if unknown_sources else 'no_path',
            'expanded':expanded,'blocked':blocked,'unknown_pips':sorted(unknown),
            'unknown_sources':sorted(unknown_sources)}
