#!/usr/bin/env python3
"""Validate the installable native package and its locked shared payload."""

import json
from pathlib import Path
import re

from sync_shared import ROOT, read_lock, verify


def validate(root=ROOT):
    verify(root, read_lock(root))
    plugin = root / "plugins/fly"
    manifest = json.loads((plugin / ".factory-plugin/plugin.json").read_text())
    if manifest["name"] != "fly" or not re.fullmatch(r"\d+\.\d+\.\d+", manifest["version"]):
        raise ValueError("Invalid plugin identity/version")
    catalog = json.loads((root / ".factory-plugin/marketplace.json").read_text())
    if catalog["name"] != "fly-droid-plugin" or len(catalog["plugins"]) != 1:
        raise ValueError("Unexpected marketplace identity")
    entry = catalog["plugins"][0]
    if entry["name"] != "fly" or entry["source"] != "./plugins/fly":
        raise ValueError("Marketplace must install the native Fly package")
    mcp = json.loads((plugin / "mcp.json").read_text())
    if mcp != {"mcpServers": {"fly": {"type": "http", "url": "https://mcp.fly.io"}}}:
        raise ValueError("MCP must use the hosted OAuth endpoint without embedded credentials")
    for path in plugin.rglob("*"):
        if path.is_symlink():
            raise ValueError(f"Plugin contains symlink: {path}")
    for name in ("fly", "brand"):
        skill = plugin / "skills" / name / "SKILL.md"
        text = skill.read_text()
        if not text.startswith("---\n") or f"name: {name}\n" not in text:
            raise ValueError(f"Invalid skill frontmatter: {skill}")
        if len(text.splitlines()) > 500:
            raise ValueError(f"Skill exceeds 500 lines: {skill}")
    for path in (plugin / "skills").rglob("*.md"):
        for target in re.findall(r"\]\(([^)]+)\)", path.read_text()):
            if "://" in target or target.startswith("#"):
                continue
            target = target.split("#", 1)[0]
            if target and not (path.parent / target).exists():
                raise ValueError(f"Broken reference in {path}: {target}")
    hooks = json.loads((plugin / "hooks/hooks.json").read_text())
    for entry in hooks["hooks"]["PreToolUse"]:
        re.compile(entry["matcher"])
        for hook in entry["hooks"]:
            if "scripts/fly_guard.py" not in hook["command"]:
                raise ValueError("Unexpected hook command")
    for required in ("README.md", "LICENSE", "assets/logo.svg"):
        if not (plugin / required).is_file():
            raise ValueError(f"Plugin missing {required}")


if __name__ == "__main__":
    validate()
    print("Native Factory plugin, shared payload, and references validated")
