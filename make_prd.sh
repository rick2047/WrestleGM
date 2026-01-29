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

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as handle:
    lines = handle.readlines()

context_line_idx = None
context_indent = None
for idx, line in enumerate(lines):
    stripped = line.lstrip()
    if stripped.startswith("context:") and "|" in stripped:
        context_line_idx = idx
        context_indent = len(line) - len(stripped)
        break

if context_line_idx is None:
    sys.exit(0)

content_lines = []
block_indent = None
for line in lines[context_line_idx + 1 :]:
    if not line.strip():
        content_lines.append("\n")
        continue
    indent = len(line) - len(line.lstrip())
    if block_indent is None:
        if indent <= context_indent:
            break
        block_indent = indent
    if indent <= context_indent:
        break
    content_lines.append(line[block_indent:])

sys.stdout.write("".join(content_lines).rstrip() + "\n")
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
