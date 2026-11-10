"""Negotiated canonical-node and site-resource routing; physical checks external."""
from collections import Counter, defaultdict
from time import perf_counter
from netlist import ownership
from site_search import search, EMPTY
from site_search import merge_demands
from site_resources import SiteState
from netlist_routing import validate_routes


def demand_entries(demands):
    signals,bits,values=demands
    return {(0,r):0 for r in signals} | {(1,r):(m,v) for r,m,v in bits} | {(2,r):v for r,v in values}


def incompatible(key,a,b):
    if key[0]==0:return True
    if key[0]==1:return bool((a[1]^b[1]) & a[0] & b[0])
    return a!=b


class DemandLedger:
    def __init__(self):self.users=defaultdict(dict);self.by_net={}
    def release(self,net):
        for key in self.by_net.pop(net,{}):
            del self.users[key][net]
            if not self.users[key]:del self.users[key]
    def replace(self,net,demands):
        self.release(net);entries=demand_entries(demands);self.by_net[net]=entries
        for key,value in entries.items():self.users[key][net]=value
    def penalty(self,net,before,after,present,history):
        old=demand_entries(before);cost=0
        for key,value in demand_entries(after).items():
            if key in old and old[key]==value:continue
            others=sum(owner!=net and incompatible(key,value,v) for owner,v in self.users.get(key,{}).items())
            cost+=present*others+history[key]
        return cost
    def conflicts(self):
        result={}
        for key,owners in self.users.items():
            entries=list(owners.items());bad=set()
            for i,(a,av) in enumerate(entries):
                for b,bv in entries[i+1:]:
                    if incompatible(key,av,bv):bad.update((a,b))
            if bad:result[key]=sorted(bad)
        return result


def route_batch(provider,snapshot,queries,requirements,*,max_iterations=80,
                max_expansions=200000,present_cap=8,fixed_bits=(),
                fixed_signals=(),fixed_values=(),progress=None):
    if min(max_iterations,max_expansions,present_cap)<1:raise ValueError('Positive budgets required')
    fixed_bits=tuple(fixed_bits);fixed_signals=tuple(fixed_signals);fixed_values=tuple(fixed_values)
    names=[q['net'] for q in queries]
    if not names or len(set(names))!=len(names) or not set(names)<=set(snapshot['nets']):
        raise ValueError('Invalid routing query domain')
    protected,protected_pips=ownership(snapshot,names);reserved={}
    for q in queries:
        for node in [q['source'],*q['sinks']]:
            if node in protected or (node in reserved and reserved[node]!=q['net']):raise ValueError('Reserved terminal conflict')
            reserved[node]=q['net']
    owners=defaultdict(set);ledger=DemandLedger();history=Counter();site_history=Counter()
    routes={};site_demands={};iterations=[];started=perf_counter()
    for iteration in range(max_iterations):
        present=min(2**min(iteration,20),present_cap);outcomes=[]
        for q in queries:
            name=q['net'];old=routes.get(name)
            if old:
                for node in old['nodes']:owners[node].remove(name)
            ledger.release(name);tree={q['source']};edges=[];demands=EMPTY;connections=[]
            forbidden=set(protected)|{n for n,owner in reserved.items() if owner!=name}
            def cost(edge,pip,before,after):
                return (1+present*len(owners.get(edge['dst'],set())-{name})+history[edge['dst']]
                        +ledger.penalty(name,before,after,present,site_history))
            for target in sorted(q['sinks']):
                r=search(provider,q['source'],target,requirements,tree_nodes=tree,
                    initial_demands=demands,blocked_nodes=forbidden,blocked_pips=protected_pips,
                    fixed_bits=fixed_bits,fixed_signals=fixed_signals,fixed_values=fixed_values,
                    max_expansions=max_expansions,edge_cost=cost)
                connections.append({'target':target,**{k:v for k,v in r.items() if k not in ('path','demands')}})
                if r['status']=='found':
                    edges.extend(r['path']);tree.update(e['dst'] for e in r['path']);demands=r['demands']
            for node in tree:owners[node].add(name)
            ledger.replace(name,demands);site_demands[name]=demands
            routes[name]={'source':q['source'],'sinks':list(q['sinks']),'nodes':sorted(tree),
                          'edges':edges,'complete':set(q['sinks'])<=tree}
            outcomes.append({'net':name,'connections':connections})
            if progress and len(outcomes)%50==0:progress(iteration,len(outcomes),len(queries))
        conflicts={n:sorted(o) for n,o in owners.items() if len(o)>1};site_conflicts=ledger.conflicts()
        incomplete=sorted(n for n,r in routes.items() if not r['complete'])
        iterations.append({'iteration':iteration,'conflicts':conflicts,
            'site_conflicts':[{'kind':k[0],'resource':k[1],'nets':v} for k,v in sorted(site_conflicts.items())],
            'incomplete_nets':incomplete,'outcomes':outcomes})
        if progress:progress(iteration,len(queries),len(queries),len(conflicts),len(site_conflicts),len(incomplete))
        if not conflicts and not site_conflicts:break
        for node,users in conflicts.items():history[node]+=len(users)-1
        for key,users in site_conflicts.items():site_history[key]+=len(users)-1
    return {'status':'routed' if not conflicts and not site_conflicts and not incomplete else 'incomplete',
        'routes':routes,'site_demands':site_demands,'iterations':iterations,
        'wall_ms':(perf_counter()-started)*1000,'protected_nodes':len(protected),
        'protected_pips':len(protected_pips),'reserved_terminals':len(reserved)}


def validate_site_routes(graph,snapshot,queries,result,requirements,*,
                         fixed_bits=(),fixed_signals=(),fixed_values=()):
    """Recompute all site demands from actual directed paths, then check claims."""
    canonical=validate_routes(graph,snapshot,queries,result)
    fixed=SiteState(fixed_signals=[(r,'protected') for r in fixed_signals],
                    fixed_bits=fixed_bits,fixed_values=fixed_values)
    ledger=DemandLedger()
    for name,route in result['routes'].items():
        demands=EMPTY
        for edge in route['edges']:
            requirement=requirements.get(edge['pip'])
            if requirement is None and graph['pips'][edge['pip']]['attributes'].get('IS_PSEUDO')=='1':
                raise ValueError('Used pseudo PIP has unknown site semantics')
            if requirement is not None and ('status' in requirement or requirement.get('additional_requirements')):
                raise ValueError('Used site requirement is unverified')
            demands=merge_demands(demands,requirement or {})
        payload=dict(zip(('signal_resources','configuration_bits','configuration_values'),demands))
        if fixed.conflicts(name,payload):raise ValueError('Route violates fixed site constraints')
        claimed=result.get('site_demands',{}).get(name)
        if claimed is None:raise ValueError('Missing site demand claim')
        claimed=merge_demands(EMPTY,dict(zip(('signal_resources','configuration_bits','configuration_values'),claimed)))
        if claimed!=demands:raise ValueError('Site demand claim differs from actual route')
        ledger.replace(name,demands)
    conflicts=ledger.conflicts()
    if result['status']=='routed' and conflicts:raise ValueError('False site-legal routing claim')
    return {'canonical':canonical,
            'site_conflicts':[{'kind':k[0],'resource':k[1],'nets':v} for k,v in sorted(conflicts.items())],
            'all_nets_site_compatible':canonical['all_nets_routed_without_conflicts'] and not conflicts,
            'scope':'Verified supplied site model only; Vivado physical readback/DRC/placement remain required.'}
