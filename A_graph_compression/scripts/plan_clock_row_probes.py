#!/usr/bin/env python3
"""Find isolated real-net row-clock probes; paths are diagnostic, never authorized."""
import argparse
from collections import deque
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'src'))
from packed_graph import PackedGraph
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for b in iter(lambda:f.read(1048576),b''):h.update(b)
    return h.hexdigest()


def bfs(rows,start,reverse=False):
    parents={start:None};queue=deque([start])
    while queue:
        node=queue.popleft()
        for edge in rows[node]:
            following=edge[0] if reverse else edge[1]
            if following not in parents:parents[following]=edge;queue.append(following)
    return parents


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    mapping_path=ROOT/'results/clock_row_mapping_20261023_v1.json';mapping=json.loads(mapping_path.read_text())
    manifest_path=ROOT/'data/derived/native_site_csr_inputs_20261023_v1/manifest.json';manifest=json.loads(manifest_path.read_text())
    image_path=Path(manifest['image']);fixture=Path(manifest['routing_fixture']);query_path=fixture.parent/'queries.json'
    for path in (image_path,fixture,query_path):
        if digest(path)!=manifest['files'][str(path)]:raise ValueError('Bound routing input changed')
    for path,value in mapping['files'].items():
        if digest(path)!=value:raise ValueError('Mapping evidence changed')
    image=PackedGraph(image_path);queries=json.loads(query_path.read_text())
    tokens=iter(fixture.read_text().split())
    if next(tokens)!='NATIVE_ROUTING_V1' or int(next(tokens))!=len(image.nodes):raise ValueError('Fixture schema/domain differs')
    def integer():return int(next(tokens))
    protected={integer() for _ in range(integer())}
    protected_pips={(integer(),integer()) for _ in range(integer())}
    bad_attrs={integer() for _ in range(integer())}
    singles=[q for q in queries if len(q['sinks'])==1]
    reserved={n for q in queries for n in [q['source'],*q['sinks']]}
    names=[image.text(n[0]) for n in image.nodes];node_ids={n:i for i,n in enumerate(names)}
    attrs=[image.attrs(i) for i in range(len(image.attr_offsets)-1)]
    pseudo={i for i,d in enumerate(attrs) if d.get('IS_PSEUDO')=='1'}
    def pip(edge):return image.text(image.tiles[edge[2]][0])+'/'+image.text(edge[3])
    all_rows=[[] for _ in names];all_reverse=[[] for _ in names]
    ordinary=[[] for _ in names];ordinary_reverse=[[] for _ in names]
    for src,node in enumerate(image.nodes):
        if node[3]<0 or src in protected:continue
        for e in image.numeric_neighbors(src):
            dst,tile,p,up,down,attr,direction=e
            if dst in protected or (tile,p) in protected_pips or attr in bad_attrs:continue
            edge=(src,*e);all_rows[src].append(edge);all_reverse[dst].append(edge)
            if attr not in pseudo:ordinary[src].append(edge);ordinary_reverse[dst].append(edge)
    results={}
    for policy,rows,reverse in (('ordinary_context',ordinary,ordinary_reverse),('all_pips_diagnostic',all_rows,all_reverse)):
        records={};suffix_cache={}
        for name,record in sorted(mapping['clock_row_pips'].items()):
            src=node_ids[record['source']['node']];dst=node_ids[record['destination']['node']]
            forced=[e for e in all_rows[src] if e[1]==dst and pip(e)==name]
            if len(forced)!=1:
                records[name]={'status':'forced_edge_protected_or_absent','matches':len(forced)};continue
            before=bfs(reverse,src,True)
            if dst not in suffix_cache:suffix_cache[dst]=bfs(rows,dst)
            after=suffix_cache[dst];candidates=[];overlap_rejections=0
            for q in singles:
                source=q['source'];target=q['sinks'][0]
                if source not in before or target not in after:continue
                prefix=[];cursor=source
                while before[cursor] is not None:
                    e=before[cursor];prefix.append(e);cursor=e[1]
                suffix=[];cursor=target
                while after[cursor] is not None:
                    e=after[cursor];suffix.append(e);cursor=e[0]
                path=prefix+forced+list(reversed(suffix));nodes=[source,*[e[1] for e in path]]
                if len(nodes)!=len(set(nodes)) or (set(nodes)&reserved)-{source,target}:
                    overlap_rejections+=1;continue
                candidates.append((len(path),q['net'],path))
            summary={'source_reachable_single_sink_queries':sum(q['source'] in before for q in singles),
                     'sink_reachable_single_sink_queries':sum(q['sinks'][0] in after for q in singles),
                     'pair_reachable_single_sink_queries':sum(q['source'] in before and q['sinks'][0] in after for q in singles),
                     'cycle_or_foreign_terminal_rejections':overlap_rejections,
                     'forward_boundary_nodes':sum(image.nodes[n][3]<0 for n in after)}
            if candidates:
                _,net,path=min(candidates)
                summary.update(status='diagnostic_candidate_not_physical_legality',net=net,
                    nodes=[names[path[0][0]],*[names[e[1]] for e in path]],numeric_edges=path,
                    pseudo_pips=[pip(e) for e in path if e[6] in pseudo])
            else:summary['status']='no_simple_pair_under_this_policy_in_captured_domain'
            records[name]=summary
            print('ROW_PROBE_REACHABILITY',policy,name,summary['status'],flush=True)
        results[policy]=records
    paths=[mapping_path,manifest_path,image_path,fixture,query_path,Path(__file__),ROOT/'src/packed_graph.py']
    report={'status':'diagnostic_probe_reachability_only','single_sink_queries':len(singles),'policies':results,
            'files':{str(p):digest(p) for p in paths},
            'limitations':['Original resource graph and running model unchanged; contexts are explicit diagnostic policies.',
                'Protected canonical resources/PIPs excluded. Candidates have no cycles or foreign query terminals.',
                'All-pips policy may require additional unknown pseudo instances; no site legality claim.',
                'Missing paths are bounded-domain results, not proof of physical impossibility; shortest subpaths may fail the simple-path filter.']}
    write_new(a.output,report)


if __name__=='__main__':main()
