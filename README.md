# Fly.io for Factory Droid

Deploy and operate Fly.io apps, and run development workloads in persistent
Sprites, from Factory Droid. This native plugin bundles the hosted Fly MCP
connection, the Fly and brand skills, and confirmation hooks.

```bash
droid plugin marketplace add superfly/fly-droid-plugin
droid plugin install fly@fly-droid-plugin --scope project
droid mcp auth
```

Start Droid in the project to complete Factory login and folder trust. Fly OAuth
is a separate browser flow. Use `--scope user` to install for all projects.
This repository is public. Availability here does not mean the plugin is listed
in Factory's official marketplace.

See [the plugin guide](plugins/fly/README.md) for prerequisites, example prompts,
remote workspace behavior, authentication, and troubleshooting.

## Checks

```bash
python3 scripts/validate.py
python3 scripts/test_fly_guard.py
```

Python 3 suffices for these checks. Live testing additionally requires
Droid model access and a Fly account with the intended OAuth grant. The package
has no local server, install scripts, or bundled credentials.

See [submission guidance](SUBMISSION.md) for the marketplace contribution process.

MIT licensed. [Fly.io](https://fly.io)
