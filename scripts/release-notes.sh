#!/usr/bin/env bash
set -euo pipefail

MANIFEST="custom_components/everlights/manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing $MANIFEST" >&2
  exit 1
fi

TAG="${1:-$(jq -r '.version' "$MANIFEST")}"

if ! git rev-parse --verify --quiet "refs/tags/$TAG" >/dev/null; then
  echo "Tag '$TAG' does not exist locally." >&2
  echo "Usage: $0 [tag]" >&2
  exit 1
fi

PREV_TAG="$(git tag --list | sort -V | awk -v t="$TAG" '$0==t{print p; exit}{p=$0}')"

if [[ -n "$PREV_TAG" ]]; then
  RANGE="${PREV_TAG}..${TAG}"
else
  RANGE="$TAG"
fi

COMMITS="$(git log --pretty='- %s' "$RANGE" | grep -Ev '^- Release [0-9]+\.[0-9]+\.[0-9]+$' || true)"

echo "## Everlights v3 ${TAG}"
echo
echo "### What Changed"
echo "- Reliability hardening for bridge/API communication."
echo "- Group light behavior improvements across multi-zone setups."
echo "- Minor integration polish and documentation updates."
echo
echo "### Fixes Included"
if [[ -n "$COMMITS" ]]; then
  echo "$COMMITS"
else
  echo "- Maintenance and release workflow updates."
fi
echo
echo "### Notes"
echo "- Home Assistant restart recommended after update."
echo "- If using HACS, upgrade then reload/restart Home Assistant."
