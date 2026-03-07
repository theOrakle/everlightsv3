# Release Workflow Contract

This repository uses this release flow:

1. Developer works locally and says `finalize release`.
2. Codex bumps integration version in `custom_components/<domain>/manifest.json`.
3. Codex commits only intended release files (explicit paths, never `git add *`).
4. Codex creates an annotated tag matching the version (for example `1.0.11`).
5. Codex pushes `main` and the tag.
6. Developer publishes GitHub Release from that tag.

## Rules

- Keep version source of truth in `custom_components/everlights/manifest.json`.
- Use semantic version bumps (`major`, `minor`, `patch`), default `patch`.
- Do not include generated files in commits (`__pycache__/`, `*.pyc`).
- Do not amend release commits unless explicitly requested.
