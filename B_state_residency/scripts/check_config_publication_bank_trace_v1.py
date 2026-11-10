"""Validate dense binary four-state snapshots and compare every recorded bit."""
import hashlib
import re

STATE_BITS=4810
OUTPUT_BITS=7238


def observation(text):
    assert text.endswith('\n') and '\r' not in text
    lines=text.splitlines();assert 1<len(lines)<3001
    pattern=re.compile(r'BANK ([1-9][0-9]*) ([0-9]+) ([01xXzZ]{4810}) ([01xXzZ]{7238})')
    times=[];unknown=0;high_impedance=0
    for index,line in enumerate(lines,1):
        match=pattern.fullmatch(line);assert match,('malformed binary snapshot',index)
        assert int(match[1])==index,('missing or repeated edge',index,match[1])
        times.append(int(match[2]))
        bits=match[3]+match[4];unknown+=bits.lower().count('x');high_impedance+=bits.lower().count('z')
    step=times[1]-times[0];assert step>0
    assert all(time==times[0]+i*step for i,time in enumerate(times)), 'nonuniform clock records'
    return dict(edges=len(lines),state_bits=STATE_BITS,output_bits=OUTPUT_BITS,
        first_timestamp=times[0],last_timestamp=times[-1],timestamp_step=step,
        x_bit_observations=unknown,z_bit_observations=high_impedance,
        sha256=hashlib.sha256(text.encode()).hexdigest())


def compare(reference,candidate):
    a,b=observation(reference),observation(candidate)
    if reference!=candidate:
        for index,(left,right) in enumerate(zip(reference.splitlines(),candidate.splitlines()),1):
            if left!=right:
                raise AssertionError(('recorded state/output/time differs',index))
        raise AssertionError('recorded edge count differs')
    assert a==b
    return a
