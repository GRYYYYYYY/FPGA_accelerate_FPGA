"""Unbounded-integer independent geometry oracle, plus explicit fault cases."""
from pathlib import Path
import random,sys
IMAX=2**31-1;IMIN=-2**31

def oracle(x):
 cx,cy,sx,sy,cs,ss,cross,length,n,p,lo,hi,det=x
 dx=abs(cx-sx);dy=abs(cy-sy);ds=abs(cs-ss)
 if cross and ds:
  if ds==1:
   if length<0:return [4,0,0,0]
   over=dy-length
   if over<0:dy=length-over
  if dy>IMAX:return [2,0,0,0]
  if n!=p:
   nv=n!=IMAX and n<hi;pv=p!=IMIN and p>lo
   if not nv and not pv:return [1,0,0,0]
   # Translate the original branch expression using mathematical infinity for
   # an unavailable column, so sentinel arithmetic cannot wrap.
   dn=abs(n-cx) if nv else float('inf');dp=abs(p-cx) if pv else float('inf')
   tn=dn+abs(sx-n);tp=dp+abs(sx-p)
   if dn==dp:dx=min(tn,tp)
   elif dn<dp and tn<=tp+det:dx=tn
   elif dp<dn and tp<=tn+det:dx=tp
   else:dx=tn if dn<dp else tp
 if dx>IMAX or dy>IMAX or dx+dy>IMAX:return [2,0,0,0]
 return [0,int(dx),dy,int(dx+dy)]

def make():
 rng=random.Random(0x9285ab);rows=[]
 for i in range(8192):
  cx=rng.randrange(100,1000);sx=rng.randrange(20,2000)
  n=cx+rng.randrange(1,90);p=cx-rng.randrange(1,90)
  if i%4==0:n=p=cx
  if i%4==1:n=cx+30;p=cx-30
  x=[cx,rng.randrange(-100,800),sx,rng.randrange(-100,800),i%3,(i//3)%3,(i//9)%2,60,n,p,-32768,32767,rng.randrange(-32,128)]
  rows.append((0,x))
 base=[100,10,200,20,0,1,1,60,120,80,0,300,1]
 # Explicit missing-column, BB equality, ties, dy just below/equal/above length.
 for n in [120,100,80,IMAX,300]:
  for p in [80,100,120,IMIN,0]:
   for dy in [0,1,59,60,61,120]:
    x=base[:];x[8]=n;x[9]=p;x[3]=10+dy;rows.append((1,x))
 extremes=[IMIN,IMIN+1,-32768,-1,0,1,32767,65535,IMAX-1,IMAX]
 for field in range(13):
  for v in extremes:
   x=base[:];x[field]=v;rows.append((2,x))
 for _ in range(1024):
  x=[rng.choice(extremes) for _ in range(13)];rows.append((2,x))
 return rows
if __name__=='__main__':
 rows=make();Path(sys.argv[1]).write_text(''.join(str(g)+' '+' '.join(f'{v&0xffffffff:08x}' for v in x+oracle(x))+'\n' for g,x in rows));print(len(rows))
