#!/usr/bin/env python3
"""Vendor exact, reviewed upstream files; never execute upstream code during sync."""

import argparse
from contextlib import contextmanager
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parents[1]
UPSTREAM = "https://github.com/superfly/skills.git"
LOCK = "upstream.lock.json"
PATHS = [
    "plugins/fly/skills",
    "plugins/fly/scripts/fly_guard.py",
    "plugins/fly/hooks/hooks.json",
    "plugins/fly/assets/logo.svg",
    "scripts/test_fly_guard.py",
    "LICENSE",
]


def git(repo, *args):
    return subprocess.check_output(["git", "-C", str(repo), *args])


def managed(path):
    p = PurePosixPath(path)
    return not p.is_absolute() and ".." not in p.parts and (
        path in PATHS or path.startswith("plugins/fly/skills/")
        or path == "plugins/fly/LICENSE"
    )


def digest(data):
    return hashlib.sha256(data).hexdigest()


def symlink_in_package(root, path):
    # macOS /tmp and /var themselves are symlinks; only package-owned paths
    # must not redirect writes outside the selected repository root.
    parts = path.relative_to(root).parts
    return any(root.joinpath(*parts[:i]).is_symlink() for i in range(1, len(parts) + 1))


def read_lock(root):
    path = root / LOCK
    return json.loads(path.read_text()) if path.exists() else None


def verify(root, lock):
    if not lock or lock.get("repository") != UPSTREAM:
        raise ValueError("Missing or invalid upstream lock")
    if not re.fullmatch(r"[0-9a-f]{40}", lock.get("commit", "")):
        raise ValueError("Upstream lock must pin a full commit SHA")
    if not lock.get("files"):
        raise ValueError("Upstream lock contains no files")
    for name, metadata in lock["files"].items():
        if not managed(name):
            raise ValueError(f"Unsafe generated path: {name}")
        path = root / name
        if symlink_in_package(root, path):
            raise ValueError(f"Generated path is a symlink: {name}")
        if not path.is_file() or digest(path.read_bytes()) != metadata["sha256"]:
            raise ValueError(f"Generated file differs from the lock: {name}")
    skill_root = root / "plugins/fly/skills"
    for path in skill_root.rglob("*"):
        if path.is_file() and path.relative_to(root).as_posix() not in lock["files"]:
            raise ValueError(f"Untracked shared skill file: {path.relative_to(root)}")


def snapshot(repo, ref):
    commit = git(repo, "rev-parse", "--verify", f"{ref}^{{commit}}").decode().strip()
    entries = git(repo, "ls-tree", "-rz", commit, "--", *PATHS).split(b"\0")
    files = {}
    for entry in filter(None, entries):
        header, raw_path = entry.split(b"\t", 1)
        mode, kind, blob = header.split()
        path = raw_path.decode()
        if mode not in (b"100644", b"100755") or kind != b"blob" or not managed(path):
            raise ValueError(f"Unsupported upstream file: {path}")
        data = git(repo, "cat-file", "blob", blob.decode())
        files[path] = (path, data)
    for required in PATHS[1:] + ["plugins/fly/skills/fly/SKILL.md"]:
        if required not in files:
            raise ValueError(f"Upstream file missing: {required}")
    files["plugins/fly/LICENSE"] = files["LICENSE"]
    return commit, files


def sync(root, repo, ref, check=False):
    previous = read_lock(root)
    if previous:
        # Refuse to erase somebody's local edits when updating the source pin.
        verify(root, previous)
    commit, files = snapshot(repo, ref)
    lock = {
        "schemaVersion": 1,
        "repository": UPSTREAM,
        "commit": commit,
        "transform": "Byte-identical shared files; copy MIT license into plugin",
        "files": {
            name: {"source": source, "sha256": digest(data)}
            for name, (source, data) in sorted(files.items())
        },
    }
    if check:
        if previous != lock:
            raise ValueError("Payload or upstream pin differs; run sync_shared.py and review changes")
        return commit
    for name in files:
        path = root / name
        if symlink_in_package(root, path):
            raise ValueError(f"Refusing to write through symlink: {name}")
        if name not in (previous or {}).get("files", {}) and path.exists():
            raise ValueError(f"Refusing to overwrite unmanaged file: {name}")
    for name in (previous or {}).get("files", {}):
        if name not in files:
            (root / name).unlink()
    for name, (_source, data) in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    (root / LOCK).write_text(json.dumps(lock, indent=2) + "\n")
    return commit


@contextmanager
def source(path, ref):
    if path:
        yield Path(path), ref
    else:
        with tempfile.TemporaryDirectory(prefix="fly-skills-sync-") as directory:
            subprocess.run(["git", "init", "-q", directory], check=True)
            subprocess.run(["git", "-C", directory, "fetch", "-q", "--depth=1", UPSTREAM, ref], check=True)
            yield Path(directory), "FETCH_HEAD"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", help="Existing local upstream git checkout (reads committed files only)")
    parser.add_argument("--ref", help="Upstream branch, tag, or SHA; defaults to the locked commit")
    parser.add_argument("--check", action="store_true", help="Compare with upstream without writing")
    args = parser.parse_args()
    ref = args.ref or (read_lock(ROOT) or {}).get("commit")
    if not ref or ref.startswith("-"):
        parser.error("Provide --ref on the first sync; refs cannot start with '-' ")
    try:
        with source(args.source, ref) as (repo, resolved):
            commit = sync(ROOT, repo, resolved, args.check)
    except (ValueError, subprocess.CalledProcessError) as error:
        parser.exit(1, f"Sync failed: {error}\n")
    print(f"{'Verified' if args.check else 'Synced'} superfly/skills@{commit}")


if __name__ == "__main__":
    main()
