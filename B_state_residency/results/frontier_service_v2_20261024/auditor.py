"""Independent command/response replay, frozen source gates and reset negative control."""
from pathlib import Path
import hashlib,heapq,json,re,struct
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def verify_sources(out):
 m=read(out/'manifest.json');assert m['status']=='passed'
 for name,spec in m['sources'].items():
  assert sha(out/'sources'/name)==spec['sha256']==sha(Path(spec['path'])),name
 for name,digest in m['artifacts'].items():assert sha(out/name)==digest,name
 gate=m['hls_gate'];assert sha(Path(gate['path']))==gate['sha256']
 assert read(Path(gate['path']))['status']=='passed'
 assert sha(out/'runner.py')==m['runner_sha256']
 assert all(c['exit_code']==0 for c in m['commands'])
 return m

def main():
 out=ROOT/'results/frontier_service_v2_20261024';m=verify_sources(out)
 neg=ROOT/'results/frontier_reset_20261024';nm=verify_sources(neg)
 assert nm['raw_reset_safe'] is False and nm['clear_hides_old_heap'] is True
 assert 'RAW_RESET_RETAINS_OLD_HEAP size_after_reset=2 stale_id=deadbeef' in (neg/'simulate.log').read_text()
 clog=(out/'frontier_hls_call.log').read_text();slog=(out/'frontier_service.log').read_text()
 assert 'FRONTIER_CALL_PASS permutations=120 coherent_calls=121 fault_cases=12' in clog
 assert not re.search(r'Fatal:|ERROR:',clog+slog) and '$finish called' in clog and '$finish called' in slog
 pending=None;heap=[];owner=None;booted=False;stopped=False
 qs=rs=resets=boots=abandoned=full=empty=wrong=busy=bad=inactive=polled=0
 max_size=0;last_cookie=0;nan_payloads=0
 for line in (out/'transactions.txt').read_text().splitlines():
  v=line.split();kind=v[0]
  if kind=='RESET':
   resets+=1;abandoned+=pending is not None;pending=None;heap=[];owner=None;booted=False;stopped=False
  elif kind=='BOOT':
   assert not booted and int(v[1])>=boots+1;boots+=1;booted=True
  elif kind=='ABORT':stopped=True
  elif kind=='Q':
   assert booted and not stopped and pending is None
   op,bits,node,cookie=(int(x,16) for x in v[1:5]);query,price=map(int,v[5:7]);qs+=1
   assert cookie==last_cookie+1;last_cookie=cookie
   pending=(op,bits,node,cookie,query,price)
  elif kind=='R':
   assert pending is not None
   status,bits,node,size,cookie=(int(x,16) for x in v[1:6]);query,price=map(int,v[6:8]);rs+=1
   op,ibits,inode,icookie,iq,ip=pending;pending=None
   assert (cookie,query,price)==(icookie,iq,ip)
   expected=0;ebits=enode=0
   if op>4:expected=3;bad+=1
   elif op==0 and owner is not None:expected=6;busy+=1
   elif op!=0 and owner is None:expected=4;inactive+=1
   elif op!=0 and owner!=(query,price):expected=5;wrong+=1
   elif op==0:heap=[];owner=(query,price)
   elif op==4:heap=[];owner=None
   elif op==1:
    if len(heap)==65536:expected=2;full+=1
    else:
     # Capacity sequence has strictly unique positive keys. Specials only occur
     # as a single element, so this oracle introduces no equal-key tie rule.
     value=struct.unpack('<f',struct.pack('<I',ibits))[0]
     if value!=value:assert not heap;nan_payloads+=1
     heapq.heappush(heap,(value,ibits,inode))
   elif op==2:
    if not heap:expected=1;empty+=1
    else:_,ebits,enode=heapq.heappop(heap);polled+=1
   assert (status,bits,node,size)==(expected,ebits,enode,len(heap)),(rs,v,pending,expected,len(heap))
   max_size=max(max_size,size)
  elif kind=='END':
   assert tuple(map(int,v[1:4]))==(qs,rs,boots)
   assert qs-rs==abandoned and pending is None
  else:raise AssertionError(kind)
 assert max_size==65536 and full==1 and nan_payloads==2 and wrong==2 and busy==1 and bad==1 and inactive==1
 assert abandoned==193 and boots==390 and resets==391,(abandoned,boots,resets)
 match=re.search(r'FRONTIER_SERVICE_PASS calls=(\d+) resets=(\d+) accepted=(\d+) responded=(\d+) hls_calls=(\d+) cycles=(\d+) capacity=65536 interrupted_offsets=192',slog)
 assert match and int(match[2])==boots and int(match[3])==qs and int(match[4])==rs and int(match[1])==rs-1
 # Successful variant changes only TB stable-edge sampling from the initial failure.
 for name in ['frontier_hls_call.sv','frontier_service.sv','tb_frontier_hls_call.sv']:
  assert sha(out/'sources'/name)==sha(ROOT/'results/frontier_service_v1_20261024/sources'/name)
 result={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),
  'raw_reset_negative_manifest_sha256':sha(neg/'manifest.json'),
  'counts':dict(requests=qs,responses=rs,reset_assertions=resets,completed_boots=boots,abandoned_on_reset=abandoned,max_heap=max_size,full=full,empty=empty,polls=polled,wrong_owner=wrong,open_busy=busy,bad_op=bad,inactive=inactive,nan_single_payloads=nan_payloads,hls_calls=int(match[5]),cycles=int(match[6])),
  'collector':{'all_event_orders':120,'coherent_calls':121,'fault_cases':12},
  'scope':'Actual generated 64K Frontier RTL plus lifecycle wrapper; coordinated reset, OPEN/CLOSE, full unique-key drain and single raw special payloads. No complete search, shared external query controller, place/route or board result.'}
 (out/'auditor.py').write_bytes(Path(__file__).read_bytes());(out/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
