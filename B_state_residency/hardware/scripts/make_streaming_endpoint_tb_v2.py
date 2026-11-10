"""Correct only watchdog sizing and the progress timestamp label."""
from pathlib import Path
from make_streaming_endpoint_tb import generate as original

ROOT = Path(__file__).resolve().parents[2]


def generate():
    text = original()
    assert text.count('#500000000000;') == 1
    assert text.count('time_ns=%0t') == 1
    return text.replace('#500000000000;', "#(64'd500000000000);").replace('time_ns=%0t', 'time_ps=%0t')


if __name__ == '__main__':
    target = ROOT / 'hardware/tb/tb_memory_endpoint_stream_v2.sv'
    if target.exists():
        raise FileExistsError(target)
    target.write_text(generate())
