# Fly.io for Factory Droid

Deploy and operate Fly.io apps, and run development workloads in persistent
Sprites, from Factory Droid. This native plugin bundles the hosted Fly MCP
connection, the shared Fly and brand skills, and confirmation hooks.

```bash
droid plugin marketplace add superfly/fly-droid-plugin
droid plugin install fly@fly-droid-plugin --scope project
droid mcp auth
```

Start Droid in the project to complete Factory login and folder trust. Fly OAuth
is a separate browser flow. Use `--scope user` to install for all projects.
While this repository has internal visibility, GitHub access is required. Availability here
does not mean the plugin is listed in Factory's official marketplace.

See [the plugin guide](plugins/fly/README.md) for prerequisites, example prompts,
remote workspace behavior, authentication, and troubleshooting.

## Shared source and releases

The skills, references, guard, hook configuration, guard tests, logo, and license
come from [superfly/skills](https://github.com/superfly/skills).
[upstream.lock.json](upstream.lock.json) records the exact source commit and each
file's SHA-256. These files are committed here, so installing the plugin does
not fetch or execute a sync script.

This repo owns the Factory manifest, marketplace, `mcp.json`, distribution docs,
and sync tooling. Shared files are byte-identical to upstream; Droid expands
the shared hook's `CLAUDE_PLUGIN_ROOT` variable. Native Factory packaging and
shared skill versions are released independently.

To update the shared payload:

```bash
python3 scripts/sync_shared.py --ref main
python3 scripts/validate.py
python3 scripts/test_fly_guard.py
python3 -m unittest discover -s tests -v
git diff --stat
```

Use a full upstream SHA to review a specific change, or add `--source /path/to/skills`
for an existing checkout. Only committed files are read. The sync refuses to
overwrite modified generated files, removes files deleted upstream, and preserves
Factory-owned files. `--check` verifies the pinned source without writing.

CI verifies the lock and fetches its exact upstream commit to check provenance.
The weekly/manual **Sync shared skills** workflow proposes upstream-main changes
as a PR; it never merges them or publishes a release. GitHub Actions must have
permission to create pull requests for that workflow. Maintainers can run the
same sync command locally if organizational policy disables PR creation.

Before publishing a changed package, review the diff, bump the Factory plugin
version, test installation in Droid, and follow [submission guidance](SUBMISSION.md).
The initial source pin includes [skills PR #6](https://github.com/superfly/skills/pull/6);
merge it upstream and verify the pin is reachable from main before submission.

## Checks

```bash
python3 scripts/validate.py
python3 scripts/sync_shared.py --check
python3 scripts/test_fly_guard.py
python3 -m unittest discover -s tests -v
```

Python 3 and Git suffice for these checks. Live testing additionally requires
Droid model access and a Fly account with the intended OAuth grant. The package
has no local server, install scripts, or bundled credentials.

MIT licensed. [Fly.io](https://fly.io)
