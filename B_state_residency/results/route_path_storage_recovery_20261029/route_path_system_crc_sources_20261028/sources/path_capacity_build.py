"""Isolated path-slot parameterization from the restored G3 publication sources."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
BASE = Path('/tmp/B_state_residency_offer_20261025/owner_g3_retired_full_v3/sources')
PARAMS = 'PATH_SLOTS=2,PATH_SLOT_BITS=(PATH_SLOTS<=2?1:$clog2(PATH_SLOTS)),'


def one(s, old, new):
    assert s.count(old) == 1, (old, s.count(old))
    return s.replace(old, new, 1)


def make():
    manifest = json.loads((BASE.parent / 'manifest.json').read_text())
    names = ['route_commit_controller.sv', 'route_commit_host_adapter.sv',
             'query_lifecycle.sv', 'residency_system.sv', 'search_residency_system.sv',
             'query_residency_system.sv', 'boot_restore_gate.sv', 'export_manifest.sv']
    result = {}
    for name in names:
        raw = (BASE / name).read_bytes()
        assert hashlib.sha256(raw).hexdigest() == manifest['sources'][name]['sha256']
        s = raw.decode()
        if name in ['route_commit_controller.sv', 'route_commit_host_adapter.sv', 'query_lifecycle.sv',
                    'residency_system.sv', 'search_residency_system.sv', 'query_residency_system.sv']:
            s = one(s, '#(parameter integer ', '#(parameter integer ' + PARAMS)
        if name in ['route_commit_controller.sv', 'route_commit_host_adapter.sv']:
            s = one(s, 'input wire req_op,req_slot,', 'input wire req_op,input wire[PATH_SLOT_BITS-1:0]req_slot,')
            s = one(s, '[1:0]slot_valid', '[PATH_SLOTS-1:0]slot_valid')
        if name == 'route_commit_controller.sv':
            s = one(s, 'reg owned,stopped,operation,slot;', 'reg owned,stopped,operation;reg[PATH_SLOT_BITS-1:0]slot;')
            s = s.replace('[0:1]', '[0:PATH_SLOTS-1]')
            s = one(s, 'Canonical two-slot image', 'Canonical PATH_SLOTS-slot image (default two-slot bytes unchanged)')
            s = one(s, 'CP_WORDS=2*CP_STRIDE', 'CP_WORDS=PATH_SLOTS*CP_STRIDE')
            s = one(s, 'reg cp_failed,cp_invalid,cp_importing,cp_check_slot;', 'reg cp_failed,cp_invalid,cp_importing;reg[PATH_SLOT_BITS-1:0]cp_check_slot;')
            s = one(s, 'if(cp_check_slot&&cp_check_field+1==CP_STRIDE)', 'if(cp_check_slot==PATH_SLOTS-1&&cp_check_field+1==CP_STRIDE)')
            s = one(s, 'cp_check_slot<=1;cp_check_field<=0;', 'cp_check_slot<=cp_check_slot+1\'b1;cp_check_field<=0;')
            assert s.count('a<2;') == 2 and s.count('i<2;') == 1
            s = s.replace('a<2;', 'a<PATH_SLOTS;').replace('i<2;', 'i<PATH_SLOTS;')
            s = one(s, 'if((!req_op&&slot_valid[req_slot])', 'if(req_slot>=PATH_SLOTS)begin rsp_status<=1;rsp_valid<=1;end\n     else if((!req_op&&slot_valid[req_slot])')
        elif name == 'route_commit_host_adapter.sv':
            s = one(s, 'route_commit_controller #(', 'route_commit_controller #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),')
        elif name == 'query_lifecycle.sv':
            s = one(s, '[1:0]route_slots', '[PATH_SLOTS-1:0]route_slots')
            s = one(s, 'input wire cmd_slot,', 'input wire[PATH_SLOT_BITS-1:0]cmd_slot,')
            s = one(s, "route_payload<={30'd0,", "route_payload<={{(31-PATH_SLOT_BITS){1'b0}},")
            s = one(s, 'if(label_state_dirty||', 'if(cmd_slot>=PATH_SLOTS||label_state_dirty||')
            assert s.count('route_payload[33:2]') == 2
            s = s.replace('route_payload[33:2]', 'route_payload[1+PATH_SLOT_BITS+:32]')
        elif name in ['residency_system.sv', 'search_residency_system.sv', 'query_residency_system.sv']:
            s = one(s, '[1:0] rc_slots', '[PATH_SLOTS-1:0] rc_slots')
            if name == 'residency_system.sv':
                s = one(s, 'route_commit_host_adapter #(', 'route_commit_host_adapter #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),')
                s = one(s, 'f_broute_payload[1+:1]', 'f_broute_payload[1+:PATH_SLOT_BITS]')
                for offset in [2, 34, 66, 98, 130]:
                    s = one(s, f'f_broute_payload[{offset}+:32]', f'f_broute_payload[{offset-1}+PATH_SLOT_BITS+:32]')
            elif name == 'search_residency_system.sv':
                s = one(s, '\nresidency_system #(', '\nresidency_system #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),')
            else:
                s = one(s, '\nsearch_residency_system #(', '\nsearch_residency_system #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),')
                s = one(s, 'input wire qc_cmd_slot,', 'input wire[PATH_SLOT_BITS-1:0]qc_cmd_slot,')
                s = one(s, 'query_lifecycle #(', 'query_lifecycle #(.PATH_SLOTS(PATH_SLOTS),.PATH_SLOT_BITS(PATH_SLOT_BITS),')
                s = one(s, 'input wire[1:0]boot_query,boot_slots,', 'input wire[1:0]boot_query,input wire[PATH_SLOTS-1:0]boot_slots,')
                s = one(s, 'boot_restore_gate boot_gate(', 'boot_restore_gate #(.PATH_SLOTS(PATH_SLOTS)) boot_gate(')
        elif name == 'boot_restore_gate.sv':
            s = one(s, 'module boot_restore_gate(', 'module boot_restore_gate #(parameter integer PATH_SLOTS=2)(')
            s = one(s, 'input wire[1:0]cfg_query,cfg_slots,', 'input wire[1:0]cfg_query,input wire[PATH_SLOTS-1:0]cfg_slots,')
            s = one(s, 'input wire[1:0]active_query,route_slots,', 'input wire[1:0]active_query,input wire[PATH_SLOTS-1:0]route_slots,')
            s = one(s, 'reg[1:0]query,slots;', 'reg[1:0]query;reg[PATH_SLOTS-1:0]slots;')
        else:
            s = one(s, 'module export_manifest(', 'module export_manifest #(parameter integer PATH_SLOTS=2,MAX_PATH=32)(')
            s = one(s, '[1:0]active_slots', '[PATH_SLOTS-1:0]active_slots')
            s = one(s, 'reg[1:0]query_epoch,slots;', 'reg[1:0]query_epoch;reg[PATH_SLOTS-1:0]slots;')
            s = one(s, 'reg lp,pp,qp;reg[31:0]pn,qn,pc,qc;', 'reg lp,pp,qp;reg[31:0]pn,qn,pc,qc;\n localparam PATH_STRIDE=7+MAX_PATH,PATH_WORDS=PATH_SLOTS*PATH_STRIDE;\n wire[31:0]path_slot=pn/PATH_STRIDE,path_field=pn%PATH_STRIDE;')
            s = s.replace('pn>=78', 'pn>=PATH_WORDS').replace('pn==77', 'pn==PATH_WORDS-1').replace('pn!=78', 'pn!=PATH_WORDS')
            start=s.index('     if((pn==0&&');end=s.index('     pc<=fold',start)
            s=s[:start]+'''     if(path_slot<PATH_SLOTS)begin
      if((path_field==0&&path_data!={31'd0,slots[path_slot]})||
         (path_field==1&&slots[path_slot]&&(path_data==0||path_data>MAX_PATH))||
         (path_field==5&&slots[path_slot]&&path_data!=bound_design[31:0])||
         (path_field==6&&slots[path_slot]&&path_data!=bound_design[63:32]))fault<=1;
     end
'''+s[end:]
        result[name] = s
    return result


if __name__ == '__main__':
    for name, text in make().items():
        (HERE / name).write_text(text)
    print('GENERATED_PATH_CAPACITY', len(make()))
