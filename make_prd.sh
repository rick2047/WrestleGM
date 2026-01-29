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

extract_config_context() {
  local config_file="$1"
  uv run python - <<'PY' "$config_file"
import sys
import yaml

path = sys.argv[1]
try:
    with open(path, "r", encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    context = config.get("context", "")
    if context:
        sys.stdout.write(context.rstrip() + "\n")
except (OSError, yaml.YAMLError) as exc:
    print(f"Error processing {path}: {exc}", file=sys.stderr)
    sys.exit(1)
PY
}

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
    if [[ "$f" == "openspec/config.yaml" ]]; then
      extract_config_context "$f"
    else
      cat "$f"
    fi
  } >> "$OUT"
done

echo "Done → $OUT"
