# Factory marketplace submission

This repository is a native Factory marketplace and plugin distribution. It is
not yet listed in the official Factory marketplace. Preparation does not submit
or publish the plugin, and the repository currently has internal visibility.

Factory documents the contribution process in
[Factory-AI/factory-plugins](https://github.com/Factory-AI/factory-plugins#contributing):
fork, add the plugin under `plugins/`, update `.factory-plugin/marketplace.json`,
and open a PR. Maintainer acceptance is separate from technical compatibility.

## Before submitting

1. Make `superfly/fly-droid-plugin` publicly accessible, or agree on another
   source/reviewer-access arrangement with Factory. This preparation does not
   change repository visibility (currently internal). Test installation without
   privileged GitHub access before claiming public availability.
2. Run the checks in README.md and a fresh Droid installation from the release
   commit. Verify MCP OAuth and the plugin's hooks with Python 3 installed.
3. Review the dated [validation evidence](VALIDATION.md), update any stale claims,
   and commit the release version before generating a pinned catalog entry.
4. Supply reviewer access through their own Factory and Fly accounts. Do not put
   reusable credentials, user-specific Sprite IDs, or tokens in the submission.

## Prepare the contribution

Clone a clean checkout of Factory's catalog, then run:

```bash
python3 scripts/prepare_submission.py --catalog /path/to/factory-plugins
```

This follows the documented copy-in process: it copies the installable package
to `plugins/fly`, adds its catalog entry, and writes `fly-submission-body.txt`
with proposed PR text. It does not commit, push, fork, or create a PR. Use the
text file with `gh pr create --body-file`, then remove it from the contribution
working tree rather than including it in the catalog commit.

The copied catalog payload is a release snapshot. Updates to this distribution
do not automatically update Factory's copy; send a follow-up catalog PR for each
release.

Factory also documents remote `git-subdir` sources. If the maintainers prefer to
reference our maintained repository, use a separate clean catalog checkout:

```bash
python3 scripts/prepare_submission.py --catalog /path/to/factory-plugins --mode git-subdir
```

That entry pins this repo's committed `plugins/fly` directory by SHA. Public
access is required for general users. Support for the source format does not
guarantee Factory accepts that arrangement in its official catalog.

## Reviewer walkthrough

1. Install `fly@fly-droid-plugin` from this repository, or `fly@factory-plugins`
   from the proposed catalog. Enable only one Fly package in the test project.
2. Complete Factory login and Fly MCP OAuth. Run `droid mcp list`; the `fly`
   connection should be authenticated. Tool availability depends on the grant.
3. Ask "What Fly.io resources can this connection access?" Confirm a read-only
   result using `get_fly_context`, with no account or resource mutation.
4. Ask for a persistent Linux development workflow on Fly.io with checkpoints
   and a team-only preview, explicitly requesting a plan without provisioning.
   Check that Droid can load the `fly` skill and Sprite reference.
5. With explicit authorization for a disposable Sprite, run a test fixture
   remotely, export a patch with byte-count/hash verification, and resume the
   same Sprite in a fresh session. Confirm URL exposure stays authenticated.
6. Inspect `/hooks` and run the repository's synthetic guard tests. Do not use
   real destructive calls to test approval behavior.

References: [Factory plugins](https://docs.factory.com/harness/plugins),
[Factory catalog](https://github.com/Factory-AI/factory-plugins).
