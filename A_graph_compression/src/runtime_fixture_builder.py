"""Build runtime input payloads from loaded graph/evidence, without hidden caches.

Callers must validate provenance before supplying objects. This module does not
promote inferred instances or provide a physical-legality certificate.
"""
from netlist import ownership
from lut_equation import truth_table, MASK


def build_runtime_payloads(image, snapshot, queries, fixed, proofs, pip_records):
    names=[image.text(n[0]) for n in image.nodes]
    if names!=sorted(set(names)):raise ValueError('Node IDs do not preserve canonical lexical order')
    node_ids={n:i for i,n in enumerate(names)}
    strings={image.text(i):i for i in range(len(image.str_offsets)-1)}
    tiles={image.text(t[0]):i for i,t in enumerate(image.tiles)}
    net_names=[q['net'] for q in queries]
    if len(set(net_names))!=len(net_names):raise ValueError('Duplicate net queries')
    protected,pips=ownership(snapshot,net_names)
    protected_ids=sorted(node_ids[n] for n in protected if n in node_ids)
    protected_pips=[]
    for name in pips:
        tile,suffix=name.split('/',1)
        if tile in tiles and suffix in strings:protected_pips.append((tiles[tile],strings[suffix]))
    blocked_attrs=[]
    for aid in range(len(image.attr_offsets)-1):
        attrs=image.attrs(aid)
        if any(attrs.get(k)=='1' for k in ('IS_EXCLUDED_PIP','IS_TEST_PIP')):blocked_attrs.append(aid)
    numeric=[{'net_id':i,'net':q['net'],'source':node_ids[q['source']],
              'sinks':[node_ids[n] for n in q['sinks']]} for i,q in enumerate(queries)]
    lines=['NATIVE_ROUTING_V1',str(len(names)),str(len(protected_ids)),*map(str,protected_ids),
           str(len(protected_pips)),*[f'{t} {p}' for t,p in sorted(protected_pips)],
           str(len(blocked_attrs)),*map(str,blocked_attrs),str(len(numeric))]
    lines.extend(' '.join(map(str,[q['net_id'],q['source'],len(q['sinks']),*q['sinks']])) for q in numeric)
    routing_text='\n'.join(lines)+'\n'
    numeric_queries=numeric
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
    numeric={}
    for name,req in sorted(requirements.items()):
        tile,suffix=name.split('/',1);t=tiles[tile];p_id=strings[suffix]
        raw=pip_records[name];up,down,attrs=raw['up_wire'],raw['down_wire'],raw['attributes']
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
    return {'routing_text':routing_text,'sites_text':'\n'.join(lines)+'\n','queries':numeric_queries,
            'symbols':{'resources':resource_names,'values':value_names,'requirements':numeric},
            'counts':{'queries':len(queries),'nodes':len(names),'protected_nodes':len(protected_ids),
                      'protected_pips':len(protected_pips),'fixed_bits':len(fixed_bits),'verified_instances':len(numeric)}}
