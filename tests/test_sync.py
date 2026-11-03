import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from sync_shared import PATHS, git, snapshot, sync, verify, read_lock


class SyncTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.source = Path(self.tmp.name) / "source"
        self.target = Path(self.tmp.name) / "target"
        self.source.mkdir()
        self.target.mkdir()
        git(self.source, "init", "-q")
        git(self.source, "config", "user.name", "Sync Test")
        git(self.source, "config", "user.email", "sync-test@example.invalid")
        for path in PATHS[1:] + ["plugins/fly/skills/fly/SKILL.md"]:
            dest = self.source / path
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_text(f"fixture: {path}\n")
        self.commit()

    def commit(self):
        git(self.source, "add", ".")
        git(self.source, "commit", "-qm", "fixture")

    def test_pinned_snapshot_ignores_uncommitted_edits(self):
        commit = git(self.source, "rev-parse", "HEAD").decode().strip()
        (self.source / "LICENSE").write_text("uncommitted")
        sync(self.target, self.source, commit)
        self.assertEqual((self.target / "LICENSE").read_text(), "fixture: LICENSE\n")
        self.assertEqual((self.target / "plugins/fly/LICENSE").read_bytes(), (self.target / "LICENSE").read_bytes())
        self.assertEqual(sync(self.target, self.source, commit, check=True), commit)

    def test_update_refuses_local_changes(self):
        sync(self.target, self.source, "HEAD")
        (self.target / "LICENSE").write_text("local edit")
        with self.assertRaisesRegex(ValueError, "differs"):
            sync(self.target, self.source, "HEAD")
        self.assertEqual((self.target / "LICENSE").read_text(), "local edit")

    def test_deleted_shared_file_removed_but_native_files_preserved(self):
        extra = self.source / "plugins/fly/skills/fly/obsolete.md"
        extra.write_text("obsolete")
        self.commit()
        sync(self.target, self.source, "HEAD")
        native = self.target / "plugins/fly/mcp.json"
        native.write_text("native config")
        extra.unlink()
        self.commit()
        sync(self.target, self.source, "HEAD")
        self.assertFalse((self.target / "plugins/fly/skills/fly/obsolete.md").exists())
        self.assertEqual(native.read_text(), "native config")

    def test_upstream_symlink_rejected(self):
        path = self.source / "plugins/fly/skills/fly/link"
        path.symlink_to("../../../../LICENSE")
        self.commit()
        with self.assertRaisesRegex(ValueError, "Unsupported"):
            snapshot(self.source, "HEAD")

    def test_target_symlink_rejected_without_writing_outside_package(self):
        outside = Path(self.tmp.name) / "outside"
        outside.mkdir()
        (self.target / "plugins").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            sync(self.target, self.source, "HEAD")
        self.assertEqual(list(outside.iterdir()), [])
        self.assertFalse((self.target / "LICENSE").exists())

    def test_added_upstream_file_does_not_overwrite_unmanaged_file(self):
        sync(self.target, self.source, "HEAD")
        name = "plugins/fly/skills/fly/new.md"
        (self.target / name).write_text("local")
        (self.source / name).write_text("upstream")
        self.commit()
        with self.assertRaisesRegex(ValueError, "Untracked"):
            sync(self.target, self.source, "HEAD")
        self.assertEqual((self.target / name).read_text(), "local")

    def test_lock_cannot_delete_outside_managed_paths(self):
        sync(self.target, self.source, "HEAD")
        lock = read_lock(self.target)
        lock["files"]["../outside"] = {"sha256": "bad"}
        with self.assertRaisesRegex(ValueError, "Unsafe"):
            verify(self.target, lock)


if __name__ == "__main__":
    unittest.main()
