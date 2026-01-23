"""Generate a markdown summary of UI snapshots for PR comments."""

from __future__ import annotations

import argparse
from collections import Counter
import os
import xml.etree.ElementTree as ET


STATUS_EMOJI = {
    "failed": "❌",
    "error": "🛑",
    "skipped": "⚠️",
    "passed": "✅",
}

SNAPSHOT_ENTRIES = [
    ("S1 Main Menu (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s1_main_menu_default.raw"),
    ("S2 Game Hub (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s2_game_hub_default.raw"),
    ("S3 Booking Hub (all slots empty)", "tests/snapshots/test_ui_snapshots/test_snapshot_s3_booking_hub_empty.raw"),
    ("S4 Booking Hub (all slots filled)", "tests/snapshots/test_ui_snapshots/test_snapshot_s4_booking_hub_filled.raw"),
    ("S5 Match Booking (empty slot)", "tests/snapshots/test_ui_snapshots/test_snapshot_s5_match_booking_empty.raw"),
    ("S6 Match Booking (filled slot)", "tests/snapshots/test_ui_snapshots/test_snapshot_s6_match_booking_filled.raw"),
    ("S7 Wrestler Selection (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s7_wrestler_selection_default.raw"),
    ("S8 Match Category Selection (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s8_match_category_selection_default.raw"),
    ("S9 Match Booking Confirmation (modal visible)", "tests/snapshots/test_ui_snapshots/test_snapshot_s9_match_booking_confirmation_modal.raw"),
    ("S10 Show Results (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s10_show_results_default.raw"),
    ("S11 Roster Overview (default)", "tests/snapshots/test_ui_snapshots/test_snapshot_s11_roster_overview_default.raw"),
    ("S12 Booking Hub (rivalry emojis)", "tests/snapshots/test_ui_snapshots/test_snapshot_s12_booking_hub_rivalry_emojis.raw"),
    ("S13 Booking Hub (cooldown emojis)", "tests/snapshots/test_ui_snapshots/test_snapshot_s13_booking_hub_cooldown_emojis.raw"),
    ("S14 Match Booking (rivalry emojis)", "tests/snapshots/test_ui_snapshots/test_snapshot_s14_match_booking_rivalry_emojis.raw"),
    ("S15 Save Slot Selection (empty)", "tests/snapshots/test_ui_snapshots/test_snapshot_s15_save_slot_selection_empty.raw"),
    ("S16 Save Slot Selection (mixed)", "tests/snapshots/test_ui_snapshots/test_snapshot_s16_save_slot_selection_mixed.raw"),
    ("S17 Name Save Slot Modal", "tests/snapshots/test_ui_snapshots/test_snapshot_s17_name_save_slot_modal.raw"),
    ("S18 Overwrite Save Slot Modal", "tests/snapshots/test_ui_snapshots/test_snapshot_s18_overwrite_save_slot_modal.raw"),
]


def short_reason(text: str | None, limit: int = 160) -> str:
    """Trim multiline failure text to a short, single-line summary."""

    if not text:
        return ""
    line = text.strip().splitlines()[0]
    return line if len(line) <= limit else f"{line[: limit - 3]}..."


def parse_junit(path: str) -> list[dict[str, str]]:
    """Parse pytest JUnit XML into a list of case dictionaries."""

    tree = ET.parse(path)
    root = tree.getroot()
    cases: list[dict[str, str]] = []
    for case in root.iter("testcase"):
        name = case.attrib.get("name", "")
        status = "passed"
        reason = ""
        for status_name, tag in (
            ("failed", "failure"),
            ("error", "error"),
            ("skipped", "skipped"),
        ):
            node = case.find(tag)
            if node is not None:
                status = status_name
                reason = short_reason(node.text)
                break
        cases.append({"name": name, "status": status, "reason": reason})
    return cases


def render_snapshot_table(base_url: str) -> str:
    """Render the snapshot table with collapsed images."""

    lines = []
    lines.append("<details>")
    lines.append("<summary>UI Snapshots (latest)</summary>")
    lines.append("")
    lines.append("| Snapshot | Image |")
    lines.append("| --- | --- |")
    for label, path in SNAPSHOT_ENTRIES:
        if os.path.exists(path):
            url = f"{base_url}/{path}"
            image_cell = (
                "<details><summary>View</summary>"
                f"<img src=\"{url}\" width=\"600\" /></details>"
            )
        else:
            image_cell = "Missing"
        lines.append(f"| {label} | {image_cell} |")
    lines.append("")
    lines.append("</details>")
    return "\n".join(lines)


def render_comment(
    cases: list[dict[str, str]],
    run_url: str,
    base_url: str,
    error_note: str | None = None,
) -> str:
    """Render the markdown comment body."""

    counts = Counter(case["status"] for case in cases)
    status = "PASSED"
    if counts.get("failed") or counts.get("error"):
        status = "FAILED"
    elif not cases:
        status = "NO TESTS"

    if status == "PASSED":
        status_emoji = STATUS_EMOJI["passed"]
    elif status == "FAILED":
        status_emoji = STATUS_EMOJI["failed"]
    else:
        status_emoji = STATUS_EMOJI["skipped"]
    lines: list[str] = ["<!-- pr-ui-snapshots -->", "## UI Snapshot Report"]
    lines.append(f"Status: {status_emoji} {status}")
    lines.append(f"Run: {run_url}")
    if error_note:
        lines.append("")
        lines.append(f"Note: {error_note}")

    failures = [case for case in cases if case["status"] in {"failed", "error"}]
    if failures:
        lines.append("")
        lines.append("Failures:")
        for case in failures:
            reason = case["reason"]
            prefix = STATUS_EMOJI.get(case["status"], "")
            if reason:
                lines.append(f"- {prefix} `{case['name']}`: {reason}")
            else:
                lines.append(f"- {prefix} `{case['name']}`")

    lines.append("")
    lines.append(render_snapshot_table(base_url))
    return "\n".join(lines).strip() + "\n"


def main() -> int:
    """CLI entry point for comment generation."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--junit", required=True, help="Path to JUnit XML file.")
    parser.add_argument("--output", required=True, help="Output markdown file.")
    parser.add_argument("--run-url", required=True, help="URL to the workflow run.")
    parser.add_argument("--repo", required=True, help="Repository in owner/name form.")
    parser.add_argument("--sha", required=True, help="Commit SHA for raw snapshot URLs.")
    parser.add_argument("--server-url", required=True, help="GitHub server URL.")
    args = parser.parse_args()

    if args.server_url.rstrip("/") == "https://github.com":
        base_url = f"https://raw.githubusercontent.com/{args.repo}/{args.sha}"
    else:
        base_url = f"{args.server_url.rstrip('/')}/{args.repo}/raw/{args.sha}"

    if not os.path.exists(args.junit):
        note = "JUnit report not found; snapshot tests may have failed to run."
        comment = render_comment([], args.run_url, base_url, error_note=note)
    else:
        cases = parse_junit(args.junit)
        comment = render_comment(cases, args.run_url, base_url)

    args.output = os.path.abspath(args.output)
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as handle:
        handle.write(comment)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
