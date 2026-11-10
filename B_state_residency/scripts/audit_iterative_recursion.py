from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed'
 for group,base in [('sources',out/'sources'),('artifacts',out)]:
  for n,h in m[group].items():assert sha(base/n)==h,n
 assert len(m['commands'])==4 and all(x['exit_code']==0 for x in m['commands'])
 src=out/'sources';a=(src/'immediate.cpp').read_text();b=(src/'iterative.cpp').read_text()
 # Recover full original observed source; only recursion scheduling may differ.
 b=b.replace('    int iterative_child=-1;\n','',1).replace('            iterative_child=child;','            exploreAndExpand(st, child);',1)
 start=b.index('    void exploreAndExpand(State& st, int root) {');end=b.index('\n    // ----------------------------------------------------------------- rip up / save',start)
 f=b[start:end]
 header='''    void exploreAndExpand(State& st, int root) {
        struct Frame { int node, next; };
        std::vector<Frame> stack;
        auto enter=[&](int node){ record_expand(node); getChildren(node); stack.push_back({node,0}); };
        enter(root);
        while (!stack.empty()) {
        int rnode=stack.back().node;
'''
 assert f.startswith(header)
 f=f.replace(header,'    void exploreAndExpand(State& st, int rnode) {\n        record_expand(rnode);',1)
 f=f.replace('''        if (st.earlyTermination || stack.back().next >= nk) { stack.pop_back(); continue; }
        int ki=stack.back().next++;
        iterative_child=-1;
        {''','        for (int ki = 0; ki < nk; ki++) {',1)
 f=f.replace('''            if (st.earlyTermination) { stack.pop_back(); continue; }
            if (iterative_child >= 0) enter(iterative_child);''','            if (st.earlyTermination) break;',1)
 assert f.endswith('        }\n        }\n    }\n');f=f[:-len('        }\n    }\n')]+'    }\n'
 assert b[:start]+f+b[end:]==a,'entire original source recovery'
 base=ROOT/'results/recursion_order_20261025';assert sha(base/'source_bound_audit.json')==m['base_audit_sha256'];assert a==(base/'sources/immediate.cpp').read_text()
 x=(out/'immediate_execute.log').read_text();assert x==(out/'iterative_execute.log').read_text()
 cases=x.split('CASE ')[1:];assert len(cases)==40
 counts=[]
 for i,c in enumerate(cases):
  lines=c.splitlines();assert lines[0]==str(i);assert lines[-1]=='RECURSION_ORDER_CASE_FINISHED'
  labels=[l.split()for l in lines if l.startswith('L ')];assert len(labels)==64 and sorted(int(l[1])for l in labels)==list(range(64))
  counts.append({'case':i,'expansions':sum(l.startswith('E ')for l in lines),'pushes':sum(l.startswith('P ')for l in lines),'visited_skips':sum(l.startswith('S ')for l in lines),'polled':sum(l.startswith('Q ')for l in lines)})
 assert counts[1]['expansions']==64 and counts[1]['pushes']==63
 assert sum(c['visited_skips']for c in counts)>0
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'cases':counts,'final_label_records_compared':2560,'scope':m['scope'],'limitation':'Unbounded software vector stack; capacity overflow, hardware suspension and full engine integration not proven.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
