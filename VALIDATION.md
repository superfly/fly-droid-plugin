# Validation evidence

Checked on 2026-11-03 on macOS. This records observations, not a guarantee of
future runtime behavior or marketplace acceptance. No production service was
deployed and no new Sprite was created for validation.

## Repository checks

- Native manifest, marketplace, hosted OAuth MCP configuration, required files,
  and skill references validated.
- All 18 confirmation-guard tests passed.
- The GitHub Actions validation workflow passed actionlint.

## Native package in Droid

- After the repository became public, cloned commit
  `bef866383ddde9825202b70e2cbf48d1bdba235e` with Git credential helpers and
  authentication headers disabled. Package validation and all 18 hook tests
  passed from that clean clone. Droid 1.2.0 then installed the same public Git
  commit in a fresh project and connected to all 75 Fly MCP tools using the
  existing Fly OAuth session.
- Installed `fly@fly-droid-plugin` in a fresh project from a local marketplace.
  Its native `.factory-plugin/plugin.json` and `mcp.json` loaded successfully;
  cached skills and hooks matched the package files.
- Separately installed the pushed Git commit
  `20c231b58602a8a0bbfdf3ec97395c103dbf1068` in another fresh project.
  All 25 cached package files matched the repository, and the connection again
  authenticated with 75 tools. This used existing authorized GitHub access to
  the internal repository; it is not evidence of anonymous/public installation.
- `droid mcp list` reported the Fly server authenticated with 75 tools using
  protocol 2025-11-25. Factory and Fly logins already existed; first-time
  account signup and OAuth consent were not repeated.
- The `/hooks` Plugins tab showed both PreToolUse matchers, with the
  plugin-root variable expanded to the native package's cache path.
- A fresh, ordinary remote-development planning request invoked `Skill("fly")`
  and read the bundled Sprite references. A specific operational request went
  directly to the MCP tools. Skill selection is model-dependent, not universal.
- The active model was the account's configured `claude-opus-5-5` custom model;
  no model override or multi-agent mode was used.
- Droid reported 1.1.0 at the beginning of testing and automatically staged
  1.2.0 during the interactive session. Later CLI invocations reported 1.2.0.

## Live Sprite workflow

The native plugin resumed an existing authorized test Sprite by name and ID,
inspected its repository and checkpoints, and ran three Python unit tests
remotely. All three passed with an explicit exit code of zero. The preview
returned HTTP 200 inside the Sprite; unauthenticated requests to its service
URL redirected to sign-in, consistent with `authenticated` exposure.

Droid exported the existing remote Git diff as a 409-byte local patch. Its
SHA-256 matched the remote diff and the previously verified fixture patch.
The framing workaround was still needed. The session briefly created and
removed a temporary patch file inside the Sprite; source, service definitions,
exposure, and checkpoints remained unchanged. No destructive approval flow was
tested against real resources; the guard uses synthetic fixtures instead.

The runtime notes describe remaining file-read, ownership, and service
adapter limitations. Package installation does not deploy fixes to those APIs.

## Catalog contribution

Prepared the documented copy-in catalog contribution locally and verified all
25 copied package files against the distribution. Public source access and
installation are verified above. Catalog acceptance remains subject to
Factory's review.
