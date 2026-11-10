"""Audit full finite-control replay and compare data events to its predecessor."""
import argparse,json
from pathlib import Path
from report_finite_replay import audit as page_audit
from replay_finite_page_values import sha,ROOT

def audit(directory):
    directory=Path(directory);result=page_audit(directory)
    reference=ROOT/'results/finite_page_fast_real_addresses_20261023T014500Z/manifest.json'
    old=json.loads(reference.read_text())
    if old['status']!='passed':raise ValueError('Reference not complete')
    for name,row in result['groups'].items():
        for key,value in old['groups'][name].items():
            if row[key]!=value:raise ValueError('Control changed data-path events: '+name+'/'+key)
        if (row['control_requests']!=2*row['fences'] or row['control_ack_packets']!=3*row['fences']
                or row['control_duplicate_acks']!=2*row['fences'] or row['control_tag_wraps']!=row['fences']//4):
            raise ValueError('Control path accounting mismatch')
    result.update(reference_manifest_sha256=sha(reference),scope='Full selected addresses/synthetic values, bounded explicit control queues with duplicates and 2-bit tag wrap; no real transport or hardware proof.')
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('directory',type=Path);a=p.parse_args();result=audit(a.directory);(a.directory/'completion_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
