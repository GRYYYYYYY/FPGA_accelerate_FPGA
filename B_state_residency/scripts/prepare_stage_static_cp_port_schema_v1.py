"""Inventory the fixed OOC top interface without changing any DUT or host TB.

This is a fail-closed parser for this project's ANSI wire-only header, not a
general Verilog elaborator. Unknown declarations or expressions are rejected.
"""
import ast
import json
import re
from pathlib import Path
from host_edit_system_common_v1 import ROOT, BASE, read, sha


def integer(expression, parameters):
    def value(node):
        if isinstance(node, ast.Constant) and type(node.value) is int:
            return node.value
        if isinstance(node, ast.Name):
            return parameters[node.id]
        if isinstance(node, ast.BinOp) and isinstance(node.op, (ast.Add, ast.Sub)):
            a, b = value(node.left), value(node.right)
            return a + b if isinstance(node.op, ast.Add) else a - b
        raise ValueError('Unsupported width expression: ' + expression)
    return value(ast.parse(expression, mode='eval').body)


def balanced(text, opening):
    assert text[opening] == '('
    depth = 1
    for end in range(opening + 1, len(text)):
        if text[end] == '(':
            depth += 1
        elif text[end] == ')':
            depth -= 1
            if depth == 0:
                return text[opening + 1:end], end + 1
    raise ValueError('Unclosed parentheses')


def ports_from_header(text, parameters):
    clean = re.sub(r'/\*.*?\*/|//[^\n]*', '', text, flags=re.S)
    start = clean.index('module query_residency_system')
    parameter_start = clean.index('(', start)
    _, end = balanced(clean, parameter_start)
    header, _ = balanced(clean, clean.index('(', end))
    ports = []
    direction = None
    width = None
    for item in header.split(','):
        item = item.strip()
        declaration = re.fullmatch(r'(input|output)\s+wire\s*(\[[^]]+\])?\s*(\w+)', item)
        if declaration:
            direction, packed, name = declaration.groups()
            if packed:
                left, right = packed[1:-1].split(':')
                width = abs(integer(left, parameters) - integer(right, parameters)) + 1
            else:
                width = 1
        else:
            assert direction and width and re.fullmatch(r'\w+', item), item
            name = item
        assert name not in {p['name'] for p in ports}, name
        ports.append(dict(name=name, direction=direction, width=width))
    return ports


def connections(text):
    start = text.index('query_residency_system #(')
    _, end = balanced(text, text.index('(', start))
    assert re.match(r'\s*system\s*\(', text[end:])
    body, _ = balanced(text, text.index('(', end))
    result = {}
    while body.strip():
        match = re.match(r'\s*\.(\w+)\s*\(', body)
        assert match, body[:100]
        expression, end = balanced(body, match.end() - 1)
        name = match[1]
        assert name not in result
        result[name] = expression
        body = body[end:].strip()
        if body:
            assert body.startswith(',')
            body = body[1:]
    return result


def main():
    target = BASE / 'stage_static_cp_synth_v1'
    source = target / 'sources/query_residency_system.sv'
    tb = BASE / 'checkpoint_host_edit_system_v1/sources/tb_query_fault.sv'
    m = read(target / 'manifest.json')
    assert sha(source) == m['sources'][source.name]
    ports = ports_from_header(source.read_text(), m['parameters'])
    conn = connections(tb.read_text())
    assert set(conn).issubset({p['name'] for p in ports})
    for port in ports:
        port['host_expression'] = conn.get(port['name'])
        port['host_connected'] = port['name'] in conn
    report = dict(status='fixed_top_port_schema_prepared_not_simulated',
                  source=str(source), source_sha256=sha(source),
                  host_tb=str(tb), host_tb_sha256=sha(tb), generator_sha256=sha(__file__),
                  parameters=m['parameters'], ports=ports,
                  counts={d:dict(ports=sum(p['direction'] == d for p in ports),
                                 bits=sum(p['width'] for p in ports if p['direction'] == d),
                                 omitted=[p['name'] for p in ports if p['direction'] == d and not p['host_connected']])
                          for d in ['input', 'output']},
                  full_system_functional_netlist_validated=False,
                  scope='Interface inventory only. Omitted input pins require preserving original unconnected semantics; no forced defaults or removed monitors.')
    out = ROOT / 'results/stage_static_cp_port_schema_20261030.json'
    assert not out.exists()
    out.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print(json.dumps(report['counts'], indent=2))


if __name__ == '__main__':
    main()
