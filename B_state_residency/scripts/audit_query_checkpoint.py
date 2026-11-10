"""Independent event/stream/CRC oracle for the native sequence ledger."""
from pathlib import Path
import json,sys,struct,zlib,importlib.util
from run_checkpoint_authority import ROOT,sha

def crc(words):return zlib.crc32(struct.pack('<10I',*words))
def main():
 p=Path(sys.argv[1]).resolve();m=json.loads((p/'manifest.json').read_text());assert m['status']=='passed'
 for n,h in m['sources'].items():assert sha(p/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(p/n)==h
 assert len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 ns={'__file__':str(ROOT/'hardware/variants/query_checkpoint_v1/build.py'),'__name__':'frozen'};exec(compile((p/'sources/build.py').read_text(),'build.py','exec'),ns);assert ns['make']()==(p/'sources/query_lifecycle.sv').read_text()
 rows=[t.split()for t in(p/'events.txt').read_text().splitlines()];seen=False;seq=0;dirty=False;pending=None;queries=[];checkpoints=[];resets=0;edits=0;images=[]
 for t in rows:
  tag=t[0]
  if tag=='RESET':assert pending is None;seen=False;seq=0;dirty=False;resets+=1
  elif tag=='EDIT':dirty=dirty or seen;edits+=1
  elif tag=='C':
   assert pending is None;idx,imp=int(t[1]),int(t[2]);d,g=int(t[3],16),int(t[4],16);v,q,price=map(int,t[5:8]);wanted=int(t[8],16)
   pending={'id':idx,'importing':imp,'design':d,'generation':g,'version':v,'query':q,'price':price,'wanted':wanted,'input':[],'output':[],'env':False,'old':(seen,seq,dirty)}
  elif tag in ['S','M']:
   assert pending is not None and int(t[1])==pending['id'];pending['input'if tag=='S'else'output'].append((int(t[2]),int(t[3],16),int(t[4])))
  elif tag=='ENV':assert pending is not None and int(t[1])==pending['id'];pending['env']=True
  elif tag=='CP':
   z=pending;assert z is not None and int(t[1])==z['id'];status=int(t[2]);actualcrc=int(t[3],16);given=tuple(map(int,t[4:7]));d,g,v,q,price=[z[k]for k in ['design','generation','version','query','price']];expected=0
   if not d or not g or not v:expected=1
   elif z['env']:expected=2
   if z['importing']:
    stream=z['input'];transport=len(stream)==10 and all(i==k and last==int(k==9)for k,(i,w,last)in enumerate(stream));words=[w for i,w,last in stream]
    if expected==0:
     if not transport:expected=1
     else:
      flags=words[7];ss=bool(flags&64);dd=bool(flags&128);n=words[8]
      bad=words[0]!=0x51435031 or words[1]!=1 or words[2]+(words[3]<<32)!=d or words[4]+(words[5]<<32)!=g or words[6]!=v or flags>>8 or flags&3!=q or (flags>>2)&15!=price or words[9]!=0 or (n==0 if ss else n!=0)or crc(words)!=z['wanted']or(seen and(not ss or n<seq))or(dirty and not dd)
      if bad:expected=1
    if transport:assert actualcrc==crc(words)
    if expected==0:seen=ss;seq=n;dirty=dd
   else:
    expectedwords=[0x51435031,1,d&0xffffffff,d>>32,g&0xffffffff,g>>32,v,q+(price<<2)+(int(seen)<<6)+(int(dirty)<<7),seq if seen else 0,0]
    if expected!=1:assert z['output']==[(i,w,int(i==9))for i,w in enumerate(expectedwords)]and actualcrc==crc(expectedwords)
   assert status==expected,(z['id'],status,expected)
   assert given==(int(seen),seq,int(dirty)),(z['id'],given,(seen,seq,dirty));checkpoints.append({'id':z['id'],'importing':bool(z['importing']),'status':status,'crc':actualcrc,'sequence_seen':seen,'last_sequence':seq,'dirty':dirty,'input_words':len(z['input']),'output_words':len(z['output'])});pending=None
  elif tag=='Q':
   assert pending is None;i,n,status,floor,service,search,route=map(int,t[1:]);expected=int(dirty or n==0 or(seen and n<=seq));assert status==expected
   if status==0:seen=True;seq=n;assert (service,search,route)==(7,1,1)
   else:assert (service,search,route)==(0,0,0)
   assert floor==seq;queries.append([i,n,status,floor,service,search,route])
  elif tag=='IMAGE':images.append((int(t[1]),int(t[2],16)))
  else:raise AssertionError(tag)
 assert pending is None and len(queries)==14 and len(checkpoints)==27 and resets==7 and edits==1
 assert [q[2]for q in queries]==[0,0,1,0,1,1,0,1,1,1,1,1,0,1]
 assert [c['status']for c in checkpoints]==[0,0,1]+[1]*12+[2,1,1,2,2,1,0,0,0,1,0,0]
 assert images==list(enumerate([0x51435031,1,0x9abcdef0,0x12345678,1,1,3,77,2,0]))
 result={'status':'passed','manifest_sha256':sha(p/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'baseline_sha256':sha(ns['BASE']),'queries':queries,'checkpoints':checkpoints,'cold_resets':resets,'host_edits':edits,'image':images,'scope':m['scope'],'limits':['Trusted caller must pair generation with all restored state.','Version/query/price are context equality, not durable global recovery-attempt floors.','No full-query AXI integration or cold-reset replay protection of an older trusted snapshot.']}
 (p/'source_bound_audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'passed','queries':len(queries),'checkpoints':len(checkpoints)}))
if __name__=='__main__':main()
