"""Gated candidate overlay and passive original-controller full-system observer."""
from pathlib import Path
import re
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from host_edit_system_common_v1 import BASE,sha,read,identity,restored,verify_freeze

REFERENCE=BASE/'checkpoint_host_edit_system_v1'
CANDIDATE=ROOT/'hardware/variants/config_native_publication_v1'
DUT='system.inner.backend.config_restore'
MODEL='config_restore_controller_observer.sv'
STATE=['state','configured','stopped','error_code','elapsed','current_version','tx_version',
       'descriptor','prepared','shadow_payload','shadow_design','shadow_checkpoint']
DECL='module tb_candidate_offer;'
FINISH=' $display("FOURTH_WARM_PASS polls=83 expands=82 candidates=402 costs=231");'
TOOLS=['run_config_native_publication_system_v1.py','audit_config_native_publication_system_v1.py',
       'freeze_config_native_publication_system_v1.py','archive_offer_result.py',
       'verify_search_retire_restore.py','restore_offer_result.py','host_edit_system_common_v1.py',
       'config_publication_units_common_v1.py','check_host_edit_trace_v1.py']


def ports(source):
    header=source.split(')(\n',1)[1].split('\n);',1)[0]
    result=[];direction=None;width=''
    for token in header.split(','):
        token=token.strip()
        match=re.fullmatch(r'(input|output)\s+(?:wire|reg)\s*(\[[0-9]+:[0-9]+\])?\s*([a-zA-Z_][a-zA-Z_0-9]*)',token)
        if match:direction,width,name=match[1],match[2] or '',match[3]
        else:
            assert direction is not None and re.fullmatch(r'[a-zA-Z_][a-zA-Z_0-9]*',token),token
            name=token
        result.append((direction,width,name))
    assert len({name for _,_,name in result})==len(result)
    outputs=[(w,n) for d,w,n in result if d=='output']
    def bits(w):return 1 if not w else int(w[1:].split(':')[0])-int(w.split(':')[1][:-1])+1
    assert len(outputs)==25 and sum(bits(w) for w,_ in outputs)==7238
    return result


def reference_source(original):
    old='module config_restore_controller #('
    new='module config_restore_controller_observer #('
    assert original.count(old)==1 and new not in original
    result=original.replace(old,new,1);assert result.replace(new,old,1)==original
    return result


def instrument(original,controller):
    assert original.count(DECL)==original.count(FINISH)==original.count('\nendmodule')==1
    assert 'np_reference' not in original and 'CONFIG_NATIVE_SYSTEM_PASS' not in original
    assert not re.search(r'\bnp_[a-zA-Z_0-9]+',original)
    parsed=ports(controller);outputs=[(width,name) for direction,width,name in parsed if direction=='output']
    declarations='\n integer np_cycles=0,np_checks=0,np_loads=0,np_load_replies=0,np_stages=0,np_captures=0;\n'
    declarations+=' integer np_publications=0,np_discards=0,np_prepared=0;reg np_stage_edge=0;\n'
    declarations+=''.join(f' wire{width} np_{name};\n' for width,name in outputs)
    mappings=[]
    for direction,width,name in parsed:
        if direction=='output':value='np_'+name
        elif name=='load_payload':value=f'{DUT}.load_stage?np_active_payload:{DUT}.load_payload'
        else:value=DUT+'.'+name
        mappings.append('.'+name+'('+value+')')
    instance='\n config_restore_controller_observer #(.MAX_CYCLES(1048576)) np_reference(\n  '+',\n  '.join(mappings)+');\n'
    actual_state='{'+','.join(DUT+'.'+n for n in STATE)+'}'
    reference_state='{'+','.join('np_reference.'+n for n in STATE)+'}'
    actual_outputs='{'+','.join(DUT+'.'+n for _,n in outputs)+'}'
    reference_outputs='{'+','.join('np_'+n for _,n in outputs)+'}'
    before='''
 always @(posedge clk)if(!__D__.rst)begin
  np_cycles=np_cycles+1;
  if((^{__D__.load_valid,__D__.load_ready,__D__.load_stage,__D__.publish_permit,
        __D__.publish_valid,__D__.publish_ready,__D__.discard_valid,__D__.discard_ready})===1'bx)
   $fatal(1,"native config actual control unknown");
  if(__D__.load_stage!==__D__.publish_permit)$fatal(1,"native config stage/permit alias");
  np_stage_edge=__D__.load_valid&&__D__.load_ready&&__D__.load_stage;
  if(__D__.load_valid&&__D__.load_ready)np_loads=np_loads+1;
  if(__D__.load_rsp_valid&&__D__.load_rsp_ready)np_load_replies=np_load_replies+1;
  if(np_stage_edge)begin
   np_stages=np_stages+1;
   if(__D__.load_payload!==__D__.active_payload||__D__.load_authoritative!==1'b1)
    $fatal(1,"native config actual accepted-stage feedback contract");
  end
  if(__D__.publish_valid&&__D__.publish_ready)np_publications=np_publications+1;
  if(__D__.discard_valid&&__D__.discard_ready)np_discards=np_discards+1;
  if(__D__.prepared===1'b1)begin
   np_prepared=np_prepared+1;
   if({__D__.shadow_payload[2303:2272],__D__.shadow_payload[2239:0]}!==
      {__D__.descriptor[2303:2272],__D__.descriptor[2239:0]})
    $fatal(1,"native config prepared non-version bank before NBA");
  end
  #0.1;
  if(np_stage_edge&&__D__.load_status===1'b0&&__D__.prepared===1'b1)np_captures=np_captures+1;
  if(__D__.prepared===1'b1&&
     {__D__.shadow_payload[2303:2272],__D__.shadow_payload[2239:0]}!==
     {__D__.descriptor[2303:2272],__D__.descriptor[2239:0]})
   $fatal(1,"native config prepared non-version bank after NBA");
'''.replace('__D__',DUT)
    comparison='  if('+actual_state+'!=='+reference_state+')$fatal(1,"native config complete original-state mismatch");\n'
    comparison+='  if('+actual_outputs+'!=='+reference_outputs+')$fatal(1,"native config complete original-output mismatch");\n'
    comparison+='  np_checks=np_checks+1;\n end\n'
    finish=''' if(np_checks==0||np_checks!=np_cycles||np_loads==0||np_loads!=np_load_replies||
    np_stages==0||np_captures==0||np_publications==0||np_prepared==0||
    np_publications>np_captures||np_captures>np_stages||np_stages>np_loads)
  $fatal(1,"native config full-system observation coverage missing");
 $display("CONFIG_NATIVE_SYSTEM_PASS cycles=%0d checks=%0d loads=%0d replies=%0d stages=%0d captures=%0d publications=%0d discards=%0d prepared=%0d",np_cycles,np_checks,np_loads,np_load_replies,np_stages,np_captures,np_publications,np_discards,np_prepared);
'''
    observation=instance+before+comparison
    result=original.replace(DECL,DECL+declarations).replace('\nendmodule',observation+'\nendmodule').replace(FINISH,finish+FINISH)
    recovered=result.replace(DECL+declarations,DECL,1).replace(observation+'\nendmodule','\nendmodule',1).replace(finish+FINISH,FINISH,1)
    assert recovered==original
    assert not re.search(r'\b(force|release)\s',observation+finish)
    assert not re.search(r'\bsystem\.[\w.\[\]:]+\s*(?:<=|=(?!=))',observation)
    return result


def evidence(reference):
    assert reference==REFERENCE
    report=ROOT/'results/config_native_publication_units_20261030.json'
    assert report.exists(),'Wait for five candidate unit modes actual restore/freeze'
    unit_freeze=verify_freeze(ROOT/'results/config_native_publication_units_sources_20261030')
    units=BASE/'config_native_publication_units_v1';um,ua,unit_files=restored(units)
    accepted=read(report)
    assert accepted['status']=='five_native_publication_unit_modes_restored' and accepted['audit']==ua
    assert um['stage']=='complete' and identity(um['runner_pid'])!=str(um['runner_start_ticks'])
    assert ua['full_bank_cycle_comparisons']==ua['exact_event_comparisons']==3 and len(ua['cases'])==5
    assert ua['native_prepared_full_nonversion_invariant'] and ua['generic_default_preserves_unaliased_xz_counterexample']
    tools_receipt=ROOT/'results/config_native_publication_system_tools_preparation_20261030.json'
    tools=read(tools_receipt)
    assert tools['status']=='native_publication_full_system_tools_prepared_not_executed'
    assert set(tools['tools'])=={str(ROOT/'scripts'/n) for n in TOOLS}|{str(HERE/'build.py')}
    for path,digest in tools['tools'].items():assert sha(path)==digest
    from config_publication_units_common_v1 import host_pair_evidence
    predecessors=host_pair_evidence()
    rm,ra,reference_files=restored(reference)
    assert rm['mode']=='cp' and rm['stage']=='complete' and len(ra['exact_comparisons'])==27
    assert identity(rm['runner_pid'])!=str(rm['runner_start_ticks'])
    cm=read(CANDIDATE/'manifest.json')
    assert ua['candidate_manifest_sha256']==sha(CANDIDATE/'manifest.json')
    for path,digest in cm['bound'].items():assert sha(path)==digest
    for name,entry in cm['sources'].items():
        assert sha(CANDIDATE/'baseline'/name)==entry['baseline']==sha(reference/'sources'/name)==rm['sources'][name]['sha256']
        assert sha(CANDIDATE/'fixed'/name)==entry['fixed']
    sm=read(BASE/'checkpoint_edit_synth_v1/manifest.json');assert len(sm['rtl'])==133
    assert len(rm['rtl'])==136 and set(rm['rtl'])==set(sm['rtl'])|{'tb_query_fault.sv','tb_directory_observer.sv','axi_file_memory.sv'}
    for name in sm['rtl']:assert sha(reference/'sources'/name)==rm['sources'][name]['sha256']==sm['sources'][name]
    files=[report,unit_freeze,CANDIDATE/'manifest.json',HERE/'build.py',tools_receipt]+unit_files+reference_files
    files += [CANDIDATE/role/name for role in ['baseline','fixed'] for name in cm['sources']]
    files += [ROOT/'scripts'/n for n in TOOLS]
    predecessors.update({str(p):sha(p) for p in files})
    return predecessors


def sources(reference):
    proof=evidence(reference)
    fixed={name:(CANDIDATE/'fixed'/name).read_text() for name in ['config_restore_controller.sv','residency_system.sv']}
    original=(CANDIDATE/'baseline/config_restore_controller.sv').read_text()
    model=reference_source(original)
    tb=instrument((reference/'sources/tb_query_fault.sv').read_text(),original)
    return fixed,model,tb,proof
