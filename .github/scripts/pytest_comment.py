"""Generate a markdown summary of pytest results for PR comments."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import os
import xml.etree.ElementTree as ET


STATUS_ORDER = ("failed", "error", "skipped", "passed")


def short_reason(text: str | None, limit: int = 120) -> str:
    """Trim multiline failure text to a short, single-line summary."""

    if not text:
        return ""
    line = text.strip().splitlines()[0]
    return line if len(line) <= limit else f"{line[: limit - 3]}..."


def group_name(classname: str) -> str:
    """Build a readable group name based on the pytest classname."""

    if not classname:
        return "Module-level tests (unknown)"
    parts = classname.split(".")
    if len(parts) > 1 and parts[-1].startswith("Test"):
        module = ".".join(parts[:-1])
        return f"{parts[-1]} ({module})"
    return f"Module-level tests ({classname})"


def parse_junit(path: str) -> list[dict[str, str]]:
    """Parse pytest JUnit XML into a list of case dictionaries."""

    tree = ET.parse(path)
    root = tree.getroot()
    cases: list[dict[str, str]] = []
    for case in root.iter("testcase"):
        classname = case.attrib.get("classname", "")
        name = case.attrib.get("name", "")
        status = "passed"
        reason = ""
        failure = case.find("failure")
        error = case.find("error")
        skipped = case.find("skipped")
        if failure is not None:
            status = "failed"
            reason = short_reason(failure.text)
        elif error is not None:
            status = "error"
            reason = short_reason(error.text)
        elif skipped is not None:
            status = "skipped"
            reason = short_reason(skipped.text)
        cases.append(
            {
                "classname": classname,
                "name": name,
                "status": status,
                "reason": reason,
            }
        )
    return cases


def render_comment(
    cases: list[dict[str, str]],
    run_url: str,
    error_note: str | None = None,
) -> str:
    """Render the markdown comment body."""

    counts = Counter(case["status"] for case in cases)
    status = "PASSED"
    if counts.get("failed") or counts.get("error"):
        status = "FAILED"
    elif not cases:
        status = "NO TESTS"

    lines: list[str] = ["<!-- pr-tests -->", "## PR Test Results"]
    lines.append(f"Status: {status}")
    lines.append(f"Run: {run_url}")
    totals = ", ".join(f"{counts.get(key, 0)} {key}" for key in STATUS_ORDER)
    lines.append(f"Totals: {totals}")
    if error_note:
        lines.append("")
        lines.append(f"Note: {error_note}")
    lines.append("")

    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for case in cases:
        grouped[group_name(case["classname"])].append(case)

    for group in sorted(grouped):
        group_counts = Counter(item["status"] for item in grouped[group])
        summary_counts = ", ".join(
            f"{group_counts.get(key, 0)} {key}" for key in STATUS_ORDER
        )
        lines.append("<details>")
        lines.append(f"<summary>{group} ({summary_counts})</summary>")
        lines.append("")
        for case in sorted(grouped[group], key=lambda item: item["name"]):
            reason = case["reason"]
            suffix = f" - {reason}" if reason else ""
            lines.append(f"- `{case['name']}` - {case['status'].upper()}{suffix}")
        lines.append("")
        lines.append("</details>")

    return "\n".join(lines).strip() + "\n"


def main() -> int:
    """CLI entry point for comment generation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", required=True, help="Path to JUnit XML file.")
    parser.add_argument("--output", required=True, help="Output markdown file.")
    parser.add_argument("--run-url", required=True, help="URL to the workflow run.")
    args = parser.parse_args()

    if not os.path.exists(args.junit):
        note = "JUnit report not found; tests may have failed to collect."
        comment = render_comment([], args.run_url, error_note=note)
    else:
        cases = parse_junit(args.junit)
        comment = render_comment(cases, args.run_url)

    args.output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(comment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
