from pathlib import Path
import hashlib,json,struct,sys
ROOT=Path(__file__).resolve().parents[1]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def f32(x):return struct.unpack('<f',struct.pack('<f',x))[0]
def bits(x):return struct.unpack('<I',struct.pack('<f',x))[0]
def pack(words):return sum(w<<(32*i)for i,w in enumerate(words))
def main():
 out=Path(sys.argv[1]).resolve();m=json.loads((out/'manifest.json').read_text());assert m['status']=='passed' and len(m['commands'])==3 and all(x['exit_code']==0 for x in m['commands'])
 for n,h in m['sources'].items():assert sha(out/'sources'/n)==h
 for n,h in m['artifacts'].items():assert sha(out/n)==h
 assert sha(out/'runner.py')==m['runner_sha256']
 base=ROOT/'results/candidate_cost23_pilot_20261025';bm=json.loads((base/'manifest.json').read_text());byname={Path(n).name:x['sha256']for n,x in bm['sources'].items()};same=0
 for n,h in m['sources'].items():
  if n.startswith('tb_'):continue
  assert h==byname[n];same+=1
 seen=[]
 for line in(out/'simulate.log').read_text().splitlines():
  if not line.startswith('BRANCH '):continue
  _,branch,g,c=line.split();geometry=int(g.split('=')[1],16);cost=int(c.split('=')[1],16)
  dx,dy,dist=(20,100,120)if branch=='cross_different_slr'else(20,20,40);assert geometry==pack([0,dx,dy,dist])
  sf=f32(1+f32(1*3));nc=f32(f32(f32(1*1)*1)/sf);bias=f32(f32(f32(1/2)*2)/10);nc=f32(nc+min(bias,f32(nc/2)));pc=f32(f32(1+nc)+f32(f32(f32(0.5)*2)/sf));h=f32(f32(0.8)*dist);total=f32(pc+f32(h/sf))
  assert cost==pack(list(map(bits,[sf,nc,pc,h,total])));seen.append(branch)
 assert seen==['cross_different_slr','cross_same_slr'];log=(out/'simulate.log').read_text();assert 'COST23_BRANCHES_PASS cases=5'in log and 'Fatal:'not in log and '$finish called'in log
 r={'status':'passed','manifest_sha256':sha(out/'manifest.json'),'auditor_sha256':sha(Path(__file__)),'actual_geometry_and_cost_sources_matched':same,'cases':5,'numeric_cost_words_independently_checked':10,'scope':'Mock coordinate replies, actual geometry/cost kernels and collectors; crossSLR different/same, noncross, unsupported-landmark stop, upper16bit version drift during cost. Not real-graph crossSLR or joined recovery.'}
 (out/'source_bound_audit.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
if __name__=='__main__':main()
