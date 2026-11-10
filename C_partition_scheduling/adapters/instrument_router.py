"""Generate an isolated, hash-pinned CPU router; never edit the source snapshot."""
from pathlib import Path
import hashlib
import json
import subprocess

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = ROOT.parent / '_shared/assets/gpu_router_original/rewrite/cpp_router'
SOURCE_SHA256 = 'cbd6e0b810a46ca06b0058ee7f2318a1862f66c64178bf27f0d6b574e5bf6826'


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as f:
        for block in iter(lambda: f.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def cpu_source():
    source = UPSTREAM / 'src/main.cpp'
    if sha(source) != SOURCE_SHA256:
        raise ValueError('Upstream changed; review instrumentation anchors before updating its hash')
    s = source.read_text()
    # Upstream CPU-only build references CUDA-only members in an unused JNI cleanup method.
    anchor = '        drop(floodCong); drop(floodCongShare); drop(shareMark);'
    if s.count(anchor) != 1:
        raise ValueError('CPU compatibility anchor changed')
    return s.replace(anchor, '#ifdef WITH_CUDA\n' + anchor + '\n#endif')


def generate():
    s = cpu_source()

    def replace(old, new):
        nonlocal s
        if s.count(old) != 1:
            raise ValueError(f'Instrumentation anchor not unique: {old[:90]}')
        s = s.replace(old, new, 1)

    replace('namespace rw =', '#include "trace.hpp"\n\nnamespace rw =')
    replace('    void routeIndirectConnection(int connIdx, long long budget = -1) {',
            '''    void routeIndirectConnection(int connIdx, long long budget = -1) {
        ctrace::Attempt cAttempt;
        const bool cProbe = budget == -1 && rwEnvI("C_CPU_BUDGET", 0) > 0;
        if (cProbe) budget = rwEnvI("C_CPU_BUDGET", 0);''')
    replace('static inline NodeDyn& TLD(int id) { return',
            'static inline NodeDyn& TLD(int id) { ctrace::label(id); return')
    for signature, hook in [
        ('void incrementUser(int id, int nw) {', 'ctrace::occ(id);'),
        ('void decrementUser(int id, int nw) {', 'ctrace::occ(id);'),
        ('void push(State& st, int child, float newPartial, float newTotal, bool lookahead) {', 'ctrace::write(child);'),
        ('void setAllTargets(Connection& c, State& st) {',
         'ctrace::write(c.sinkRnode); for (int id : c.altSinks) ctrace::write(id);'),
    ]:
        replace(signature, signature + '\n        ' + hook)
    replace('        TLD(childRnode).prev = rnode;', '        ctrace::write(childRnode);\n        TLD(childRnode).prev = rnode;')
    replace('            int childRNode = kids[ki];',
            '            int childRNode = kids[ki];\n            ctrace::edge(rnode, childRNode);')
    replace('        lastAborted = aborted;   // caller floods',
            '''        cTraceFinish(cAttempt, connIdx, budget, pops, found, aborted, corridor);
        if (cProbe && aborted) {
            c.xMinBB = oxmin; c.xMaxBB = oxmax; c.yMinBB = oymin; c.yMaxBB = oymax;
            routeIndirectConnection(connIdx, 0); // explicit unbudgeted CPU retry, same input constraints
            return;
        }
        lastAborted = aborted;   // caller floods''')
    replace('    void routeCpuLoop() {', '    void routeCpuLoop() {\n        cTracePartitions();')
    replace('    void writeResult(const std::string& path) {',
            '    #include "router_hooks.inc"\n\n    void writeResult(const std::string& path) {')
    replace('    Router router;\n    router.load(argv[1]);', '''    if (const char* path = std::getenv("C_TRACE_PATH")) {
        ctrace::output.open(path);
        if (!ctrace::output) throw std::runtime_error("cannot open C_TRACE_PATH");
        ctrace::limit = rwEnvI("C_TRACE_LIMIT", 2000);
        ctrace::cap = rwEnvI("C_TRACE_CAP", 200000);
    }
    if (const char* path = std::getenv("C_METRICS_PATH")) ctrace::metricsPath = path;
    Router router;
    router.load(argv[1]);
    {
        std::unordered_set<long long> keys;
        for (int i=0; i<router.numNodes(); ++i) {
            if (router.ns[i].tileAddr < 0 || router.nc[i].wireIndex < 0 ||
                router.nc[i].wireIndex > 0xFFFFF || !keys.insert(router.keyOf(i)).second)
                throw std::runtime_error("invalid or duplicate canonical node key");
        }
    }''')
    replace('    router.writeResult(argv[2]);', '    router.cTraceVerify();\n    router.writeResult(argv[2]);')
    replace('    router.routeIndirectConnectionsIteratively();\n    auto t2 = clk::now();',
            '''    auto cRouteStart = clk::now();
    router.routeIndirectConnectionsIteratively();
    ctrace::routeNs = std::chrono::duration_cast<std::chrono::nanoseconds>(clk::now()-cRouteStart).count();
    auto t2 = clk::now();''')
    return s


def build():
    directory = ROOT / 'build/cpu_trace'
    directory.mkdir(parents=True, exist_ok=True)
    generated = directory / 'main.cpp'
    baseline = directory / 'baseline.cpp'
    content = generate()
    if not generated.exists() or generated.read_text() != content:
        generated.write_text(content)
    if not baseline.exists() or baseline.read_text() != cpu_source():
        baseline.write_text(cpu_source())
    inputs = [generated, baseline, Path(__file__), ROOT / 'adapters/trace.hpp', ROOT / 'adapters/router_hooks.inc',
              UPSTREAM / 'src/main.cpp', *sorted((UPSTREAM / 'include').glob('*.hpp'))]
    hashes = {str(p.relative_to(ROOT)) if p.is_relative_to(ROOT) else str(p): sha(p) for p in inputs}
    compiler = subprocess.check_output(['g++', '--version'], text=True).splitlines()[0]
    identity = {'files': hashes, 'compiler': compiler, 'flags': ['-std=c++17', '-O3', '-fno-fast-math', '-pthread']}
    manifest = directory / 'build.json'
    binaries = [directory / 'router_trace', directory / 'router_original']
    if manifest.exists() and all(p.is_file() for p in binaries):
        previous = json.loads(manifest.read_text())
        if previous['identity'] == identity and previous['binaries'] == {p.name: sha(p) for p in binaries}:
            return binaries, previous
    commands = []
    for source, binary in zip([generated, baseline], binaries):
        command = ['g++', *identity['flags'], '-I', str(UPSTREAM / 'include'),
                   '-I', str(ROOT / 'adapters'), str(source), '-o', str(binary)]
        with (directory / (binary.name + '.build.log')).open('w') as log:
            subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True, timeout=180)
        commands.append(command)
    record = {'identity': identity, 'commands': commands, 'binaries': {p.name: sha(p) for p in binaries}}
    manifest.write_text(json.dumps(record, indent=2) + '\n')
    return binaries, record
