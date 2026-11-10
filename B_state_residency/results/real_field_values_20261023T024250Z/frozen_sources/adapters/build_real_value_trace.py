"""Instrument actual field values in a separate frozen serial index-LRU build."""
import json
import re
import subprocess
from pathlib import Path
from prepare_real import ROOT, UPSTREAM, sha


HELPERS = '''    template<class T> struct BWriteField {
        LabelLease lease;
        T NodeDyn::* member;
        int node, field, line;
        BWriteField(LabelLease&& handle,T NodeDyn::* m,int n,int f,int l)
            : lease(std::move(handle)),member(m),node(n),field(f),line(l) {}
        void operator=(T value) {
            lease.value->*member = value;
            bvalues::emit(node,line,unsigned(field),true,value,tl_dyn[node].hist);
        }
    };
    template<class T> static BWriteField<T> bWriteLabel(int node,T NodeDyn::* member,int field,int line) {
        return BWriteField<T>(TLD(node),member,node,field,line);
    }
    template<class T> static T bReadLabel(int node,T NodeDyn::* member,int field,int line) {
        auto handle = TLRead(node);
        T value = handle.lease.value->*member;
        bvalues::emit(node,line,unsigned(field),false,value,tl_dyn[node].hist);
        return value;
    }
'''


def generate(text):
    fields = {'lb': 0, 'upstream': 1, 'prev': 2, 'visited': 3, 'target': 4}
    edits, sites = [], []
    for match in re.finditer(r'\b(TLD|TLRead)\(', text):
        end, depth = match.end(), 1
        while depth:
            depth += (text[end] == '(') - (text[end] == ')')
            end += 1
        field = re.match(r'->(lb|upstream|prev|visited|target)\b', text[end:])
        if not field:
            continue
        name = field[1]
        line = text[:match.start()].count('\n') + 1
        write = match[1] == 'TLD'
        following = text[end+field.end():].lstrip()
        if write != bool(re.match(r'=(?!=)', following)):
            raise ValueError('Unexpected access classification')
        node = text[match.end():end-1]
        replacement = f'b{"Write" if write else "Read"}Label({node}, &NodeDyn::{name}, {fields[name]}, {line})'
        edits.append((match.start(), end+field.end(), replacement))
        sites.append(dict(line=line, field=name, write=write, node_expression=node))
    if (sum(not site['write'] for site in sites), sum(site['write'] for site in sites)) != (18, 10):
        raise ValueError('Field site coverage changed')
    for start, end, replacement in reversed(edits):
        text = text[:start] + replacement + text[end:]
    def replace(old, new):
        nonlocal text
        if text.count(old) != 1:
            raise ValueError('Source anchor changed: '+old)
        text = text.replace(old, new)
    replace('    SparseLabels bSerialLabels;', HELPERS+'    SparseLabels bSerialLabels;')
    signature = '    void routeIndirectConnection(int connIdx, long long budget = -1) {'
    replace(signature, signature+'\n        bvalues::Attempt b_value_attempt(routeIteration, connIdx, connections[connIdx].connId, connections[connIdx].netIdx);')
    replace('    router.bConfigureLabels();', '''    if (router.parPart || router.parIter1 || router.overlapT || router.batchMin > 0 || router.lazy)
        throw std::runtime_error("Value tracing requires frozen serial configuration");
    bvalues::init();
    router.bConfigureLabels();
    if (!router.bSerialPaged) throw std::runtime_error("Value tracing requires serial paging");''')
    replace('    router.bReportLabels();', '    router.bReportLabels();\n    bvalues::finish();')
    return '#include "real_values_trace.hpp"\n'+text, sites


def main():
    base = ROOT / 'build/resident_index_lru_v1'
    frozen = json.loads((base/'build.json').read_text())
    if sha(base/'router.cpp') != frozen['source_sha256']:
        raise ValueError('Frozen index-LRU source changed')
    text, sites = generate((base/'router.cpp').read_text())
    out = ROOT / 'build/real_values_trace_v1'
    out.mkdir(exist_ok=False)
    source = out/'router.cpp'; source.write_text(text)
    binary = out/'router'
    command = ['g++','-std=c++17','-O3','-g','-fno-fast-math','-fno-omit-frame-pointer','-no-pie','-pthread',
               '-I',str(ROOT/'adapters'),'-I',str(UPSTREAM/'cpp_router/include'),str(source),'-o',str(binary)]
    with (out/'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=240)
    inputs = [Path(__file__).resolve(), ROOT/'adapters/real_values_trace.hpp', base/'router.cpp', base/'build.json']
    (out/'build.json').write_text(json.dumps(dict(source_sha256=sha(source), binary_sha256=sha(binary),
        command=command, field_sites=sites, inputs={str(p):sha(p) for p in inputs}), indent=2)+'\n')
    print(out, flush=True)


if __name__ == '__main__':
    main()
