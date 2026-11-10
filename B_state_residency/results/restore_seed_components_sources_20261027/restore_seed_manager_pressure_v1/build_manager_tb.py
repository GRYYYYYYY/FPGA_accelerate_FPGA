from pathlib import Path
import runpy
HERE=Path(__file__).resolve().parent
replace=runpy.run_path(str(HERE/'build.py'))['replace']

def make():
    s=(HERE.parent/'label_baseline_miss_v1/tb_miss.sv').read_text()
    s=replace(s,'module tb_baseline_miss;',
              'module tb_baseline_miss;\nreg baseline_raw_probe=0,baseline_restore_write=0;')
    s=replace(s,'reg[159:0]v0,v1,v8,want;', 'reg[159:0]v0,v1,v8,v3,want;')
    s=replace(s,'"%h %h %h",v0,v1,v8);check(rc==3);', '"%h %h %h %h",v0,v1,v8,v3);check(rc==4);')
    s=replace(s,'@(negedge clk);io_valid=0;io_node=32\'hffffffff;io_value=0;',
              '@(negedge clk);io_valid=0;baseline_restore_write=0;io_node=32\'hffffffff;io_value=0;')
    # Existing tests retain normal baseline/client, eviction and fault semantics.
    s=replace(s,' phase=5;', '''
 phase=6;$fdisplay(tf,"SEED_BEGIN");want=0;
 for(integer f=0;f<5;f=f+1)begin
  want[f*32+:32]=f==4?32'h12:32'h1000+f;
  baseline_restore_write=1;io(2,1,f,want[f*32+:32],0,want);check(misses==3);
 end
 $fdisplay(tf,"SEED_END");io(2,0,0,0,0,want);check(misses==3);
 // Illegal use must be rejected without any native or baseline command.
 $fdisplay(tf,"REJECT_BEGIN");baseline_restore_write=1;io(2,0,0,0,3,0);
 baseline_restore_write=1;io(2,1,4,256,3,0);
 baseline_restore_write=1;baseline_raw_probe=1;io(2,1,0,99,3,0);baseline_raw_probe=0;
 $fdisplay(tf,"REJECT_END");check(misses==3);io(2,0,0,0,0,want);
 // Clearing the qualifier at acceptance must not leak into the next operation.
 io(3,0,0,0,0,v3);check(misses==4);
 control(1,0);check(snapshot_clean);io(2,0,0,0,0,want);check(misses==4);
 phase=5;''')
    s=replace(s,'check(fault&&misses==4&&!io_ready&&!snapshot_clean);',
              'check(fault&&misses==5&&!io_ready&&!snapshot_clean);')
    s=replace(s,'BASELINE_MISS_PASS','RESTORE_SEED_MANAGER_PASS')
    return s

if __name__=='__main__':(HERE/'tb_seed_manager.sv').write_text(make())
