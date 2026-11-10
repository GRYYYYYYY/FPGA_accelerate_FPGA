"""Independent bounded-control log checks. Not a real DUT/full shadow auditor."""
import re

def parse(log,name,error=None):
 fatal=re.findall(r'^Fatal:.*$',log,re.M)
 assert not re.search(r'^\s*(ERROR:|Error:)',log,re.M)
 marker='FULL_SHADOW_FIXTURE_READY_CANDIDATE_PASS'
 assert 'FULL_SHADOW_PROTOCOL_PASS' not in log
 if error is not None:
  assert name not in ['matching','ready_nba'] and len(fatal)==1 and error in fatal[0]
  assert marker not in log
  if 'COVERAGE_MISSING' in error:
   m=re.search(r'active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+)',fatal[0]);assert m
   a,s,t,e,i=map(int,m.groups());assert i>0
   if name.endswith('no_stream'):assert a==s==t==e==0
   elif name.endswith('no_transfers'):assert a>0 and s>0 and t==0 and e>0
   elif name.endswith('no_stalls'):assert a>0 and s==0 and t==e==5
   else:raise AssertionError(name)
  return {'verdict':'expected_rejection','fatal':fatal[0]}
 assert name in ['matching','ready_nba'] and not fatal
 assert log.count('$finish called at time : 1202 ns')==1
 pattern=r'^'+marker+r' outputs=346 unconditional=342 qualified=cp_m_data,k_a_node,k_a_net,p_m_wdata checks=(\d+) reset_edges=(\d+) original_end=(\d+) last_checked=(\d+) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$'
 matches=re.findall(pattern,log,re.M);assert len(matches)==1
 values=list(map(int,matches[0]));assert values[:4]==[190,5,1000000,1201000]
 groups={'CP':values[4:]};rows=re.findall(r'^PAYLOAD_GROUP_PASS group=(KA|PW) active=(\d+) stalled=(\d+) transfers=(\d+) edges=(\d+) idle=(\d+) idle_differences=(\d+)$',log,re.M)
 assert len(rows)==2 and {x[0] for x in rows}=={'KA','PW'}
 groups.update({row[0]:list(map(int,row[1:])) for row in rows})
 # 190 post-update samples plus94 qualified pre-edges=284 group observations.
 # KA valid145..195ns gives10post+5pre; five always-ready requests, no stalls.
 cp=[33,18,5,11,251,251] if name=='ready_nba' else [30,16,5,10,254,254]
 assert groups=={'CP':cp,'KA':[15,0,5,5,269,269],'PW':cp},groups
 return {'verdict':'match','groups':groups}
