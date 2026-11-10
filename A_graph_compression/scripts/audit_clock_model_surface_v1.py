#!/usr/bin/env python3
"""Bound the installed public primitive interface against physical observations."""
import json
import re
from pathlib import Path
from check_vitis_kernel import digest, require
from run_compact_native_stack_recovery_v1 import atomic

ROOT = Path(__file__).resolve().parents[1]
LIB = Path('/inspire/hdd/global_user/guoruiyuan-253208540291/Xilinx/Vivado/2022.2/data/verilog/src/unisims')


def main():
    output = ROOT/'results/clock_public_model_surface_audit_20261025_v1.json'
    require(not output.exists(), 'Refuse overwrite')
    files = {str(Path(__file__).resolve()): digest(__file__)}
    interfaces = {}
    for name in ('BUFCE_ROW', 'BUFCE_LEAF'):
        path = LIB/(name+'.v')
        text = path.read_text()
        header = re.search(r'module\s+'+name+r'\s*#\((.*?)\);', text, re.S)
        require(header is not None, 'Cannot identify public module header')
        parameters = re.findall(r'\bparameter\s+(?:\[[^]]+\]\s*)?(\w+)\s*=', header[1])
        ports = re.findall(r'\b(?:input|output)\s+(\w+)\b', header[1])
        require(set(parameters) == {'LOC', 'CE_TYPE', 'IS_CE_INVERTED', 'IS_I_INVERTED'}, 'Public parameter surface changed')
        require(set(ports) == {'O', 'CE', 'I'}, 'Public port surface changed')
        interfaces[name] = dict(parameters=parameters, ports=ports, source=str(path))
        files[str(path)] = digest(path)
    for name in ('clock_semantics_stage_20261023_v1.json', 'clock_property_surface_stage_20261023_v1.json', 'clock_extended_observation_stage_20261023_v1.json'):
        path = ROOT/'results'/name
        report = json.loads(path.read_text())
        files[str(path)] = digest(path)
        for source, expected in report['files'].items():
            source = Path(source)
            if not source.is_absolute():
                source = ROOT/source
            require(digest(source) == expected, 'Changed physical/behavioral evidence '+str(source))
            files[str(source)] = expected
    physical = ROOT/'results/clock_property_observation_20261023_v1.json'
    observation = json.loads(physical.read_text())
    require('LCLK_TEST_DELAY' in physical.read_text() and 'CONFIG.DELAY' in physical.read_text(), 'Physical delay-control observation missing')
    atomic(output, dict(status='public_model_surface_verified_insufficient_for_physical_delay_test_semantics', interfaces=interfaces,
        installed_tool_version='2022.2', physical_property_observation=str(physical),
        conclusion='The inspected public ROW/LEAF module interfaces have no delay/test parameter or port. Their existing behavioral tests cannot establish physical LCLK_TEST_DELAY configuration semantics.',
        next_evidence_required=['Device-specific configuration semantics for the observed delay/test BEL', 'Actual constant and inversion bindings', 'Shared/fixed ownership and configuration compatibility'],
        full_clock_model_complete=False, model_change=False, files=files,
        limits=['Static interface audit, no new simulation or physical experiment', 'Does not prove that delay/test behavior is absent from hardware or from other simulation models', 'No implicit clock resource is admitted into the routing model']))
    print(output)


if __name__ == '__main__':
    main()
