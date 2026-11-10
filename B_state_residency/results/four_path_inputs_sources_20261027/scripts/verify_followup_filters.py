"""Independently replay eager getChildren/access decisions and emit label read closure."""
from pathlib import Path
import contextlib,hashlib,json,mmap,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb')as f:
  for b in iter(lambda:f.read(1<<20),b''):h.update(b)
 return h.hexdigest()
def main():
 inp=Path(sys.argv[1]).resolve();out=Path(sys.argv[2]).resolve();out.mkdir();gate=json.loads((inp/'source_bound_audit.json').read_text());assert gate['status']=='passed'
 base=Path(json.loads((inp/'manifest.json').read_text())['base']);ba=json.loads((base/'source_bound_audit.json').read_text());st=ba['state'];graph=ROOT/'results/graph_image_20261024';assert st['cross']==[0,0] and st['landmark']==[0] and st['flags'][2]==0
 local={6,7,8,9,13,14,15,16};west={7,9,15};east={6,8,14};exclusive={1,2,3,4}
 closure=set();updated={};created={};cache={};reasons={};rawsum=0;cachehits=0;pushes=0;lookaheads=0;earlycount=0;parent=None;expectedkids=[];kidx=0;previous=None;pending=None
 overflow={}
 for node,net,refs in struct.iter_unpack('<III',(base/'initial_overflow.u32').read_bytes()):overflow[node,net]=refs
 data=(base/'initial_caches.u32').read_bytes();cursor=0
 while cursor<len(data):
  node,count=struct.unpack_from('<II',data,cursor);cursor+=8;cache[node]=list(struct.unpack_from('<'+'I'*count,data,cursor));cursor+=count*4
 with contextlib.ExitStack()as stack:
  def mm(path):
   f=stack.enter_context(path.open('rb'));return stack.enter_context(mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ))
  initial=mm(base/'initial_nodes.u32');final=mm(base/'search_final_nodes.u32');attrs=mm(graph/'nodes.rrt32');offsets=mm(graph/'offsets.u32le');edges=mm(graph/'edges.u32le')
  def sn(i):assert 0<=i<ba['nodes'];return struct.unpack_from('<11I',initial,i*44)
  def a(i):return struct.unpack_from('<iiBBhhhhhIii',attrs,i*32)
  def label(i):closure.add(i);return updated.get(i,sn(i)[:6])
  def iscreated(i):return created.get(i,sn(i)[9])
  def prev(i):return label(i)[3]
  def ey(i):
   d=a(i)
   if d[2]==5:
    p=prev(i)
    if p!=0xffffffff and a(p)[7]==d[7]:return d[5]
   return d[7]
  def count(i):
   s=sn(i);return s[7] if s[6]==st['net'][0] else overflow.get((i,st['net'][0]),0)
  def overuse(i):
   occ=min(255,sn(i)[8]);return occ>1 or(occ==1 and count(i)==0)
  def excluded(par,child):
   d=a(child)
   if iscreated(child):
    p=prev(child)
    if p!=0xffffffff and label(child)[4]!=label(par)[4] and p==par and d[3]&64:return False
   if d[3]&64:return True
   if d[3]&4 and not iscreated(child):return True # no Laguna
   if d[3]&2:return True
   if iscreated(child) and d[3]&32 and prev(child)!=par:return True
   return False
  def graphaccess(par,child):
   d=a(child);pd=a(par);t=d[2]
   if t not in local:
    if t==12:
     if pd[2] in local:
      if d[3]&2:return False
     elif pd[2]==5:
      p=prev(par)
      if p!=0xffffffff and a(p)[0]==d[0]:return False
    return True
   sink=a(st['sink'][0]);same=d[0]==sink[0];sk=sink[2]
   if sk==2 and(t in west or t==16):return False
   if sk==3 and(t in east or t==16):return False
   if sk==1 and(not same or t!=13):return False
   if sk==4:return False
   return same or(d[6]==sink[4] and abs(ey(child)-sink[5])<=1)
  def decision(par,child):
   d=a(child);v=label(child);t=d[2]
   if v[4]==st['sequence'][0]:return False,False,False,'visited'
   if v[5]:return True,False,t in exclusive or not overuse(child),'target'
   if st['flags'][3] and not(d[6]>st['bbox'][0] and d[6]<st['bbox'][1] and ey(child)>st['bbox'][2] and ey(child)<st['bbox'][3]):return False,False,False,'bbox'
   la=False
   if t in local:
    if t in {6,7,8,9}:la=not overuse(child)
    if not graphaccess(par,child):return False,False,False,'graph_access'
   elif t in {10,11,12}:
    if not graphaccess(par,child):return False,False,False,'graph_access'
    la=bool(a(par)[3]&2 or d[3]&2)
   elif t in exclusive:
    if count(child)==0 or not(d[3]&128):return False,False,False,'exclusive_sink'
   return True,la,False,'push'
  for line in(base/'events.txt').read_text().splitlines():
   tag,*vals=line.split();v=list(map(int,vals))
   if tag in {'C','E','P','END'}:assert pending is None,('missing CPU push',pending)
   if tag=='P':label(v[0])
   elif tag=='E':
    parent,degree,q=v;label(parent)
    lo,hi=struct.unpack_from('<2I',offsets,parent*4);raw=[struct.unpack_from('<I',edges,j*4)[0]for j in range(lo,hi)];rawsum+=len(raw)
    # Includes every raw candidate even when the CPU excludes before label access;
    # this deliberate superset allows safe pre-import before hardware filtering.
    closure.update(raw)
    if parent in cache:expectedkids=cache[parent];cachehits+=1
    else:
     expectedkids=[]
     for child in raw:
      if excluded(parent,child):continue
      created[child]=1
      if a(child)[2]==17:continue
      expectedkids.append(child)
     cache[parent]=expectedkids
    assert len(expectedkids)==degree,(parent,'degree',expectedkids,degree);kidx=0
   elif tag=='K':assert v==[parent,expectedkids[kidx]];kidx+=1
   elif tag=='C':
    assert kidx==len(expectedkids);par,child,pos=v[:3];assert par==parent and expectedkids[pos]==child
    push,la,early,why=decision(par,child);reasons[why]=reasons.get(why,0)+1;previous=(par,child,early)
    if push:pending=(par,child,la,early)
   elif tag=='W':
    assert pending is not None;par,child,la,early=pending;assert v[0]==child and v[1]==par and v[6]==int(la)
    old=label(child);updated[child]=(v[2],v[3],old[2],par,v[4],v[5]);pushes+=1;lookaheads+=la;earlycount+=early;pending=None
   elif tag=='END':assert v[:3]==[ba['event_counts']['P'],1,0]
  assert pushes==ba['event_counts']['W'] and lookaheads==0 and earlycount==1 and reasons.get('target')==1
  # Host import is a full literal record for each read-footprint node, including
  # -1 prev and untouched nonvisited fields. No zero-default substitution.
  closure.update([st['source'][0],st['sink'][0]])
  with(out/'initial_label_imports.u32').open('wb')as fi,(out/'expected_label_reads.u32').open('wb')as ff:
   for i in sorted(closure):
    u=sn(i);fin=struct.unpack_from('<11I',final,i*44)
    fi.write(struct.pack('<6I',i,u[0],u[1],u[3],u[4],u[5]));ff.write(struct.pack('<6I',i,fin[0],fin[1],fin[3],fin[4],fin[5]))
  changedcreated=0
  # Compare the constructed node set against every observed full-snapshot
  # transition, not only filtered child IDs.
  for start in range(0,ba['nodes']*44,44*16384):
   aa=initial[start:start+44*16384];bb=final[start:start+44*16384]
   if aa==bb:continue
   for off in range(0,len(aa),44):
    if aa[off:off+44]==bb[off:off+44]:continue
    i=(start+off)//44;u=struct.unpack_from('<11I',aa,off);f=struct.unpack_from('<11I',bb,off)
    assert f[9]==iscreated(i) and f[10]==u[10];changedcreated+=u[9]!=f[9]
  assert changedcreated==ba['created_transitions']
  pages=len({i//8 for i in closure})
 m=dict(status='passed',input_root=str(inp),input_audit_sha256=sha(inp/'source_bound_audit.json'),capture_audit_sha256=sha(base/'source_bound_audit.json'),graph_audit_sha256=sha(graph/'source_bound_audit.json'),runner_sha256=sha(Path(__file__)),raw_children=rawsum,filtered_children=sum(reasons.values()),expansions=len([l for l in(base/'events.txt').read_text().splitlines()if l.startswith('E ')]),cache_hits=cachehits,decisions=reasons,pushes=pushes,lookahead=lookaheads,early=earlycount,created_transitions=changedcreated,label_import_records=len(closure),logical_pages=pages,artifacts={p.name:sha(p)for p in out.iterdir()if p.is_file()},scope='Independent natural eager getChildren/exclusion/access/visited/target decisions, complete created transitions, and conservative literal label read closure. No RTL execution or board measurement.')
 (out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n');audit=dict(m,manifest_sha256=sha(out/'manifest.json'));(out/'source_bound_audit.json').write_text(json.dumps(audit,indent=2)+'\n');print(json.dumps(m,indent=2))
if __name__=='__main__':main()
