#!/usr/bin/env bash
set -eo pipefail

OUT="prd.md"

FILES=(
  "openspec/config.yaml"
  "openspec/specs/data/spec.md"
  "openspec/specs/game-loop/spec.md"
  "openspec/specs/rivalry/spec.md"
  "openspec/specs/simulation/spec.md"
  "openspec/specs/persistence/spec.md"
  "openspec/specs/ui/spec.md"
  "openspec/specs/ui-testing/spec.md"
  "openspec/specs/documentation/spec.md"
  "openspec/specs/ci/spec.md"
)

> "$OUT"

for f in "${FILES[@]}"; do
  if [[ ! -f "$f" ]]; then
    echo "ERROR: missing file: $f" >&2
    exit 1
  fi

  {
    echo
    echo "---"
    echo "# FILE: $f"
    echo "---"
    echo
    cat "$f"
  } >> "$OUT"
done

echo "Done → $OUT"
