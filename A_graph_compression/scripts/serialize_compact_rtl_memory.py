#!/usr/bin/env python3
"""Serialize owned compact elaboration against an existing large snapshot compiler."""
import json,os,signal,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
BASE=Path('/tmp/A_graph_compression_recovery_20261025_v1')
def identity(pid):
 p=Path('/proc',str(pid));fields=(p/'stat').read_text().rsplit(')',1)[1].split()
 return dict(pid=pid,start_ticks=fields[19],command=(p/'cmdline').read_bytes().replace(b'\0',b' ').decode(),cwd=str((p/'cwd').resolve()))
def main():
 out=ROOT/'data/derived/compact_rtl_memory_serialization_20261025_v1';out.mkdir(exist_ok=False)
 target=1509104;blocking=2516537;who=identity(target);block=identity(blocking)
 assert who['cwd']==str(BASE/'compressed_batch_compact_rtl_guarded_v1/sim/verilog') and '/xelab ' in who['command']
 assert block['cwd']==str(BASE/'snapshot_rtl_local_project/solution/sim/verilog') and '/xelab ' in block['command']
 state=dict(owner_pid=os.getpid(),status='running',stage='suspend_existing_compact',target=who,blocking_compiler=block,required_free_bytes=184*1024**3)
 def save():
  p=out/'state.tmp';p.write_text(json.dumps(state,indent=2)+'\n');p.replace(out/'state.json')
 def resource():
  cg=Path('/sys/fs/cgroup');maximum=int((cg/'memory.max').read_text());current=int((cg/'memory.current').read_text())
  return dict(maximum_bytes=maximum,current_bytes=current,free_bytes=max(0,maximum-current),events=(cg/'memory.events').read_text())
 (out/'before.json').write_text(json.dumps(resource(),indent=2)+'\n');save()
 assert identity(target)==who
 os.kill(target,signal.SIGSTOP);time.sleep(.2)
 assert Path('/proc',str(target),'stat').read_text().rsplit(')',1)[1].split()[0] in ['T','t']
 state['stage']='waiting_original_snapshot_compiler_and_cgroup_headroom';save()
 try:
  while True:
   assert identity(target)==who,'Suspended compiler identity changed'
   try:same_block=identity(blocking)==block
   except FileNotFoundError:same_block=False
   memory=resource();state['memory']=memory;state['blocking_compiler_live']=same_block;save()
   if not same_block and memory['free_bytes']>=state['required_free_bytes']:break
   time.sleep(30)
  assert identity(target)==who
  os.kill(target,signal.SIGCONT)
  state.update(status='complete',stage='same_compact_compiler_resumed_after_memory_gate');save()
 except BaseException as e:
  state.update(status='failed',error=str(e),resume_required_for_existing_pid=target);save();raise
if __name__=='__main__':main()
