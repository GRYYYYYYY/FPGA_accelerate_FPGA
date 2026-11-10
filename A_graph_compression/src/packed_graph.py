"""Versioned little-endian, sectioned routing graph; no JSON in runtime lookup tables.

All static identity/property/alias data is retained and charged to file size.
AUDIT is shared provenance metadata, not a source of runtime adjacency.
"""
from collections import Counter, defaultdict
from copy import deepcopy
import json
from pathlib import Path
import struct

from canonical_graph import compare, signature, split_name, validate
from heldout import object_digest
from template_codec import family, normalize

MAGIC = b"AGRAPH01"
HEADER = struct.Struct("<8sIIII")
DIRECTORY = struct.Struct("<16sQQII")
FORMATS = {"STR_OFF": "Q", "ATTR_OFF": "Q", "ATTR_KV": "II", "TILE": "IIiiiI",
           "NODE": "IIIi", "ROOT": "III", "ALIAS": "III", "GRID": "iiI",
           "CSR_OFF": "Q", "CSR_EDGE": "7I", "TPL_OFF": "Q", "RULE": "ii5I",
           "INSTANCE": "i6I", "REMOVE": "I", "ADD": "ii5I", "PATCH": "II"}


def topology(rule):
    return signature({k: v for k, v in rule.items() if k != "attributes"})


def rule_plan(graph, bank, attribute_patches=True):
    adjacency = validate(graph)
    by_family = {tuple(t["family"]): tid for tid, t in bank["templates"].items()}
    used = sorted({by_family[family(graph, root)] for root in graph["roots"]
                   if family(graph, root) in by_family})
    template_ids = {tid: i for i, tid in enumerate(used)}
    templates = [bank["templates"][tid]["rules"] for tid in used]
    instances = []
    for root in sorted(graph["roots"]):
        actual = [normalize(graph, e) for e in adjacency[root]]
        tid = by_family.get(family(graph, root))
        if tid is None:
            instances.append({"template": -1, "remove": [], "add": actual, "patch": []})
            continue
        index = template_ids[tid]
        base = templates[index]
        key = topology if attribute_patches else signature
        expected = {key(r): r for r in actual}
        if len(expected) != len(actual) or len({key(r) for r in base}) != len(base):
            raise ValueError("Non-unique directed PIP rule identity")
        removed, patches = [], []
        for i, rule in enumerate(base):
            other = expected.pop(key(rule), None)
            if other is None:
                removed.append(i)
            elif rule["attributes"] != other["attributes"]:
                patches.append((i, other["attributes"]))
        instances.append({"template": index, "remove": removed, "add": list(expected.values()), "patch": patches})
    return templates, instances


def build_sections(graph, mode, bank=None, attribute_patches=True):
    validate(graph)
    if mode not in {"csr", "compact"}:
        raise ValueError("mode must be csr or compact")
    if mode == "compact":
        if bank is None or set(graph["roots"]) & set(bank["training_sources"]):
            raise ValueError("Missing bank or training/evaluation source overlap")
        templates, instances = rule_plan(graph, bank, attribute_patches)
    else:
        templates, instances = [], []
    props = set()
    def attrkey(attrs):
        return tuple(sorted(attrs.items()))
    for attrs in [*graph["tiles"].values(), *graph["nodes"].values()]:
        props.add(attrkey(attrs))
    for pip in graph["pips"].values():
        props.add(attrkey({k: v for k, v in pip["attributes"].items() if k != "TILE"}))
    for rules in templates:
        props.update(attrkey(r["attributes"]) for r in rules)
    attributes = sorted(props)
    attr_ids = {p: i for i, p in enumerate(attributes)}
    strings = set()
    for name in graph["nodes"]:
        strings.add(name)
    for name, attrs in graph["tiles"].items():
        strings.update([name, attrs["TYPE"]])
    for wire in graph["aliases"]:
        strings.add(split_name(wire)[1])
    for name in graph["pips"]:
        strings.add(split_name(name)[1])
    for rows in templates:
        for rule in rows:
            strings.update([rule["pip_suffix"], rule["src_wire"], rule["dst_wire"]])
    for pairs in attributes:
        for key, value in pairs:
            if not isinstance(key, str) or not isinstance(value, str):
                raise ValueError("Static properties must be lossless source strings")
            strings.update([key, value])
    strings = sorted(strings)
    sid = {s: i for i, s in enumerate(strings)}
    tiles, nodes, roots = map(sorted, (graph["tiles"], graph["nodes"], graph["roots"]))
    tile_ids, node_ids, source_rows = ({n: i for i, n in enumerate(names)} for names in (tiles, nodes, roots))
    sections = {}
    def rows(name, values):
        fmt = struct.Struct("<"+FORMATS[name])
        values = list(values)
        payload = b"".join(fmt.pack(*(v if isinstance(v, (list, tuple)) else (v,))) for v in values)
        sections[name] = (payload, len(values), fmt.size)
    def blob(name, value):
        sections[name] = (value, len(value), 1)
    offsets, payload = [0], bytearray()
    for value in strings:
        payload.extend(value.encode("utf-8")); offsets.append(len(payload))
    rows("STR_OFF", offsets); blob("STR_DATA", bytes(payload))
    offsets, pairs = [0], []
    for values in attributes:
        pairs.extend((sid[k], sid[v]) for k, v in values); offsets.append(len(pairs))
    rows("ATTR_OFF", offsets); rows("ATTR_KV", pairs)
    rows("TILE", [(sid[t], attr_ids[attrkey(graph['tiles'][t])], int(graph['tiles'][t]['COLUMN']),
                    int(graph['tiles'][t]['ROW']), int(graph['tiles'][t]['SLR_REGION_ID']), sid[graph['tiles'][t]['TYPE']]) for t in tiles])
    rows("NODE", [(sid[n], attr_ids[attrkey(graph['nodes'][n])], tile_ids[split_name(n)[0]], source_rows.get(n, -1)) for n in nodes])
    rows("ROOT", [(node_ids[n], graph['roots'][n]['pip_count'], graph['roots'][n]['child_count']) for n in roots])
    rows("ALIAS", sorted((tile_ids[split_name(w)[0]], sid[split_name(w)[1]], node_ids[n]) for w, n in graph['aliases'].items()))
    rows("GRID", sorted((int(a['COLUMN']), int(a['ROW']), tile_ids[t]) for t, a in graph['tiles'].items()))
    audit = {k: graph[k] for k in ['schema','dataset_kind','metadata','provenance','seed_tiles','selections']}
    # Identical provenance section in both formats; runtime never consults it.
    blob("AUDIT", signature(audit).encode())
    def encode_rule(rule):
        up, down = (rule['src_wire'], rule['dst_wire']) if rule['direction'] == 'forward' else (rule['dst_wire'], rule['src_wire'])
        return (*rule['tile_offset'], sid[rule['pip_suffix']], sid[up], sid[down], attr_ids[attrkey(rule['attributes'])], int(rule['direction']=='reverse'))
    if mode == 'csr':
        adjacency = defaultdict(list)
        for edge in graph['edges']:
            pip = graph['pips'][edge['pip']]
            attrs = {k:v for k,v in pip['attributes'].items() if k != 'TILE'}
            adjacency[edge['src']].append((node_ids[edge['dst']], tile_ids[pip['attributes']['TILE']], sid[split_name(edge['pip'])[1]],
                                          sid[split_name(pip['up_wire'])[1]], sid[split_name(pip['down_wire'])[1]], attr_ids[attrkey(attrs)], int(edge['direction']=='reverse')))
        offsets, records = [0], []
        for root in roots:
            records.extend(sorted(adjacency[root])); offsets.append(len(records))
        rows('CSR_OFF', offsets); rows('CSR_EDGE', records)
    else:
        offsets, records = [0], []
        for ruleset in templates:
            records.extend(encode_rule(r) for r in ruleset); offsets.append(len(records))
        rows('TPL_OFF', offsets); rows('RULE', records)
        removed, added, patches, records = [], [], [], []
        for instance in instances:
            records.append((instance['template'],len(removed),len(instance['remove']),len(added),len(instance['add']),len(patches),len(instance['patch'])))
            removed.extend(instance['remove'])
            added.extend(encode_rule(r) for r in instance['add'])
            patches.extend((i,attr_ids[attrkey(a)]) for i,a in instance['patch'])
        rows('INSTANCE', records); rows('REMOVE', removed); rows('ADD', added); rows('PATCH', patches)
    return sections


def write_packed(path, graph, mode, bank=None, attribute_patches=True):
    sections = build_sections(graph, mode, bank, attribute_patches)
    align = lambda n: (n+63)//64*64
    cursor = align(HEADER.size+DIRECTORY.size*len(sections))
    directory, layout = [], {}
    for name, (payload,count,width) in sections.items():
        directory.append(DIRECTORY.pack(name.encode(),cursor,len(payload),count,width))
        layout[name] = {'offset':cursor,'bytes':len(payload),'count':count,'record_bytes':width}
        cursor = align(cursor+len(payload))
    data = bytearray(cursor)
    data[:HEADER.size] = HEADER.pack(MAGIC,1,int(mode=='compact'),0x01020304,len(sections))
    data[HEADER.size:HEADER.size+len(directory)*DIRECTORY.size] = b''.join(directory)
    for name,(payload,_,_) in sections.items():
        start=layout[name]['offset']; data[start:start+len(payload)]=payload
    path = Path(path); path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('xb') as f:f.write(data)
    return {'mode':mode,'file_bytes':len(data),'section_bytes':sum(x['bytes'] for x in layout.values()),
            'header_directory_padding_bytes':len(data)-sum(x['bytes'] for x in layout.values()),'sections':layout,
            'bank_sha256':object_digest(bank) if bank else None,'attribute_patches':attribute_patches if mode=='compact' else None}


class PackedGraph:
    """Strict binary reader. Native/hardware readers use the same fixed records."""
    def __init__(self,path):
        self.data=Path(path).read_bytes(); self.layout={}
        if len(self.data)<HEADER.size: raise ValueError('Truncated header')
        magic,version,self.mode,endian,n=HEADER.unpack_from(self.data)
        if (magic,version,endian)!=(MAGIC,1,0x01020304) or self.mode not in (0,1): raise ValueError('Unsupported packed format')
        if HEADER.size+n*DIRECTORY.size>len(self.data): raise ValueError('Truncated directory')
        occupied=[]
        for i in range(n):
            name,offset,size,count,width=DIRECTORY.unpack_from(self.data,HEADER.size+i*DIRECTORY.size)
            name=name.rstrip(b'\0').decode('ascii')
            if name in self.layout or name not in {*FORMATS,'STR_DATA','AUDIT'}: raise ValueError('Unknown/duplicate section')
            expected=struct.calcsize('<'+FORMATS[name]) if name in FORMATS else 1
            if width!=expected or count*width!=size or offset%64 or offset<HEADER.size+n*DIRECTORY.size or offset+size>len(self.data): raise ValueError('Invalid section bounds/shape')
            self.layout[name]=(offset,size,count,width)
            if size:occupied.append((offset,offset+size))
        if any(a[1]>b[0] for a,b in zip(sorted(occupied),sorted(occupied)[1:])):raise ValueError('Overlapping sections')
        end=max([HEADER.size+n*DIRECTORY.size]+[o+s for o,s,_,_ in self.layout.values()])
        if len(self.data)!=(end+63)//64*64:raise ValueError('Truncated or extra trailing data')
        required={'STR_OFF','STR_DATA','ATTR_OFF','ATTR_KV','TILE','NODE','ROOT','ALIAS','GRID','AUDIT'}
        required |= {'CSR_OFF','CSR_EDGE'} if not self.mode else {'TPL_OFF','RULE','INSTANCE','REMOVE','ADD','PATCH'}
        if set(self.layout)!=required: raise ValueError('Missing/unexpected sections')
        self.str_offsets=self.table('STR_OFF'); self.attr_offsets=self.table('ATTR_OFF')
        for offsets,total in [(self.str_offsets,self.layout['STR_DATA'][1]),(self.attr_offsets,self.layout['ATTR_KV'][2])]:
            values=[v[0] for v in offsets]
            if not values or values[0]!=0 or values[-1]!=total or values!=sorted(values):raise ValueError('Invalid pool offsets')
        self.tiles=self.table('TILE'); self.nodes=self.table('NODE'); self.roots=self.table('ROOT')
        self.aliases={(t,w):node for t,w,node in self.table('ALIAS')}
        self.grid={(x,y):tile for x,y,tile in self.table('GRID')}
        if len(self.aliases)!=self.layout['ALIAS'][2] or len(self.grid)!=self.layout['GRID'][2]:raise ValueError('Duplicate alias/grid key')
        self._check_runtime()

    def table(self,name):
        offset,size,_,_=self.layout[name]
        return list(struct.iter_unpack('<'+FORMATS[name],self.data[offset:offset+size]))

    def text(self,sid):
        if not 0<=sid<len(self.str_offsets)-1:raise ValueError('String ID out of range')
        base=self.layout['STR_DATA'][0]; lo=self.str_offsets[sid][0]; hi=self.str_offsets[sid+1][0]
        return self.data[base+lo:base+hi].decode('utf-8')

    def attrs(self,aid):
        if not 0<=aid<len(self.attr_offsets)-1:raise ValueError('Attribute ID out of range')
        lo=self.attr_offsets[aid][0]; hi=self.attr_offsets[aid+1][0]
        base=self.layout['ATTR_KV'][0]; pairs=struct.iter_unpack('<II',self.data[base+lo*8:base+hi*8])
        result={}
        for k,v in pairs:
            key=self.text(k)
            if key in result:raise ValueError('Duplicate attribute key')
            result[key]=self.text(v)
        return result

    def _check_runtime(self):
        for i,(name,attrs,anchor,row) in enumerate(self.nodes):
            self.text(name); self.attrs(attrs)
            if not 0<=anchor<len(self.tiles) or row < -1 or row>=len(self.roots):raise ValueError('Invalid node anchor/source row')
            if row>=0 and self.roots[row][0]!=i:raise ValueError('Inconsistent source index')
        for i,(node,_,_) in enumerate(self.roots):
            if not 0<=node<len(self.nodes) or self.nodes[node][3]!=i:raise ValueError('Inconsistent root ID')
        for name,attrs,_,_,_,ty in self.tiles:self.text(name);self.attrs(attrs);self.text(ty)
        for (tile,wire),node in self.aliases.items():
            if not 0<=tile<len(self.tiles) or not 0<=node<len(self.nodes):raise ValueError('Invalid alias reference')
            self.text(wire)
        for point,tile in self.grid.items():
            if not 0<=tile<len(self.tiles) or point!=self.tiles[tile][2:4]:raise ValueError('Invalid grid entry')
        if not self.mode:
            self.offsets=self.table('CSR_OFF');self.edges=self.table('CSR_EDGE')
            if len(self.offsets)!=len(self.roots)+1:raise ValueError('CSR source count differs')
            self.check_offsets(self.offsets,len(self.edges))
        else:
            self.offsets=self.table('TPL_OFF');self.rules=self.table('RULE');self.instances=self.table('INSTANCE')
            self.removed=self.table('REMOVE');self.added=self.table('ADD');self.patched=self.table('PATCH')
            self.check_offsets(self.offsets,len(self.rules))
            if len(self.instances)!=len(self.roots):raise ValueError('Instance count differs')
            for tid,rs,rc,ads,adc,ps,pc in self.instances:
                if tid < -1 or tid >= len(self.offsets)-1:raise ValueError('Bad template ID')
                if rs+rc>len(self.removed) or ads+adc>len(self.added) or ps+pc>len(self.patched):raise ValueError('Bad exception range')
                limit=0 if tid<0 else self.offsets[tid+1][0]-self.offsets[tid][0]
                removes=[x[0] for x in self.removed[rs:rs+rc]]; patches=[x[0] for x in self.patched[ps:ps+pc]]
                if len(set(removes))!=rc or len(set(patches))!=pc or set(removes)&set(patches):raise ValueError('Conflicting/duplicate exception index')
                if any(i>=limit for i in removes+patches):raise ValueError('Exception index out of range')

    @staticmethod
    def check_offsets(rows,total):
        values=[r[0] for r in rows]
        if not values or values[0]!=0 or values[-1]!=total or values!=sorted(values):raise ValueError('Bad adjacency offsets')

    def numeric_neighbors(self,node):
        if not 0<=node<len(self.nodes):raise ValueError('Node ID out of range')
        row=self.nodes[node][3]
        if row<0:raise KeyError('Adjacency not exported')
        if not self.mode:return list(self.edges[self.offsets[row][0]:self.offsets[row+1][0]])
        tid,rs,rc,ads,adc,ps,pc=self.instances[row]
        removed={x[0] for x in self.removed[rs:rs+rc]}; patched=dict(self.patched[ps:ps+pc])
        rules=[]
        if tid>=0:
            for i,rule in enumerate(self.rules[self.offsets[tid][0]:self.offsets[tid+1][0]]):
                if i not in removed:rules.append((*rule[:5],patched.get(i,rule[5]),rule[6]))
        rules.extend(self.added[ads:ads+adc])
        anchor=self.tiles[self.nodes[node][2]]; result=[]
        for dx,dy,pip,up,down,attr,direction in rules:
            tile=self.grid[(anchor[2]+dx,anchor[3]+dy)]
            sw,dw=(down,up) if direction else (up,down)
            if self.aliases[tile,sw]!=node:raise ValueError('Wrong canonical source')
            result.append((self.aliases[tile,dw],tile,pip,up,down,attr,direction))
        return sorted(result)

    def decoded_neighbors(self,node):
        result=[]
        for dst,tile,pip,up,down,attr,direction in self.numeric_neighbors(node):
            if direction not in (0,1) or not 0<=dst<len(self.nodes) or not 0<=tile<len(self.tiles):raise ValueError('Invalid edge IDs')
            tn=self.text(self.tiles[tile][0]);un=tn+'/'+self.text(up);dn=tn+'/'+self.text(down)
            sw,dw=(dn,un) if direction else (un,dn)
            edge={'src':self.text(self.nodes[node][0]),'dst':self.text(self.nodes[dst][0]),'pip':tn+'/'+self.text(pip),
                  'src_wire':sw,'dst_wire':dw,'direction':'reverse' if direction else 'forward'}
            result.append((edge,{'up_wire':un,'down_wire':dn,'attributes':{**self.attrs(attr),'TILE':tn}}))
        return result

    def materialize(self):
        off,size,_,_=self.layout['AUDIT'];graph=json.loads(self.data[off:off+size])
        graph.update(tiles={self.text(t[0]):self.attrs(t[1]) for t in self.tiles},
                     nodes={self.text(n[0]):self.attrs(n[1]) for n in self.nodes},
                     aliases={self.text(self.tiles[t][0])+'/'+self.text(w):self.text(self.nodes[n][0]) for (t,w),n in self.aliases.items()},
                     roots={},pips={},edges=[],oracle_children={})
        for node,pc,cc in self.roots:
            name=self.text(self.nodes[node][0]);graph['roots'][name]={'pip_count':pc,'child_count':cc}
            children=set()
            for edge,pip in self.decoded_neighbors(node):
                if edge['pip'] in graph['pips'] and graph['pips'][edge['pip']]!=pip:raise ValueError('Conflicting PIP properties')
                graph['pips'][edge['pip']]=pip;graph['edges'].append(edge);children.add(edge['dst'])
            graph['oracle_children'][name]=sorted(children)
        return graph
