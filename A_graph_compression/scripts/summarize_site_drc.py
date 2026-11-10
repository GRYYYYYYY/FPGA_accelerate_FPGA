#!/usr/bin/env python3
"""Preserve and structure Vivado PDIL site failures without inferring legality."""
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re


def parse(text):
    records=[]
    for block in re.split(r'(?m)^(?=PDIL-1#\d+ Error\s*$)',text)[1:]:
        block=block.split('Related violations:',1)[0].strip()
        site=re.search(r'Invalid configuration for site (\S+)\.',block)
        if not site:raise ValueError('Unrecognized PDIL block')
        owners=[{'existing_net':a,'requested_net':b,'bel_pin':c}
                for a,b,c in re.findall(r'Cannot replace net (.+?) with net (.+?) on bel pin (\S+)',block)]
        equations=[{'bel':b,'site':s,'existing_value':old,'required_value':new,'user_logic':bool(user)}
            for user,b,s,old,new in re.findall(
                r"for (user logic )?element '([^ ]+) in site '([^']+)'. Attribute 'EQN' is programmed to '(.*?)' but needs a value of '(.*?)' for the route-thru",block)]
        records.append({'site':site[1],'ownership_conflicts':owners,'equation_conflicts':equations,'raw':block})
    return records


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('report',type=Path);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();records=parse(a.report.read_text());counts=Counter()
    for r in records:
        for c in r['ownership_conflicts']:
            counts['constant_net' if c['existing_net'].startswith('GLOBAL_LOGIC') else 'other_net']+=1
        for c in r['equation_conflicts']:
            counts['user_logic_equation' if c['user_logic'] else 'other_equation']+=1
    result={'status':'physical_validation_failed','sites':len(records),'counts':dict(counts),'records':records,
            'report_sha256':hashlib.sha256(a.report.read_bytes()).hexdigest(),
            'limitations':['Counts are reported conflicts, not a complete resource ownership model or mutually exclusive root causes.']}
    with a.output.open('x') as f:json.dump(result,f,indent=2);f.write('\n')
    print(json.dumps({'sites':len(records),'counts':dict(counts)}))


if __name__=='__main__':main()
