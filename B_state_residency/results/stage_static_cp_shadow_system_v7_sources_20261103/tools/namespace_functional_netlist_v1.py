"""Rename only module definitions and module instance types for a shadow DUT.

Never rewrite ports, nets, instance names, primitive types, strings or comments.
The accepted input is Vivado's parameter-free structural write_verilog format.
"""
import hashlib
import json
import re
import sys
from pathlib import Path

IDENT = r'(?:\\[^\s]+|[A-Za-z_$][A-Za-z_0-9$]*)'
TOKEN = re.compile(r'//[^\n]*|/\*.*?\*/|"(?:\\.|[^"\\])*"|' + IDENT + r'|[^\s]', re.S)


def namespace(text, prefix='shadow_gate_'):
    assert re.fullmatch(r'[A-Za-z_][A-Za-z_0-9]*', prefix)
    # Ignore lexical comments and strings while retaining exact source offsets.
    tokens = [m for m in TOKEN.finditer(text)
              if not m.group().startswith(('//', '/*', '"'))]
    definitions = {}
    for i, token in enumerate(tokens):
        if token.group() == 'module':
            name = tokens[i + 1].group()
            assert re.fullmatch(IDENT, name) and name not in definitions
            definitions[name] = prefix + str(len(definitions)) + '_' + name.lstrip('\\')
            # Generated names are simple identifiers; reject unusual escaped names.
            assert re.fullmatch(r'[A-Za-z_][A-Za-z_0-9$]*', definitions[name]), name
    assert 'query_residency_system' in definitions
    assert not set(definitions.values()).intersection(m.group() for m in tokens)
    replacements = []
    instances = {name: 0 for name in definitions}
    for i, token in enumerate(tokens):
        name = token.group()
        if name not in definitions:
            continue
        is_definition = i > 0 and tokens[i - 1].group() == 'module'
        is_instance = (i + 2 < len(tokens)
                       and re.fullmatch(IDENT, tokens[i + 1].group())
                       and tokens[i + 2].group() == '(')
        assert not (is_definition and is_instance)
        if is_definition or is_instance:
            replacements.append((token.start(), token.end(), definitions[name]))
            if is_instance:
                instances[name] += 1
        elif i + 1 < len(tokens) and tokens[i + 1].group() == '#':
            raise ValueError('Parameterized structural module instance unsupported: ' + name)
    assert len(replacements) == len(definitions) + sum(instances.values())
    result = text
    for start, end, new in reversed(replacements):
        result = result[:start] + new + result[end:]
    # Exact inverse establishes every byte outside the selected type tokens stays.
    inverse = {new: old for old, new in definitions.items()}
    restored = result
    inverse_spans = [m for m in TOKEN.finditer(result) if m.group() in inverse]
    assert len(inverse_spans) == len(replacements)
    for match in reversed(inverse_spans):
        restored = restored[:match.start()] + inverse[match.group()] + restored[match.end():]
    assert restored == text
    return result, dict(module_map=definitions, module_instance_counts=instances,
                        replacements=len(replacements), exact_inverse=True,
                        shadow_top=definitions['query_residency_system'])


def main():
    source, destination = map(Path, sys.argv[1:3])
    assert source.is_file() and not destination.exists()
    original = source.read_text()
    result, report = namespace(original)
    destination.write_text(result)
    report.update(source=str(source.resolve()), destination=str(destination.resolve()),
                  source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                  output_sha256=hashlib.sha256(destination.read_bytes()).hexdigest(),
                  status='namespace_prepared_not_compiled_or_simulated',
                  full_system_functional_netlist_validated=False)
    destination.with_suffix('.namespace.json').write_text(json.dumps(report, indent=2, sort_keys=True) + '\n')
    print('FUNCTIONAL_NETLIST_NAMESPACED', len(report['module_map']), report['replacements'])


if __name__ == '__main__':
    main()
