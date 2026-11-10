"""Symbolize completed resident diagnostic samples; source attribution, not latency."""
import argparse,json
from collections import Counter
from pathlib import Path
from analyze_real import symbolize
from report_resident_capacity import sha,require,ROOT

def analyze(directory):
    directory=Path(directory);d=json.loads((directory/'manifest.json').read_text());binary=ROOT/'build/resident_profile_v1/router';source=binary.with_name('router.cpp')
    require(sha(binary)==d['build']['binary_sha256'] and sha(source)==d['build']['source_sha256'],'Diagnostic build changed')
    # Explicit ranges are tied to this exact source hash and audited anchors below.
    lines=source.read_text().splitlines()
    require('void reset()' in lines[543] and 'bool readIsZero' in lines[552] and 'size_t acquire' in lines[559] and 'void release' in lines[600],'Source ranges changed')
    def classify(frames):
        apps=[f for f in frames if f['file']==str(source)]
        for f in apps:
            n=f['line']
            if 544<=n<=551:return 'query_reset'
            if 553<=n<=559:return 'zero_page_lookup'
            if 560<=n<=600:
                if 567<=n<=570:return 'victim_selection'
                if 573<=n<=577:return 'writeback_context'
                if 580<=n<=581:return 'backing_lookup'
                if 582<=n<=583:return 'zero_fill_context'
                if 585<=n<=587:return 'refill_context'
                if 594<=n<=599:return 'lru_pin_dirty'
                return 'page_acquire_other'
            if 601<=n<=604 or 625<=n<=640:return 'lease_release_or_wrapper'
            if 605<=n<=610:return 'label_prefetch'
        # Preserve residual search work; only innermost application expression is
        # eligible as a label-source site (not every caller of label routines).
        if apps:
            n=apps[0]['line']
            code=lines[n-1].split('//',1)[0] if 0<n<=len(lines) else ''
            if 'TLD(' in code or 'TLRead(' in code:return 'label_source_expression'
        names=' '.join(f['function'] for f in frames)
        if 'Router::TLRead(' in names or 'Router::TLD(' in names:return 'label_interface_wrapper'
        if any(x in names for x in ['::countUserHot(', '::countUserSlot(', '::searchCountUser(', '::countConnectionsOfUser(']):return 'same_net_owner_lookup'
        if any(x in names for x in ['::getChildren(', '::computeChildren(', '::deadChild(']):return 'adjacency'
        if any(x in names for x in ['::ripUp(', '::updateUsersAndPresentCongestionCost(', '::saveRouting(', '::setAllTargets(', '::updateCost(']):return 'route_state_updates'

        if 'tightenBoundingBoxesCoarse' in names:return 'bbox'
        if 'DaryPQ' in names:return 'priority_queue'
        if any('real_profile.hpp' in f['file'] for f in frames):return 'sampling_code'
        return 'other_or_unresolved'
    output={}
    for r in d['runs']:
        if not r.get('verified') or not r['sample_us']:continue
        path=directory/(r['name']+'.profile.pcs');rows=[[int(x,16)-(i>0) for i,x in enumerate(s.split())] for s in path.read_text().splitlines()]
        require(len(rows)==r['profile']['samples'] and not r['profile']['samples_dropped'],'Sample count mismatch')
        symbols=symbolize(binary,(pc for row in rows for pc in row));counts=Counter();sites=Counter()
        for row in rows:
            frames=[f for pc in row for f in symbols[pc]];counts[classify(frames)]+=1
            first=next((f for f in frames if f['file']==str(source)),frames[0]);sites[(first['function'],first['location'])]+=1
        output[r['name']]=dict(samples=len(rows),pcs_sha256=sha(path),counts=dict(counts),percent={k:100*v/len(rows) for k,v in counts.items()},top_sites=[dict(function=k[0],location=k[1],samples=v) for k,v in sites.most_common(60)])
        (directory/(r['name']+'.symbols.json')).write_text(json.dumps({hex(k):v for k,v in symbols.items()},indent=2)+'\n')
    return dict(scope='Completed sampled cases only; exclusive sampled source/stack context, not isolated memory latency. Periodic sampling and DWARF/unwind bias apply; zeros do not prove absence.',source_sha256=sha(source),binary_sha256=sha(binary),runs=output)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);args=p.parse_args();out=analyze(args.directory);(args.directory/'sample_analysis.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:dict(samples=v['samples'],percent=v['percent']) for k,v in out['runs'].items()},indent=2))
