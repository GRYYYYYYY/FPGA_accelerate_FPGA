"""Strict ordered transfer-log parser; gold records originate outside gate logger."""
import re


def rows(text,pattern):
    lines=text.splitlines();out=[]
    for line in lines:
        m=re.fullmatch(pattern,line);assert m,line
        out.append(m.groups())
    return out


def times(values):
    assert values and all(a<b for a,b in zip(values,values[1:]))
    assert all(t%10000==5000 for t in values)


def check_ka(text,gold,expected_design=None):
    data=rows(text,r'KA_WORD (\d+) (\d+) (\d+) (\d+) (\d+) ([0-9a-fA-F]{16})')
    assert len(data)==len(gold)>0
    ts=[int(r[0]) for r in data];times(ts)
    actual=[tuple(map(int,r[1:5])) for r in data]
    assert actual==[tuple(r) for r in gold]
    if expected_design is not None:assert all(int(r[5],16)==expected_design for r in data)
    return dict(requests=len(data),first_time_ps=ts[0],last_time_ps=ts[-1])


def check_pw(text,gold):
    addresses=[];beats=[]
    for line in text.splitlines():
        if line.startswith('PW_AW '):
            m=re.fullmatch(r'PW_AW (\d+) ([0-9a-fA-F]{8}) (\d+) (\d+) (\d+) ([0-9a-fA-F]+)',line);assert m,line
            t,addr,length,size,burst,ident=m.groups();t=int(t);addr=int(addr,16);length=int(length)+1
            assert 1<=length<=256 and int(size)==6 and int(burst)==1 and int(ident,16)==0
            assert addr%64==0 and (addr%4096)+length*64<=4096
            addresses.append((t,addr,length))
        else:
            m=re.fullmatch(r'PW_W (\d+) ([0-9a-fA-F]{128}) ([0-9a-fA-F]{16}) ([01])',line);assert m,line
            t,data,strb,last=m.groups();beats.append((int(t),int(data,16),int(strb,16),int(last)))
    assert addresses and beats and len(beats)==len(gold)
    times([r[0] for r in addresses]);times([r[0] for r in beats])
    expanded=[(addr+64*i,int(i==length-1)) for _,addr,length in addresses for i in range(length)]
    assert len(expanded)==len(beats)
    actual=[]
    for (addr,last),(_,data,strb,observed_last) in zip(expanded,beats):
        assert observed_last==last
        actual.append((addr,strb,data))
    assert actual==[tuple(r) for r in gold]
    return dict(addresses=len(addresses),write_beats=len(beats),first_time_ps=beats[0][0],last_time_ps=beats[-1][0])
