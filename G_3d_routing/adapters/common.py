"""Local provenance helpers; never write into the referenced source project."""
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def sha256(path):
    result = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            result.update(chunk)
    return result.hexdigest()


def read_json(path):
    return json.loads(Path(path).read_text())


def write_new(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x") as stream:
        json.dump(value, stream, indent=2, ensure_ascii=False, allow_nan=False)
        stream.write("\n")


def verified_file(record):
    path = Path(record["path"])
    if not path.is_absolute():
        path = ROOT / path
    if sha256(path) != record["sha256"]:
        raise ValueError(f"Pinned input changed: {path}")
    return path.resolve()
