"""Read-only source bundles; mutate private hardlink clones by atomic replacement."""
from pathlib import Path
import json,struct,hashlib,os,shutil,sys,tempfile,zlib
from run_checkpoint_authority import sha
from verify_rtl_bundle import verify

def write(p,data):
 tmp=p.with_name(p.name+'.replacement');tmp.write_bytes(data);os.replace(tmp,p)
def js(p,x):write(p,(json.dumps(x,sort_keys=True,indent=2)+'\n').encode())
def reseal(p,m,n=None):
 if n is not None:m['components'][n]={'bytes':(p/n).stat().st_size,'sha256':sha(p/n)}
 js(p/'manifest.json',m);js(p/'COMMIT.json',{'manifest_sha256':sha(p/'manifest.json'),'generation':m['generation'],'checkpoint':m['checkpoint']})
def main():
 root=Path(sys.argv[1]).resolve();results={}
 for name in ['full_5','pressure_5']:
  src=root/name/'bundle';original=verify(src);hashes={p.name:sha(p)for p in src.iterdir()if p.is_file()};checks=[]
  for case in ['valid','staging','no_commit','manifest','payload','path_semantics','query_semantics','directory_semantics','config_override','attempt_floor','commit_identity','immutable_reference']:
   with tempfile.TemporaryDirectory(prefix='b_bundle_integrity_')as tmp:
    p=Path(tmp)/('bundle.staging'if case=='staging'else'bundle');shutil.copytree(src,p,copy_function=os.link);m=json.loads((p/'manifest.json').read_text())
    if case=='no_commit':(p/'COMMIT.json').unlink()
    elif case=='manifest':m['generation']+=1;js(p/'manifest.json',m)
    elif case=='payload':d=bytearray((p/'query.bin').read_bytes());d[32]^=1;write(p/'query.bin',d)
    elif case=='path_semantics':
     v=list(struct.unpack('<78I',(p/'paths.bin').read_bytes()));v[7]=v[3];write(p/'paths.bin',struct.pack('<78I',*v));m['path_crc32']=zlib.crc32((p/'paths.bin').read_bytes());reseal(p,m,'paths.bin')
    elif case=='query_semantics':
     v=list(struct.unpack('<10I',(p/'query.bin').read_bytes()));v[7]&=~64;write(p/'query.bin',struct.pack('<10I',*v));m['query_crc32']=zlib.crc32((p/'query.bin').read_bytes());reseal(p,m,'query.bin')
    elif case=='directory_semantics':
     d=json.loads((p/'directory.json').read_text());image=(p/'labels.bin').read_bytes();i=0;j=next(j for j in range(1,len(d['owners']))if image[192*i:192*(i+1)]!=image[192*j:192*(j+1)]);d['owners'][i],d['owners'][j]=d['owners'][j],d['owners'][i];d['owners'][i]['frame']=i;d['owners'][j]['frame']=j;js(p/'directory.json',d);reseal(p,m,'directory.json')
    elif case=='config_override':
     d=bytearray((p/'config_effective.bin').read_bytes());struct.pack_into('<I',d,70*4,m['context']['version']-1);write(p/'config_effective.bin',d);reseal(p,m,'config_effective.bin')
    elif case=='attempt_floor':m['recovery_attempt_floor']['version']-=1;reseal(p,m)
    elif case=='commit_identity':c=json.loads((p/'COMMIT.json').read_text());c['checkpoint']+=1;js(p/'COMMIT.json',c)
    elif case=='immutable_reference':m['immutable_resources']['tables0']['sha256']='0'*64;reseal(p,m)
    failed=False
    try:verify(p,check_immutable=case in ['valid','immutable_reference'])
    except (AssertionError,FileNotFoundError,ValueError,KeyError):failed=True
    assert failed==(case!='valid'),(name,case,failed);checks.append({'case':case,'accepted':not failed})
  for n,h in hashes.items():assert sha(src/n)==h
  results[name]=checks
 r={'status':'passed','cases':results,'checks':sum(map(len,results.values())),'source_bundles_unchanged':True,'script_sha256':sha(Path(__file__)),'verifier_sha256':sha(Path(__file__).with_name('verify_rtl_bundle.py')),'scope':'Private clone corruption and semantic inconsistency rejection, not power-cut or malicious authenticated-replay testing.'}
 (root/'bundle_integrity_tests.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({'status':'passed','checks':r['checks']}))
if __name__=='__main__':main()
