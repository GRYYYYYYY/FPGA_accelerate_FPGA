"""Extend frozen G3 warm TB to four slots, real G4 rotation and natural q4."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
BASE = Path('/tmp/B_state_residency_offer_20261025/third_warm_full_v2')


def make():
    m = json.loads((BASE/'manifest.json').read_text())
    s = (BASE/'sources/tb_query_fault.sv').read_text()
    assert hashlib.sha256(s.encode()).hexdigest() == m['sources']['tb_query_fault.sv']['sha256']
    def change(a, b):
        nonlocal s
        assert a in s, a
        s = s.replace(a, b)
    change('.PATH_SLOTS(3)', '.PATH_SLOTS(4)')
    change('wire[2:0]rc_slots', 'wire[3:0]rc_slots')
    change('reg[2:0]qcp_slots', 'reg[3:0]qcp_slots')
    change('.boot_slots(2\'d0)', '.boot_slots(4\'d0)')
    change('[0:116]', '[0:155]')
    change('x<117', 'x<156')
    change('x==116', 'x==155')
    change('reg g3_phase=0', 'reg g4_phase=0;reg g3_phase=0')
    change("g3_phase ? 64'h100000003 : 64'h100000002", "g4_phase ? 64'h100000004 : (g3_phase ? 64'h100000003 : 64'h100000002)")
    change("g3_phase ? 32'd19 : 32'd18", "g4_phase ? 32'd20 : (g3_phase ? 32'd19 : 32'd18)")
    for suffix in ['00000000', '08aaff40', '08b81dc0']:
        change(f"g3_phase ? 64'hc0{suffix} : 64'ha0{suffix}", f"g3_phase&&!g4_phase ? 64'hc0{suffix} : 64'ha0{suffix}")
    change(".cmd_generation(64'h100000003)", ".cmd_generation(g4_phase ? 64'h100000004 : 64'h100000003)")
    change(".cmd_checkpoint(g3_op==0 ? 64'd17 : 64'd19)", ".cmd_checkpoint(g3_op==0 ? 64'd17 : (g4_phase ? 64'd20 : 64'd19))")
    change("as_bound_generation==64'h100000002 ?", "(as_bound_generation==64'h100000002||as_bound_generation==64'h100000004) ?")
    change(".publish_generation(64'h100000003)", ".publish_generation(g4_phase ? 64'h100000004 : 64'h100000003)")
    change(".publish_checkpoint(64'd19)", ".publish_checkpoint(g4_phase ? 64'd20 : 64'd19)")
    change(".publish_destination(64'hc000000000)", ".publish_destination(g4_phase ? 64'ha000000000 : 64'hc000000000)")
    change(".destination_base(64'hc000000000)", ".destination_base(g4_phase ? 64'ha000000000 : 64'hc000000000)")
    change('.MAX_BEATS(1),.TERTIARY_WRITABLE(1),.TAG("g3copy")', '.MAX_BEATS(1),.SECONDARY_WRITABLE(1),.TERTIARY_WRITABLE(1),.TAG("g3copy")')
    change(".target_generation(64'h100000003)", ".target_generation(g4_phase ? 64'h100000004 : 64'h100000003)")
    change(".target_checkpoint(32'd19)", ".target_checkpoint(g4_phase ? 32'd20 : 32'd19)")
    change('(g3_phase ? 180328 : 180327)', '(g4_phase ? 180329 : (g3_phase ? 180328 : 180327))')
    change('ss_polls!=(query_index==0?171:114)', 'ss_polls!=(query_index==0?171:(query_index==3?83:114))')
    change('ss_expands!=(query_index==0?170:113)', 'ss_expands!=(query_index==0?170:(query_index==3?82:113))')
    change('(query_index==1?564:565)', '(query_index==1?564:(query_index==3?402:565))')
    # Preserve G3 recovery source file; G4 export has a separate physical artifact.
    change('if(g3_phase)begin if(!$value$plusargs("g3imports=%s",warm_path))', 'if(g4_phase)begin if(!$value$plusargs("g4imports=%s",warm_path))$fatal(1,"G4 label output path");end else if(g3_phase)begin if(!$value$plusargs("g3imports=%s",warm_path))')
    for tag in ['LABEL_BEGIN','LABEL_DONE','FRAME_REQUEST','FRAME_REPLY','LABEL_RECORD']:
        # Insert the G4 branch with identical data fields before the old G3 branch.
        start = s.index(f'if(g3_phase)$fdisplay(trace,"G3_{tag}')
        end = s.index(';', start) + 1
        old = s[start:end]
        s = s[:start] + old.replace('if(g3_phase)', 'if(g4_phase)').replace('"G3_', '"G4_') + 'else ' + old + s[end:]
    # Duplicate the already tested protocol, changing only the actual new identities.
    start = s.index('task publish_g3;')
    end = s.index('end endtask', start) + len('end endtask')
    publish = s[start:end].replace('task publish_g3;', 'task publish_g4;')
    for a,b in [("64'h100000003","64'h100000004"),("64'h100000002","64'h100000003"),
                ('!=19','!=20'),('!=18','!=19'),('joint_pulses!=2','joint_pulses!=3'),
                ('joint_pulses!=1','joint_pulses!=2'),('180328','180329'),
                ('qcp_image[6]!=5','qcp_image[6]!=6'),("32'h57","32'h58"),('G3','G4')]:
        publish = publish.replace(a,b)
    publish = publish.replace('cap_path_image[39]!=1||', 'cap_path_image[39]!=1||cap_path_image[78]!=1||cap_path_image[117]!=0||')
    start = s.index('task cumulative_g3_copy;')
    end = s.index('end endtask', start) + len('end endtask')
    copy = s[start:end].replace('task cumulative_g3_copy;begin', 'task cumulative_g4_copy;begin\n g4_phase=1;\n $fdisplay(trace,"G4_ROTATION_BEGIN %0d %0d %0d %0d",cycles,as_rbeats,g3_memory.rbeats,g3_memory.wbeats);')
    for a,b in [("64'h100000003","64'h100000004"),("64'h100000002","64'h100000003"),
                ('g3_rc!=19','g3_rc!=20'),('k_saved_checkpoint!=18','k_saved_checkpoint!=19'),
                ("64'hc000000000","64'ha000000000"),('rc_slots!=3','rc_slots!=7'),('180328','180329'),('G3','G4')]:
        copy = copy.replace(a,b)
    copy = copy.replace('end endtask', '$fdisplay(trace,"G4_ROTATION_COPIED %0d %0d %0d %0d",cycles,as_rbeats,g3_memory.rbeats,g3_memory.wbeats);\nend endtask')
    change(' third_query;\n', ' third_query;\n cumulative_g4_copy;\n publish_g4;\n fourth_query;\n')
    tasks = (HERE/'fourth_tasks.sv').read_text()
    return s.replace('\nendmodule', '\n'+copy+'\n'+publish+'\n'+tasks+'\nendmodule')


if __name__ == '__main__':
    (HERE/'tb_fourth.sv').write_text(make())
