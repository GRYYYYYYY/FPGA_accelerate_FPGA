"""Public-command oracle: mapping, publication and leases, independent of hashing."""
from pathlib import Path
import hashlib
import json
import random
import sys

ROOT = Path(__file__).resolve().parents[2]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Directory:
    def __init__(self, capacity):
        self.capacity = capacity
        self.owners = []
        self.mapping = {}
        self.published = []
        self.leases = [None] * 4
        self.last_tx = -1
        self.rows = []

    def request(self, op, owner=0, frame=0, cookie=0, success=1, fence=0):
        status = result = published = 0
        slot = cookie & 3
        c_owner = (cookie >> 2) & 0xffffff
        transaction = (cookie >> 42) & 65535
        refill = (cookie >> 58) & 1
        lease = self.leases[slot]
        match = lease is not None and lease[:2] == (cookie, frame)
        if op in (0, 5):
            if owner in self.mapping:
                result = self.mapping[owner]
                published = self.published[result]
            elif op == 5:
                status = 6
            elif len(self.owners) == self.capacity:
                status = 4
            else:
                result = len(self.owners)
                self.mapping[owner] = result
                self.owners.append(owner)
                self.published.append(0)
        elif op == 1:
            if cookie >> 59:
                status = 3
            elif frame >= len(self.owners):
                status = 1
            elif lease is not None or any(x is not None and x[1] == frame for x in self.leases):
                status = 2
            elif transaction <= self.last_tx:
                status = 5
            elif self.owners[frame] != c_owner:
                status = 1
            elif refill and not self.published[frame]:
                status = 6
            else:
                self.leases[slot] = (cookie, frame, 'inflight')
                self.last_tx = transaction
                if not refill:
                    self.published[frame] = 0
                result, published = frame, refill
        elif op == 2:
            if not match or lease[2] != 'inflight':
                status = 1
            else:
                self.leases[slot] = (cookie, frame, 'complete' if success else 'failed')
                if not success:
                    status = 7
                else:
                    result, published = frame, 1
                    if not refill:
                        self.published[frame] = 1
        elif op == 3:
            if not match:
                status = 1
            elif lease[2] != 'complete':
                status = 6
            else:
                self.leases[slot] = None
                result, published = frame, 1
        elif op == 4:
            if any(self.leases) or not fence:
                status = 2
            else:
                self.owners.clear(); self.mapping.clear(); self.published.clear()
                self.last_tx = -1
        else:
            status = 3
        leased = sum(1 << i for i, value in enumerate(self.leases) if value is not None)
        fault = int(any(x is not None and x[2] == 'failed' for x in self.leases))
        self.rows.append((op, owner, frame, cookie, success, fence,
                          status, result, published, len(self.owners), leased, fault))


def cookie(owner, tx, slot=0, refill=0, generation=1):
    return slot | (owner << 2) | (generation << 26) | (tx << 42) | (refill << 58)


def mixed(value):
    value ^= value >> 16
    value = value * 0x85ebca6b & 0xffffffff
    value ^= value >> 13
    value = value * 0xc2b2ae35 & 0xffffffff
    return value ^ (value >> 16)


def write(path, rows):
    path.write_text(''.join(' '.join(f'{x:x}' for x in row) + '\n' for row in rows))


def main():
    out = Path(sys.argv[1]).resolve()
    out.mkdir()
    rng = random.Random(20261023)
    small = Directory(16)
    collisions = [page | 0x100000 for page in range(10000) if mixed(page | 0x100000) & 15 == 0][:12]
    old = []
    for epoch in range(10):
        small.request(5, owner=0xeeeeee)
        for owner in old:
            small.request(5, owner=owner)
        # Two same-bucket insertions fill the probe budget; remaining owners
        # become unindexed. A later empty bucket must still scan the overflow.
        keys = [x ^ (epoch << 20) for x in collisions]
        # The first epoch guarantees collisions; later epochs vary owner/price.
        keys += [keys[0] ^ (tag << 18) for tag in range(1, 4)] + [keys[0] ^ 0x800000]
        for owner in keys:
            small.request(0, owner=owner)
        small.request(0, owner=0xfffffe)
        for _ in range(60):
            small.request(rng.choice([0, 5]), owner=rng.choice(keys + [0xfffffe]))
        for frame in range(4):
            owner = keys[frame]
            token = cookie(owner, frame + 1, frame)
            small.request(1, frame=frame, cookie=token | (1 << 59))
            small.request(1, frame=frame, cookie=cookie(owner, frame + 1, frame, refill=1))
            small.request(1, frame=frame, cookie=token)
            small.request(1, frame=frame, cookie=cookie(owner, 20, (frame + 1) % 4))
            small.request(3, frame=frame, cookie=token)
            small.request(4, fence=1)
            small.request(2, frame=frame, cookie=token ^ (1 << 26))
            small.request(2, frame=frame, cookie=token)
            small.request(5, owner=owner)
        for frame in reversed(range(4)):
            small.request(3, frame=frame, cookie=cookie(keys[frame], frame + 1, frame))
        small.request(1, frame=0, cookie=cookie(keys[0], 4))
        small.request(1, frame=0, cookie=cookie(keys[0] ^ 1, 5))
        small.request(1, frame=0, cookie=cookie(keys[0], 5, refill=1))
        small.request(2, frame=0, cookie=cookie(keys[0], 5, refill=1))
        small.request(3, frame=0, cookie=cookie(keys[0], 5, refill=1))
        small.request(1, frame=0, cookie=cookie(keys[0], 6))
        small.request(5, owner=keys[0])  # publication revoked during WB
        small.request(2, frame=0, cookie=cookie(keys[0], 6))
        small.request(3, frame=0, cookie=cookie(keys[0], 6))
        small.request(4, fence=0)
        small.request(6)
        small.request(7)
        small.request(4, fence=1)
        old = keys
    small.request(0, owner=17)
    small.request(1, cookie=cookie(17, 1))
    small.request(2, cookie=cookie(17, 1), success=0)
    small.request(3, cookie=cookie(17, 1))
    small.request(4, fence=1)
    small.request(5, owner=17)
    write(out / 'small.txt', small.rows)

    parent = ROOT / 'results/directory_keysets_20261023'
    manifest = json.loads((parent / 'manifest.json').read_text())
    audit = json.loads((parent / 'completion_audit.json').read_text())
    assert sha(parent / 'manifest.json') == audit['manifest_sha256']
    assert sha(parent / 'keysets.jsonl') == manifest['artifacts']['keysets.jsonl']
    sets = [json.loads(line) for line in (parent / 'keysets.jsonl').read_text().splitlines()]
    largest = max(sets, key=lambda x: len(x['dirty_pages_first_write_order']))
    bound = json.loads((parent / 'probe_bound_control.json').read_text())
    bound_audit = json.loads((parent / 'probe_bound_control_audit.json').read_text())
    assert sha(parent / 'probe_bound_control.json') == bound_audit['control_sha256']
    # Read the explicitly recorded adversarial keys; no new sampling.
    keys_control = bound['keys']
    large = Directory(23405)
    keys_real = [(largest['iteration'] & 15) << 20 | page for page in largest['dirty_pages_first_write_order']]
    for keys in [keys_real, keys_control]:
        for owner in keys:
            large.request(0, owner=owner)
        for owner in reversed(keys):
            large.request(5, owner=owner)
            large.request(0, owner=owner)
        large.request(5, owner=0xffffff)
        large.request(4, fence=1)
        for owner in keys[:16]:
            large.request(5, owner=owner)
    write(out / 'large.txt', large.rows)
    info = {'status': 'generated', 'small_commands': len(small.rows), 'large_commands': len(large.rows),
            'largest_attempt': largest['attempt'], 'real_keys': len(keys_real), 'adversarial_keys': len(keys_control),
            'seed': 20261023, 'scope': 'Standalone directory command oracle; not full field/transport replay.',
            'inputs': {str(parent / name): sha(parent / name) for name in
                       ['manifest.json', 'keysets.jsonl', 'probe_bound_control.json']},
            'source': {str(Path(__file__).resolve()): sha(Path(__file__).resolve())},
            'artifacts': {name: sha(out / name) for name in ['small.txt', 'large.txt']}}
    (out / 'manifest.json').write_text(json.dumps(info, indent=2) + '\n')
    print(json.dumps(info, indent=2))


if __name__ == '__main__':
    main()
