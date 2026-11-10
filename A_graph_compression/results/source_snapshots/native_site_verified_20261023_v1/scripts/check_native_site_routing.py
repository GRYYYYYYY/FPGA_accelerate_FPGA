#!/usr/bin/env python3
"""Independently decode native site results against the physically checked reference."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from packed_graph import PackedGraph
from site_search import EMPTY, merge_demands
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def equal(actual,expected,context):
    if actual!=expected:raise ValueError(context+' differs')


def index(values,key,context):
    if type(key) is not int or not 0<=key<len(values):raise ValueError('Invalid '+context+' ID')
    return values[key]


def check_mode(directory,mode,plan,reference):
    folder=ROOT/f'data/derived/native_site_{mode}_inputs_20261023_v1'
    manifest=json.loads((folder/'manifest.json').read_text())
    symbols=json.loads((folder/'symbols.json').read_text())
    routing_folder=Path(manifest['routing_fixture']).parent
    queries=json.loads((routing_folder/'queries.json').read_text())
    net_names={q['net_id']:q['net'] for q in queries}
    if len(net_names)!=manifest['queries'] or len(queries)!=manifest['queries']:raise ValueError('Query scope differs')
    raw_path=directory/f'{mode}.raw.json';receipt_path=directory/f'{mode}.receipt.json'
    receipt=json.loads(receipt_path.read_text())
    if receipt['exit_code']!=0:raise ValueError('Native process failed')
    equal(digest(raw_path),receipt['output_sha256'],'Raw result hash')
    submission_path=directory/f'{mode}.submission.json';submission=json.loads(submission_path.read_text())
    expected_command=[str(ROOT/'build/native_site_20261023_v1'),manifest['image'],manifest['routing_fixture'],str(folder/'sites.txt'),
                      str(plan['cache_rows']),str(plan['max_iterations']),str(plan['max_expansions']),str(plan['present_cap'])]
    equal(submission['command'],expected_command,'Executed command')
    equal(submission['cpu'],plan['cpu'],'Pinned CPU')
    equal(submission['owner_pid'],plan['owner_pid'],'Execution owner')
    image=PackedGraph(manifest['image']);raw=json.loads(raw_path.read_text())
    equal(raw['scope'],'tested_site_instances_only','Model scope')
    equal(raw['status'],reference['status'],'Final status')
    names=[image.text(n[0]) for n in image.nodes]
    def node(n):return index(names,n,'node')
    def net(n):
        if type(n) is not int or n not in net_names:raise ValueError('Invalid net ID')
        return net_names[n]
    @lru_cache(maxsize=65536)
    def pip_text(tile,suffix):
        t=index(image.tiles,tile,'tile')
        if type(suffix) is not int or not 0<=suffix<len(image.str_offsets)-1:raise ValueError('Invalid PIP string ID')
        return image.text(t[0])+'/'+image.text(suffix)
    def pip(pair):
        if len(pair)!=2:raise ValueError('Invalid PIP identity')
        return pip_text(*pair)
    def demands(d):
        if len(d)!=3:raise ValueError('Malformed site demands')
        resources=symbols['resources'];values=symbols['values']
        return [[index(resources,r,'resource') for r in d[0]],
                [[index(resources,r,'resource'),m,v] for r,m,v in d[1]],
                [[index(resources,r,'resource'),index(values,v,'value')] for r,v in d[2]]]
    requirements={name:dict(zip(('signal_resources','configuration_bits','configuration_values'),demands(
        [r['signal_resources'],r['configuration_bits'],r['configuration_values']]))) for name,r in symbols['requirements'].items()}
    @lru_cache(maxsize=4096)
    def row(n):return set(image.numeric_neighbors(n))
    def edge(record):
        if len(record)!=8 or any(type(v) is not int or v<0 for v in record):raise ValueError('Malformed edge')
        src,dst,tile,pip_id,up,down,attr,direction=record
        node(src);node(dst)
        if tuple(record[1:]) not in row(src):raise ValueError('Directed edge/attributes absent from packed image')
        name=pip((tile,pip_id));tile_name=name.split('/',1)[0]
        sw=tile_name+'/'+image.text(down if direction else up)
        dw=tile_name+'/'+image.text(up if direction else down)
        if image.attrs(attr).get('IS_PSEUDO')=='1' and name not in requirements:
            raise ValueError('Used pseudo PIP without tested requirements')
        return {'src':node(src),'dst':node(dst),'pip':name,'src_wire':sw,'dst_wire':dw,
                'direction':'reverse' if direction else 'forward'}
    converted={};converted_demands={};query_map={q['net_id']:q for q in queries}
    for r in raw['routes']:
        name=net(r['net'])
        if name in converted:raise ValueError('Duplicate route')
        q=query_map[r['net']]
        converted[name]={'source':node(q['source']),'sinks':[node(n) for n in q['sinks']],
            'nodes':[node(n) for n in r['nodes']],'edges':[edge(e) for e in r['edges']],'complete':r['complete']}
        converted_demands[name]=demands(r['demands'])
        recomputed=EMPTY
        for e in converted[name]['edges']:recomputed=merge_demands(recomputed,requirements.get(e['pip'],{}))
        claimed=merge_demands(EMPTY,dict(zip(('signal_resources','configuration_bits','configuration_values'),converted_demands[name])))
        equal(claimed,recomputed,'Route-derived demands for '+name)
    equal(converted,reference['routes'],'Complete final trees')
    equal(converted_demands,reference['site_demands'],'Complete site demands')
    equal(len(raw['iterations']),len(reference['iterations']),'Round count')
    connections=0;conflict_counts=[]
    for number,(actual,expected) in enumerate(zip(raw['iterations'],reference['iterations'])):
        equal(expected['iteration'],number,'Reference round identity')
        conflicts={node(n):sorted(net(v) for v in users) for n,users in actual['conflicts']}
        if len(conflicts)!=len(actual['conflicts']):raise ValueError('Duplicate conflict node')
        equal(conflicts,expected['conflicts'],f'Round {number} conflicts')
        site_conflicts=[{'kind':kind,'resource':index(symbols['resources'],resource,'resource'),'nets':sorted(net(n) for n in users)}
                        for kind,resource,users in actual['site_conflicts']]
        equal(site_conflicts,expected['site_conflicts'],f'Round {number} site conflicts')
        equal(sorted(net(n) for n in actual['incomplete']),expected['incomplete_nets'],f'Round {number} incomplete nets')
        equal(len(actual['connections']),len(queries),'Native outcome count')
        equal(len(expected['outcomes']),len(queries),'Reference outcome count')
        conflict_counts.append(len(conflicts))
        for q,outcomes,old in zip(queries,actual['connections'],expected['outcomes']):
            equal(old['net'],q['net'],'Outcome net identity')
            targets=sorted(q['sinks'])
            equal(len(outcomes),len(targets),'Native connection count')
            equal(len(old['connections']),len(targets),'Reference connection count')
            for target,c,e in zip(targets,outcomes,old['connections']):
                context=f'Round {number}, {q["net"]}, {node(target)}'
                equal(e['target'],node(target),'Target')
                for key in ('status','cost','expanded','blocked'):equal(c[key],e.get(key),context+' '+key)
                equal(sorted(node(n) for n in c['unknown_sources']),e['unknown_sources'],context+' unknown sources')
                equal(sorted(pip(pair) for pair in c['unknown_pips']),e['unknown_pips'],context+' unknown PIPs')
                connections+=1
    return {'status':'matches_physically_validated_python_under_partial_site_model','nets':len(converted),
            'pips':sum(len(r['edges']) for r in converted.values()),'round_conflicts':conflict_counts,
            'connections_checked':connections,'nets_with_site_demands':sum(any(d) for d in converted_demands.values()),
            'measurements':{k:raw[k] for k in ('preparation_ms','route_ms','cache_hits','cache_misses')},
            'artifacts':{str(p):digest(p) for p in (raw_path,receipt_path,submission_path,directory/f'{mode}.log')}}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('experiment',type=Path)
    p.add_argument('--mode',nargs='+',choices=['csr','compact'],default=['csr','compact'])
    p.add_argument('--output',type=Path,required=True);a=p.parse_args();directory=a.experiment.resolve()
    if len(set(a.mode))!=len(a.mode):raise ValueError('Duplicate mode')
    binding_path=ROOT/'results/native_site_execution_binding_20261023_v1.json'
    binding=json.loads(binding_path.read_text())
    equal(directory,ROOT/binding['output'],'Bound experiment directory')
    plan_path=directory/'plan.json';plan=json.loads(plan_path.read_text())
    equal(digest(plan_path),binding['files'][str(plan_path.relative_to(ROOT))],'Frozen plan hash')
    for name,value in plan['files'].items():equal(digest(name),value,'Frozen evidence '+name)
    for key,value in {'queries':1062,'verified_instances':14,'cache_rows':4096,'max_iterations':80,'max_expansions':200000,'present_cap':8}.items():
        equal(plan[key],value,'Plan '+key)
    if set(a.mode)=={'csr','compact'}:
        complete=json.loads((directory/'execution_complete.json').read_text())
        equal(complete['status'],'awaiting_independent_semantic_audit','Execution completion')
    reference_path=ROOT/'data/derived/site_routing_all_known_instances_20261023_v1/routes.json'
    if str(reference_path) not in plan['files']:raise ValueError('Unbound reference')
    print('NATIVE_SITE_AUDIT_LOADING_REFERENCE',flush=True)
    reference=json.loads(reference_path.read_text())
    results={}
    for mode in a.mode:
        print('NATIVE_SITE_AUDIT_MODE',mode,flush=True)
        results[mode]=check_mode(directory,mode,plan,reference)
    report={'status':'verified_native_site_routing' if len(results)==2 else 'verified_native_site_routing_partial_modes',
            'modes':results,'plan_sha256':digest(plan_path),'reference_sha256':plan['files'][str(reference_path)],
            'checker_files':{str(p):digest(p) for p in (Path(__file__),ROOT/'src/packed_graph.py',ROOT/'src/site_search.py',ROOT/'src/site_resources.py')},
            'limitations':['Only fourteen tested physical PIP instances; does not certify the full site/resource model.',
                'Final directed edges/attributes, demands, round conflicts and all retained connection fields are compared.',
                'Per-connection paths were omitted by the Python reference; they are not claimed equal.',
                'Physical readback is inherited by exact equality to the previously validated final trees; no new Vivado run.',
                'Single execution diagnostics with concurrent host work, not statistical performance or board acceleration.']}
    write_new(a.output,report);print(json.dumps(report,indent=2))


if __name__=='__main__':main()
