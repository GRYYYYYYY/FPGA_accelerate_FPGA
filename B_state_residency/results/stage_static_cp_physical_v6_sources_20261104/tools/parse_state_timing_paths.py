"""Parse literal Vivado setup/hold data paths, retaining physical locations."""
from collections import Counter, defaultdict
import hashlib
import re


def rounded_sum_matches(values, total):
    # All report numbers have three decimals. Account for rounding each term
    # and the separately rounded total, without accepting missing cell rows.
    return abs(sum(values)-total) <= 0.0005*(len(values)+1)+1e-8


def parse_block(block):
    def field(pattern):
        match = re.search(pattern,block,re.M)
        assert match, pattern
        return match

    kind = field(r'^[ \t]+Path Type:[ \t]+(Setup|Hold)\b')[1]
    source = field(r'^[ \t]+Source:[ \t]+(\S+)')[1]
    destination = field(r'^[ \t]+Destination:[ \t]+(\S+)')[1]
    group = field(r'^[ \t]+Path Group:[ \t]+(\S+)')[1]
    slack = float(field(r'^Slack \([^)]+\)[ \t]*:[ \t]*(-?[\d.]+)ns')[1])
    requirement = float(field(r'^[ \t]+Requirement:[ \t]+(-?[\d.]+)ns')[1])
    delay = field(r'Data Path Delay:[ \t]+([\d.]+)ns[ \t]+\(logic[ \t]+([\d.]+)ns.*?route[ \t]+([\d.]+)ns')
    data_delay, logic_delay, net_delay = map(float,(delay[1],delay[2],delay[3]))
    assert rounded_sum_matches([logic_delay,net_delay],data_delay)
    levels = field(r'^[ \t]+Logic Levels:[ \t]+(\d+)(?:[ \t]+\(([^)]+)\))?[ \t]*$')
    entries = re.findall(r'([A-Z][A-Z0-9_]*)=(\d+)',levels[2] or '')
    assert ' '.join(f'{name}={count}' for name,count in entries)==(levels[2] or '').strip()
    declared = {name:int(count) for name,count in entries}
    assert len(entries)==len(declared) and sum(declared.values())==int(levels[1])
    sections = re.split(r'^[ \t]*-{5,}(?:[ \t]+-{5,})?[ \t]*$',block,flags=re.M)
    assert len(sections)>=5, 'Missing timing table separators'
    launch_clock, data = sections[1], sections[2]
    assert re.search(r'[rf][ \t]+'+re.escape(source)+r'[ \t]*$',launch_clock,re.M)
    assert re.search(r'[rf][ \t]+'+re.escape(destination)+r'[ \t]*$',data,re.M)
    pattern = (r'^[ \t]*(?:(\S+)[ \t]+)?([A-Z][A-Z0-9_]*)[ \t]+\(Prop_([^)]+)\)'
               r'[ \t]*\n?[ \t]*(-?\d+\.\d+)[ \t]+(-?\d+\.\d+)[ \t]+([rf])[ \t]+(\S+)[ \t]*$')
    rows = [dict(location=m[1],type=m[2],arc=m[3],delay_ns=float(m[4]),
                 arrival_ns=float(m[5]),edge=m[6],pin=m[7],cell=m[7].rsplit('/',1)[0])
            for m in re.finditer(pattern,data,re.M)]
    assert rows and rows[0]['cell']==source.rsplit('/',1)[0], 'Missing launch propagation row'
    launch, cells = rows[0], rows[1:]
    assert len(cells)==int(levels[1]) and dict(Counter(x['type'] for x in cells))==declared, 'Incomplete logic rows'
    assert rounded_sum_matches([x['delay_ns'] for x in rows],logic_delay), 'Logic delay mismatch'
    nets = [dict(fanout=int(m[1]),placement=m[2],delay_ns=float(m[3]),arrival_ns=float(m[4]),name=m[5])
            for m in re.finditer(r'^[ \t]+net \(fo=(\d+), ([^)]+)\)[ \t]+(-?\d+\.\d+)[ \t]+(-?\d+\.\d+)[ \t]+(\S+)[ \t]*$',data,re.M)]
    assert len(nets)==len(cells)+1, 'Incomplete data-net rows'
    assert rounded_sum_matches([x['delay_ns'] for x in nets],net_delay), 'Data-net delay mismatch'
    actual_delay = nets[-1]['arrival_ns']-launch['arrival_ns']+launch['delay_ns']
    assert abs(actual_delay-data_delay)<=0.00200001, 'Arrival/data delay mismatch'
    groups = defaultdict(lambda:dict(levels=0,logic_delay_ns=0.0))
    segments = []
    for cell in cells:
        hierarchy = cell['cell'].rsplit('/',1)[0] if '/' in cell['cell'] else '(top)'
        groups[hierarchy]['levels'] += 1
        groups[hierarchy]['logic_delay_ns'] += cell['delay_ns']
        if not segments or segments[-1]['hierarchy']!=hierarchy:
            segments.append(dict(hierarchy=hierarchy,levels=0))
        segments[-1]['levels'] += 1
    return dict(path_type=kind,path_group=group,source=source,destination=destination,
                requirement_ns=requirement,slack_ns=slack,data_delay_ns=data_delay,
                logic_delay_ns=logic_delay,net_delay_ns=net_delay,
                logic_levels=len(cells),primitive_counts=declared,launch_cell=launch,
                logic_cells=cells,data_nets=nets,net_placement_counts=dict(Counter(n['placement'] for n in nets)),
                hierarchy_totals=dict(groups),ordered_hierarchy_segments=segments,
                highest_fanout_data_nets=sorted(nets,key=lambda n:n['fanout'],reverse=True)[:10],
                largest_delay_data_nets=sorted(nets,key=lambda n:n['delay_ns'],reverse=True)[:10],
                literal_block_sha256=hashlib.sha256(block.encode()).hexdigest())


def parse_report(text, clock):
    starts = list(re.finditer(r'^Slack \(',text,re.M))
    assert starts, 'No reported timing paths'
    paths = []
    for i,start in enumerate(starts):
        block = text[start.start():starts[i+1].start() if i+1<len(starts) else len(text)]
        group = re.search(r'^[ \t]+Path Group:[ \t]+(\S+)',block,re.M)
        kind = re.search(r'^[ \t]+Path Type:[ \t]+(Setup|Hold)\b',block,re.M)
        if group and group[1]==clock and kind:
            paths.append(parse_block(block))
    assert {p['path_type'] for p in paths}=={'Setup','Hold'}, 'Missing requested clock setup/hold paths'
    return paths
