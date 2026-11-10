"""Legacy compatibility (excluding newly assigned opcode6) and checkpoint mutants."""
from pathlib import Path
import hashlib,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[2]
BIN=Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/bin')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 out=Path(sys.argv[1]).resolve();out.mkdir();sources=out/'sources';sources.mkdir()
 parent=ROOT/'results/rtl_retained_directory_20261023/classified_manifest.json'
 assert sha(parent)=='bf6ec0fbf3c7912b6fbfdcb73851a8caf69bfd9cae1c0b723422241798069981'
 frozen=json.loads(parent.read_text())
 for path,digest in frozen['sources'].items():assert sha(Path(path))==digest
 paths=['hardware/rtl/backing_frame_directory_retained.sv','hardware/rtl/backing_frame_directory_lookup.sv','hardware/tb/tb_retained_directory.sv','hardware/tb/tb_indexed_directory.sv','hardware/scripts/verify_retained_directory.py']
 m={'status':'running','sources':{},'parent_sha256':sha(parent),'cases':{},'rtl_checkpoint_integrated':False}
 for name in paths:
  p=ROOT/name;shutil.copyfile(p,sources/p.name);m['sources'][name]=sha(p)
 tb=(sources/'tb_indexed_directory.sv').read_text();assert tb.count('backing_frame_directory_indexed #(')==1
 (sources/'tb_compatibility.sv').write_text(tb.replace('backing_frame_directory_indexed #(','backing_frame_directory_retained #('))
 vectors=ROOT/'results/indexed_directory_vectors_20261023';vm=json.loads((vectors/'manifest.json').read_text())
 for name,digest in vm['artifacts'].items():assert sha(vectors/name)==digest
 m['vector_manifest_sha256']=sha(vectors/'manifest.json')
 rows=(vectors/'small.txt').read_text().splitlines(True)
 removed=[(i,line) for i,line in enumerate(rows) if int(line.split()[0],16)==6]
 assert len(removed)==10
 (out/'small_legacy.txt').write_text(''.join(line for line in rows if int(line.split()[0],16)!=6))
 m['legacy_exclusion']={'reason':'opcode6 now assigned RECYCLE_TX; formerly BAD. All other legacy stimuli unchanged.', 'removed_zero_based_rows':removed, 'adapted_sha256':sha(out/'small_legacy.txt')}
 def save():(out/'manifest.json').write_text(json.dumps(m,indent=2)+'\n')
 def run(name,rtl,tb,top,vector=None,expected=None,negative=False):
  folder=out/name;folder.mkdir();(folder/'simulate.tcl').write_text('run 1s\nquit\n')
  row={'status':'running','commands':[]};m['cases'][name]=row;save()
  commands=[('compile',[BIN/'xvlog','--sv',sources/'backing_frame_directory_lookup.sv',rtl,tb]),('elaborate',[BIN/'xelab',top,'-s','test_tb','--debug','typical','--mt','2']),('simulate',[BIN/'xsim','test_tb','--tclbatch','simulate.tcl','--log','simulate.log']+(['--testplusarg','VECTORS='+str(vector)] if vector else []))]
  for stage,cmd in commands:
   args=list(map(str,cmd))
   with (folder/(stage+'.stdout.log')).open('w') as log:
    proc=subprocess.Popen(args,cwd=folder,stdout=log,stderr=subprocess.STDOUT)
    receipt={'stage':stage,'argv':args,'pid':proc.pid,'exit_code':None};row['commands'].append(receipt);save();receipt['exit_code']=proc.wait();save()
   if receipt['exit_code'] and (stage!='simulate' or not negative):raise RuntimeError(name+'/'+stage)
  text=(folder/'simulate.log').read_text();fatal=[l for l in text.splitlines() if l.startswith('Fatal:')]
  if negative:
   assert fatal and expected in fatal[0] and 'RETAINED_DIRECTORY_PASS' not in text,(name,text[-1000:])
   row.update(status='detected',first_failure=fatal[0])
  else:
   lines=[l for l in text.splitlines() if l.startswith('TEST_PASS indexed_directory ')]
   assert len(lines)==1 and not fatal and '$finish' in text
   counters=dict(item.split('=') for item in lines[0].split()[2:]);assert int(counters['checks'])==expected
   row.update(status='passed',counters=counters)
   if name=='legacy_large':row['counters']['ref_cycles']=None # reference disabled; mirrored counter is not baseline
  row['artifacts']={p.name:sha(p) for p in folder.iterdir() if p.is_file() and p.suffix in ('.log','.tcl')};save();print(name,row['status'],flush=True)
 save()
 try:
  run('legacy_small',sources/'backing_frame_directory_retained.sv',sources/'tb_compatibility.sv','tb_indexed_directory_small',out/'small_legacy.txt',1450)
  run('legacy_large',sources/'backing_frame_directory_retained.sv',sources/'tb_compatibility.sv','tb_indexed_directory_large',vectors/'large.txt',66261)
  original=(sources/'backing_frame_directory_retained.sv').read_text()
  block='''RECYCLE_TX:begin
                        if(leased!=0 || !fence_retired)rsp_status<=BUSY;
                        else begin tx_used<=0;last_tx<=0;end
                    end'''
  assert original.count(block)==1
  variants={
   'skip_id_reset':block.replace('tx_used<=0;last_tx<=0;','last_tx<=last_tx;'),
   'drop_allocation':block.replace('tx_used<=0;last_tx<=0;','tx_used<=0;last_tx<=0;allocated<=0;'),
   'ignore_leases':block.replace('leased!=0 || !fence_retired','!fence_retired'),
   'ignore_fence':block.replace('leased!=0 || !fence_retired','leased!=0'),
  }
  for name,changed in variants.items():
   path=sources/(name+'.sv');path.write_text(original.replace(block,changed))
   run(name,path,sources/'tb_retained_directory.sv','tb_retained_directory',expected='retained allocation' if name=='drop_allocation' else 'status check=',negative=True)
  for name,digest in m['sources'].items():assert sha(ROOT/name)==digest
  m['status']='passed';m['artifacts']={str(p.relative_to(out)):sha(p) for p in sources.iterdir() if p.is_file()};save()
  (out/'completion_audit.json').write_text(json.dumps({'status':'passed','manifest_sha256':sha(out/'manifest.json')},indent=2)+'\n')
 except Exception as exc:
  m.update(status='failed',error=repr(exc));save();raise
if __name__=='__main__':main()
