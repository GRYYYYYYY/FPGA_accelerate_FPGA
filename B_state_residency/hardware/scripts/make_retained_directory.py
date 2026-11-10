"""Add a trusted, internal ID-only recycle operation to a frozen directory."""
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]

def generate(text):
    changes = {
        'module backing_frame_directory_indexed #(': 'module backing_frame_directory_retained #(',
        'RECYCLE=4,LOOKUP=5;': 'RECYCLE=4,LOOKUP=5,RECYCLE_TX=6;',
        '                    RECYCLE:begin': '''                    // Internal only: caller proves exclusive query and full drain.
                    // Free leases alone do not establish end-to-end quiescence.
                    RECYCLE_TX:begin
                        if(leased!=0 || !fence_retired)rsp_status<=BUSY;
                        else begin tx_used<=0;last_tx<=0;end
                    end
                    RECYCLE:begin''',
    }
    for before, after in changes.items():
        assert text.count(before) == 1, before
        text = text.replace(before, after)
    return text

if __name__ == '__main__':
    source = ROOT / 'hardware/rtl/backing_frame_directory_indexed.sv'
    (ROOT / 'hardware/rtl/backing_frame_directory_retained.sv').write_text(generate(source.read_text()))
