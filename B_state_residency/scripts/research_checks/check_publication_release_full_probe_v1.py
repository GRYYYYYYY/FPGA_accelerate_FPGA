"""Strict text oracle for the actual full-RTL early publication/release probe."""
import re
PATTERNS={
 'ready':r'FULL_PROBE_READY cycle=(\d+) time=(\d+) generation=([0-9a-fA-F]{16}) checkpoint=(\d+) version=(\d+)',
 'accept':r'FULL_SIMULTANEOUS_ACCEPT cycle=(\d+) time=(\d+) start=([01xz]) release=([01xz])',
 'split':r'FULL_OWNERSHIP_SPLIT cycle=(\d+) time=(\d+) publication=([01xz]) lease=([01xz])',
 'halt':r'FULL_RTL_RELEASE_OVERLAP_OBSERVED cycle=(\d+) time=(\d+) status=(\d+)'
}
def parse_probe_text(text):
 assert not re.search(r'Fatal:|ERROR:|\$fatal|watchdog',text,re.I),'runtime error/timeout'
 found={};positions=[]
 for key,pattern in PATTERNS.items():
  matches=list(re.finditer(r'^'+pattern+r'\s*$',text,re.M));assert len(matches)==1,(key,'missing/duplicate/malformed')
  tag=pattern.split(' ',1)[0];assert len(re.findall(r'^'+re.escape(tag)+r'\b',text,re.M))==1,(key,'extra malformed marker')
  match=matches[0];positions.append(match.start());found[key]=match.groups()
 assert positions==sorted(positions),'event order'
 assert found['accept'][2:]==('1','1'),'not simultaneous accepted'
 assert found['split'][2:]==('1','0'),'ownership split absent'
 assert int(found['halt'][2])==3,'not HALT status'
 ready,accept,split,halt=[int(found[k][1]) for k in ['ready','accept','split','halt']]
 assert ready<accept and split==accept+1000 and halt==accept+11000,'10ns clock / NBA sampling times'
 assert (accept-ready)%10000==5000,'drive not on preceding falling edge'
 assert int(found['ready'][0])>=73,'original cold initialization prefix not reached'
 assert int(found['ready'][2],16)==0x100000001 and int(found['ready'][3])==17 and int(found['ready'][4])==3,'cold descriptor context'
 cycles=[int(found[k][0]) for k in ['ready','accept','split','halt']]
 assert all(0<=b-a<=2 for a,b in zip(cycles,cycles[1:])),'cycle continuity'
 assert re.search(r'\$finish called at time\s*:',text),'normal testbench termination missing'
 return {'ready_ps':ready,'accept_ps':accept,'split_ps':split,'halt_ps':halt,'cycles':cycles,'scope':'Observed interface invariant failure; not full regression PASS.'}
