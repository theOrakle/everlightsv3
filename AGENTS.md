# Release Workflow Contract

This repository uses this release flow:

1. Developer works locally and says `finalize release`.
2. Codex bumps integration version in `custom_components/<domain>/manifest.json`.
3. Codex commits only intended release files (explicit paths, never `git add *`).
4. Codex creates an annotated tag matching the version (for example `1.0.11`).
5. Codex pushes `main` and the tag.
6. Developer publishes GitHub Release from that tag.

## Trigger Phrases

- `finalize release` -> patch release
- `finalize patch release` -> patch release
- `finalize minor release` -> minor release
- `finalize major release` -> major release

## Script Commands

- Create release commit + tag + push: `./scripts/release.sh [patch|minor|major] ["commit message"]`
- Push already-created release/tag: `./scripts/push-release.sh [tag]`
- Generate copy/paste release notes: `./scripts/release-notes.sh [tag]`

## Rules

- Keep version source of truth in `custom_components/everlights/manifest.json`.
- Use semantic version bumps (`major`, `minor`, `patch`), default `patch`.
- Do not include generated files in commits (`__pycache__/`, `*.pyc`).
- Do not amend release commits unless explicitly requested.

## Release Notes Template

Use this for GitHub Release notes:

```md
## Everlights v3 <VERSION>

### What Changed
- Reliability hardening for bridge/API communication.
- Group light behavior improvements across multi-zone setups.
- Minor integration polish and documentation updates.

### Fixes Included
- <short bullet 1>
- <short bullet 2>
- <short bullet 3>

### Notes
- Home Assistant restart recommended after update.
- If using HACS, upgrade then reload/restart Home Assistant.
```
