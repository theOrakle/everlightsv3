#!/usr/bin/env bash
set -euo pipefail

MANIFEST="custom_components/everlights/manifest.json"

if [[ ! -f "$MANIFEST" ]]; then
  echo "Missing $MANIFEST"
  exit 1
fi

TAG="${1:-$(jq -r '.version' "$MANIFEST")}"

if [[ -z "$TAG" || "$TAG" == "null" ]]; then
  echo "Could not determine release tag"
  exit 1
fi

if ! git rev-parse --verify --quiet "refs/tags/$TAG" >/dev/null; then
  echo "Tag '$TAG' does not exist locally."
  echo "Create it first or pass a valid tag: $0 <tag>"
  exit 1
fi

git push origin main
git push origin "$TAG"

echo "Pushed main and tag $TAG"
