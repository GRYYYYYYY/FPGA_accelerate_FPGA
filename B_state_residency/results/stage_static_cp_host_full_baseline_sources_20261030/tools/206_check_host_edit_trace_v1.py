"""Independent suffix/CRC parser. This is not the full source-bound run auditor."""
import hashlib
import re
import struct
import zlib


def crc(words):
    assert len(words) == 10
    return zlib.crc32(struct.pack('<10I', *words)) & 0xffffffff


def hexadecimal(token, digits=8):
    assert re.fullmatch(r'[0-9a-fA-F]{' + str(digits) + r'}', token), token
    return int(token, 16)


def check(trace, stdout, original_trace):
    assert not re.search(r'(?im)^\s*(Fatal|ERROR)\s*:', stdout)
    lines, old = trace.splitlines(keepends=True), original_trace.splitlines(keepends=True)
    ends = [i for i, line in enumerate(lines) if line.startswith('FOURTH_PASS ')]
    old_ends = [i for i, line in enumerate(old) if line.startswith('FOURTH_PASS ')]
    assert len(ends) == len(old_ends) == 1
    assert lines[:ends[0] + 1] == old[:old_ends[0] + 1], 'Original trace prefix changed'
    prefix = ''.join(old[:old_ends[0] + 1])
    suffix = lines[ends[0] + 1:]
    combined = [line.split()[0] for line in suffix if line.startswith(('HOST_EDIT_', 'QCM ', 'QCS ', 'QCP '))]
    combined_expected = (['HOST_EDIT_CLEAN_WORD'] * 10 +
        ['HOST_EDIT_BEGIN', 'HOST_EDIT_LABEL_BEFORE', 'HOST_EDIT_WRITE', 'HOST_EDIT_WRITE_REPLY', 'HOST_EDIT_LABEL_AFTER'] +
        ['HOST_EDIT_DIRTY_WORD', 'QCM'] * 10 + ['QCP', 'HOST_EDIT_CP_REPLY'] +
        ['QCS'] * 10 + ['HOST_EDIT_CP_CHECK', 'QCP', 'HOST_EDIT_CP_REPLY'] +
        ['QCS'] * 10 + ['HOST_EDIT_CP_CHECK', 'QCP', 'HOST_EDIT_CP_REPLY', 'HOST_EDIT_PASS'])
    assert combined == combined_expected, 'Host-edit and raw CP event ordering differs'
    rows = [line.split() for line in suffix if line.startswith('HOST_EDIT_')]
    expected = (['CLEAN_WORD'] * 10 + ['BEGIN', 'LABEL_BEFORE', 'WRITE', 'WRITE_REPLY', 'LABEL_AFTER']
                + ['DIRTY_WORD'] * 10 + ['CP_REPLY', 'CP_CHECK', 'CP_REPLY', 'CP_CHECK', 'CP_REPLY', 'PASS'])
    assert [r[0] for r in rows] == ['HOST_EDIT_' + n for n in expected]
    cycles = [int(r[1]) for r in rows]
    assert cycles == sorted(cycles)
    assert cycles[0] == int(lines[ends[0]].split()[1])
    grouped = {}
    for row in rows:
        grouped.setdefault(row[0][10:], []).append(row[1:])

    def words(name):
        data = grouped[name]
        assert len(data) == 10 and all(len(row) == 3 for row in data)
        assert [int(row[1]) for row in data] == list(range(10))
        return [hexadecimal(row[2]) for row in data]

    clean, dirty = words('CLEAN_WORD'), words('DIRTY_WORD')
    old_words = [line.split() for line in prefix.splitlines() if line.startswith('FOURTH_QUERY_WORD ')]
    assert len(old_words) == 10 and [int(row[2]) for row in old_words] == list(range(10))
    assert clean == [hexadecimal(row[3]) for row in old_words]
    assert clean[0:2] == [0x51435031, 1] and clean[4:10] == [4, 1, 8, 0x62, 180330, 0]
    assert (clean[3] << 32 | clean[2]) != 0
    assert dirty == [word ^ (0x80 if i == 7 else 0) for i, word in enumerate(clean)]
    clean_crc, dirty_crc = crc(clean), crc(dirty)
    assert clean_crc != dirty_crc and hexadecimal(lines[ends[0]].split()[-1]) == clean_crc
    begin = grouped['BEGIN'][0]
    assert len(begin) == 4 and hexadecimal(begin[1]) == clean_crc
    assert list(map(int, begin[2:])) == [3, 20]
    before, after = grouped['LABEL_BEFORE'][0], grouped['LABEL_AFTER'][0]
    assert len(before) == len(after) == 2
    label = hexadecimal(before[1], 40)
    assert hexadecimal(after[1], 40) == label
    write = grouped['WRITE'][0]
    assert len(write) == 4 and list(map(int, write[1:3])) == [66893, 3]
    assert hexadecimal(write[3]) == (label >> 96 & 0xffffffff)
    reply = grouped['WRITE_REPLY'][0]
    assert len(reply) == 2 and int(reply[1]) == 0
    assert int(before[0]) < int(write[0]) <= int(reply[0]) < int(after[0])

    checks = grouped['CP_CHECK']
    assert len(checks) == 2
    for row, phase, checksum in zip(checks, [3, 4], [clean_crc, dirty_crc]):
        assert len(row) == 15 and int(row[1]) == phase
        assert hexadecimal(row[2]) == hexadecimal(row[3]) == checksum
        assert list(map(int, row[4:6])) == [1, int(phase == 4)]
        assert list(map(int, row[6:12])) == [0] * 6
        assert list(map(int, row[12:])) == [1, 180330, 180330]
    cp_replies = grouped['CP_REPLY']
    for row, phase, status, checksum, pending in zip(cp_replies, [2, 3, 4], [0, 1, 0],
                                                   [dirty_crc, clean_crc, dirty_crc], [0, 1, 1]):
        assert len(row) == 5 and list(map(int, row[1:3])) == [phase, status]
        assert hexadecimal(row[3]) == checksum and int(row[4]) == pending

    # Validate the existing raw CP stream monitor, independently of new word displays.
    old_receipts = [line.split() for line in prefix.splitlines() if line.startswith('QCP ')]
    # Three earlier rebase commands use a different receipt path. The original
    # actual-port monitor has 12 commands, while this task's local index reaches 9.
    assert len(old_receipts) == 9 and [int(row[1]) for row in old_receipts] == list(range(9))
    raw = [line.split() for line in suffix if line.startswith(('QCM ', 'QCS ', 'QCP '))]
    expected_raw = []
    for kind, index, data, status, checksum, pending in [
        ('QCM', 9, dirty, 0, dirty_crc, 0),
        ('QCS', 10, clean, 1, clean_crc, 1),
        ('QCS', 11, dirty, 0, dirty_crc, 1),
    ]:
        expected_raw += [[kind, str(index), str(i), f'{word:08x}', str(int(i == 9))] for i, word in enumerate(data)]
        expected_raw += [['QCP', str(index), str(status), f'{checksum:08x}', str(pending), '180330']]
    assert raw == expected_raw, 'Actual checkpoint streams/replies differ'

    end = grouped['PASS'][0]
    assert len(end) == 20
    assert list(map(int, end[1:11])) == [3, 3, 1, 1, 3, 3, 20, 10, 1, 1]
    atomic, elapsed = map(int, end[11:13])
    assert 0 < atomic <= elapsed <= 100000
    assert int(end[0]) - int(begin[0]) == elapsed
    assert hexadecimal(end[13]) == clean_crc and hexadecimal(end[14]) == dirty_crc
    assert list(map(int, end[15:])) == [0, 1, 180330, 15, 0]
    passes = re.findall(r'^HOST_EDIT_NATIVE_PASS writes=(\d+) replies=(\d+) clean_rejected=(\d+) '
                        r'dirty_accepted=(\d+) atomic_checks=(\d+)$', stdout, re.M)
    assert passes == [('1', '1', '1', '1', str(atomic))]
    cp = re.findall(r'^CHECKPOINT_EDIT_EXCLUSION_PASS cycles=(\d+) safe=(\d+) edit=(\d+) busy=(\d+) '
                    r'requests=(\d+) replies=(\d+) imports=(\d+) exports=(\d+)$', stdout, re.M)
    assert len(cp) == 1
    counts = list(map(int, cp[0]))
    assert counts[0] > 0 and counts[1] > 0 and counts[3] > 0
    assert counts[2] == 1 and counts[4:] == [15, 15, 60, 90]
    return dict(host_edit_events=len(rows), clean_crc=f'{clean_crc:08x}', dirty_crc=f'{dirty_crc:08x}',
                host_requests=3, host_replies=3, host_writes=1, write_replies=1,
                cp_requests=3, cp_replies=3, import_words=20, export_words=10,
                clean_reject_checks=1, dirty_accept_checks=1, atomic_checks=atomic,
                extension_cycles=elapsed, actual_raw_cp_records=len(raw),
                original_prefix_sha256=hashlib.sha256(prefix.encode()).hexdigest(),
                final_dirty=1, final_pending=0, final_sequence=180330, final_slots=15,
                scope='Trace semantics only; full run provenance, simulator exit, complete outputs, source equality and actual restoration require the separate full-system auditor.')
