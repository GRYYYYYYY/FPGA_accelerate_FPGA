"""Preserve old stimuli/observers while isolating the stage-only CP candidate."""
from pathlib import Path
import importlib.util


def build(root,mode,suite):
    root=Path(root);assert mode in ['baseline','default','factored']
    prior=root/'hardware/variants/route_stage_write_v1/build_tb.py'
    spec=importlib.util.spec_from_file_location('preserved_stage_unit_observers',prior)
    helper=importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    text,marker=helper.build(root,mode,suite)
    assert text.count('.FACTORED_PATH_WRITES(1),')==1
    text=text.replace('.FACTORED_PATH_WRITES(1),','',1)
    if mode=='factored':
        assert text.count('.FACTORED_STAGE_WRITES(1),')==1
        text=text.replace('.FACTORED_STAGE_WRITES(1),','.STATIC_STAGE_WRITES(1),',1)
    assert 'FACTORED_PATH_WRITES' not in text and 'FACTORED_STAGE_WRITES' not in text
    assert text.count('.STATIC_STAGE_WRITES(1),')==int(mode=='factored')
    return text,marker
