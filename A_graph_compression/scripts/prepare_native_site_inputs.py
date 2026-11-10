#!/usr/bin/env python3
"""Bind only the physically tested site model to each real packed image."""
import argparse
import hashlib
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'adapters')]
from packed_graph import PackedGraph
from lut_equation import truth_table,MASK
from import_vivado import properties
from real_experiment import write_new


def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda:stream.read(1048576),b''):h.update(chunk)
    return h.hexdigest()


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['csr','compact'],required=True)
    p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    source=ROOT/'data/derived/site_routing_all_known_instances_20261023_v1'
    base=ROOT/'data/derived/region_all_nets_cap8_20261022_v1'
    stage_path=ROOT/'results/site_full_stage_20261023_v1.json';stage=json.loads(stage_path.read_text())
    if stage['status']!='full_query_physical_validation_passed_under_partial_site_model':raise ValueError('Physical reference not verified')
    files={str(stage_path):digest(stage_path)}
    def bind(path,expected=None):
        path=Path(path).resolve();actual=digest(path)
        if expected is not None and actual!=expected:raise ValueError('Frozen evidence changed: '+str(path))
        files[str(path)]=actual
    for name,value in stage['artifacts'].items():bind(ROOT/name,value)
    plan=json.loads((source/'plan.json').read_text())
    for name,value in plan['files'].items():bind(name,value)
    if plan['selected_queries']!=1062 or plan['probe_net'] is not None or plan['verified_pseudo_instances']!=14:
        raise ValueError('Unexpected reference query/model scope')
    meta={}
    for line in (source/'candidate_routes.tsv').read_text().splitlines():
        if line.startswith('meta\t'):
            _,key,value=line.split('\t');meta[key]=value
    bind(source/'routes.json',meta['input_sha256'])
    fixed_path=base/'fixed_site_state_v2.json';fixed=json.loads(fixed_path.read_text())
    for name,value in fixed['files'].items():bind(ROOT/name,value)
    proof_paths=[ROOT/f'data/netlist/lut_route_probes_20261023_v{v}/verification.json' for v in (1,2)]
    proofs=[json.loads(path.read_text()) for path in proof_paths]
    for path,proof in zip(proof_paths,proofs):
        for name,value in proof['files'].items():bind(path.parent/name,value)
    if not proofs[0]['no_site_drc_errors'] or proofs[1]['status']!='sampled_lut_equations_and_output_muxes_verified':
        raise ValueError('Physical probe verification missing')
    equations={v['pip']:v for v in proofs[0]['checks']};requirements={}
    for probe in proofs[1]['checks']:
        if not probe['equation_matches'] or probe['pip'] in requirements:raise ValueError('Invalid/duplicate probe')
        equation=equations[probe['pip']];bel=equation['bel'];signals=[bel+'/O6'];values=[]
        if probe['output_mux']:
            mux,setting=probe['output_mux'].split(':')
            if setting!='D6':raise ValueError('Unsupported verified MUX setting')
            signals.append(mux+'/OUT');values.append((mux,setting))
        requirements[probe['pip']]={'signal_resources':signals,
            'configuration_bits':[(bel+'/INIT',MASK,truth_table(equation['expected_equation']))],
            'configuration_values':values}
    if len(requirements)!=14:raise ValueError('Verified-instance domain differs')
    fixed_bits=[r['configuration_bits'] for r in fixed['fixed_functional_luts']]
    fixed_bits.extend(r['configuration_bits'] for r in fixed['unoccupied_constant_configurations']
                      if r['status']=='isolated_vivado_conflict_verified')
    resources={field for field,mask,value in fixed_bits};values=set()
    for r in requirements.values():
        resources.update(r['signal_resources']);resources.update(field for field,mask,value in r['configuration_bits'])
        resources.update(field for field,value in r['configuration_values']);values.update(value for field,value in r['configuration_values'])
    resource_names=sorted(resources);value_names=sorted(values)
    resource_ids={name:i for i,name in enumerate(resource_names)};value_ids={name:i for i,name in enumerate(value_names)}
    for field,mask,value in fixed_bits:
        if not isinstance(mask,int) or not isinstance(value,int) or not 0<=mask<=MASK or value<0 or value&~mask:
            raise ValueError('Invalid 64-bit fixed configuration')
    fixture=ROOT/f'data/derived/native_region_{a.mode}_inputs_20261023_v2'
    manifest=json.loads((fixture/'manifest.json').read_text());bind(fixture/'manifest.json')
    for name,value in manifest['files'].items():bind(name,value)
    for name,value in manifest['outputs'].items():bind(fixture/name,value)
    image=PackedGraph(manifest['image']);tile_ids={image.text(v[0]):i for i,v in enumerate(image.tiles)}
    strings={image.text(i):i for i in range(len(image.str_offsets)-1)}
    capture_path=ROOT/'data/raw/region_u280_20261022_v1/capture.json';capture=json.loads(capture_path.read_text())
    graph_path=ROOT/capture['graph']['path'];bind(graph_path,meta['graph_sha256']);raw_pips={}
    with graph_path.open() as stream:
        for line in stream:
            if not line.startswith('pip\t'):continue
            name=line.split('\t',2)[1]
            if name in requirements:
                f=line.rstrip('\n').split('\t')
                if name in raw_pips:raise ValueError('Duplicate physical PIP')
                raw_pips[name]=(f[2],f[3],properties(f[4:]))
    if set(raw_pips)!=set(requirements):raise ValueError('Verified PIPs absent from real capture')
    numeric={}
    for name,req in sorted(requirements.items()):
        tile,suffix=name.split('/',1);t=tile_ids[tile];p_id=strings[suffix]
        up,down,attrs=raw_pips[name]
        if attrs.get('IS_PSEUDO')!='1' or attrs.get('IS_DIRECTIONAL')!='1':raise ValueError('Unsupported evidenced PIP direction/kind')
        if not up.startswith(tile+'/') or not down.startswith(tile+'/'):raise ValueError('PIP endpoint tile differs')
        u=strings[up.split('/',1)[1]];d=strings[down.split('/',1)[1]]
        src=image.aliases[t,u];dst=image.aliases[t,d]
        matches=[e for e in image.numeric_neighbors(src) if e[:5]==(dst,t,p_id,u,d) and e[6]==0]
        if len(matches)!=1 or image.attrs(matches[0][5])!={k:v for k,v in attrs.items() if k!='TILE'}:
            raise ValueError('Verified directed PIP/attributes differ in packed image')
        numeric[name]={'tile_id':t,'pip_id':p_id,'signal_resources':[resource_ids[r] for r in req['signal_resources']],
            'configuration_bits':[[resource_ids[r],m,v] for r,m,v in req['configuration_bits']],
            'configuration_values':[[resource_ids[r],value_ids[v]] for r,v in req['configuration_values']]}
    pseudo=[i for i in range(len(image.attr_offsets)-1) if image.attrs(i).get('IS_PSEUDO')=='1']
    lines=['NATIVE_SITES_V1',f'{len(resource_names)} {len(value_names)} {len(image.attr_offsets)-1}',str(len(fixed_bits))]
    lines.extend(f'{resource_ids[r]} {m} {v}' for r,m,v in fixed_bits)
    lines.extend(['0','0',str(len(numeric))]) # fixed signal and category counts
    for n in numeric.values():
        lines.append(f'{n["tile_id"]} {n["pip_id"]}');lines.append(str(len(n['signal_resources'])))
        lines.extend(map(str,n['signal_resources']));lines.append(str(len(n['configuration_bits'])))
        lines.extend(' '.join(map(str,row)) for row in n['configuration_bits']);lines.append(str(len(n['configuration_values'])))
        lines.extend(' '.join(map(str,row)) for row in n['configuration_values'])
    lines.append(str(len(pseudo)));lines.extend(map(str,pseudo))
    a.output.mkdir(parents=True,exist_ok=False);site_file=a.output/'sites.txt';site_file.write_text('\n'.join(lines)+'\n')
    write_new(a.output/'symbols.json',{'resources':resource_names,'values':value_names,'requirements':numeric})
    for path in [Path(__file__),ROOT/'src/packed_graph.py',ROOT/'src/lut_equation.py',ROOT/'adapters/import_vivado.py']:bind(path)
    write_new(a.output/'manifest.json',{'status':'prepared_tested_instances_only','mode':a.mode,'image':manifest['image'],
        'routing_fixture':str(fixture/'routing.txt'),'queries':1062,'verified_instances':len(numeric),
        'functional_lut_records':len(fixed['fixed_functional_luts']),'fixed_bit_records':len(fixed_bits),
        'resource_symbols':len(resource_names),'files':files,
        'outputs':{p.name:digest(p) for p in (site_file,a.output/'symbols.json')},
        'limitations':['Only the same14 tested physical instances as the physically verified Python workload.',
            'Other pseudo requirements remain unknown; inferred v3 table is not consumed.']})
    print(json.dumps({'output':str(a.output),'mode':a.mode,'verified_instances':len(numeric),'fixed_bits':len(fixed_bits)}))


if __name__=='__main__':main()
