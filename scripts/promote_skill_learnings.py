#!/usr/bin/env python3
"""Promote approved JSONL learnings into skill reference files."""

from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path

from log_skill_learning import DEFAULT_LOG, redact_text
from skill_repo import REPO_ROOT, Skill, load_skills


LEARNED_REF = "references/learned-usage.md"
LEARNED_ROW = (
    "| [references/learned-usage.md](references/learned-usage.md) | "
    "Reusable learnings promoted from prior usage; read when troubleshooting similar failures or edge cases. |"
)


def read_records(path: Path) -> list[dict[str, object]]:
    records: list[dict[str, object]] = []
    if not path.exists():
        return records
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            record = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{lineno}: invalid JSONL: {exc}") from exc
        records.append(record)
    return records


def skill_lookup(include_untracked: bool = False) -> dict[str, Skill]:
    lookup: dict[str, Skill] = {}
    for skill in load_skills(REPO_ROOT, include_untracked=include_untracked):
        lookup[skill.name] = skill
        lookup[skill.dir_name] = skill
    return lookup


def selected_records(records: list[dict[str, object]], promote_all: bool, skill_filter: str | None) -> list[dict[str, object]]:
    selected = []
    for record in records:
        if skill_filter and record.get("skill") != skill_filter:
            continue
        if promote_all or record.get("status") == "approved":
            selected.append(record)
    return selected


def existing_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return set(re.findall(r"Learning ID: `([^`]+)`", path.read_text(encoding="utf-8")))


def render_entry(record: dict[str, object]) -> str:
    severity = redact_text(str(record.get("severity", "medium")))
    summary = redact_text(str(record.get("summary", ""))).strip()
    detail = redact_text(str(record.get("detail", ""))).strip()
    source_task = redact_text(str(record.get("source_task", ""))).strip()
    learning_id = redact_text(str(record.get("id", ""))).strip()
    timestamp = redact_text(str(record.get("timestamp_utc", ""))).strip()

    lines = [f"- **[{severity}] {summary}**"]
    if detail:
        lines.append(f"  - Detail: {detail}")
    if source_task:
        lines.append(f"  - Source task: {source_task}")
    if timestamp:
        lines.append(f"  - Captured: {timestamp}")
    if learning_id:
        lines.append(f"  - Learning ID: `{learning_id}`")
    return "\n".join(lines)


def ensure_router_link(skill_path: Path) -> None:
    text = skill_path.read_text(encoding="utf-8")
    if LEARNED_REF in text:
        return

    heading = "## When to load which sub-doc"
    if heading in text:
        lines = text.splitlines()
        for index, line in enumerate(lines):
            if line.strip() == heading:
                for table_index in range(index + 1, min(index + 8, len(lines))):
                    if lines[table_index].startswith("|---"):
                        lines.insert(table_index + 1, LEARNED_ROW)
                        skill_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
                        return

    addition = (
        "\n## Learned Usage Notes\n\n"
        "| Sub-doc | Use when |\n"
        "|---|---|\n"
        f"{LEARNED_ROW}\n"
    )
    skill_path.write_text(text.rstrip() + addition, encoding="utf-8")


def promote(records: list[dict[str, object]], lookup: dict[str, Skill], write: bool) -> int:
    by_skill: dict[str, list[dict[str, object]]] = defaultdict(list)
    for record in records:
        by_skill[str(record.get("skill", ""))].append(record)

    promoted = 0
    for skill_name, skill_records in sorted(by_skill.items()):
        skill = lookup.get(skill_name)
        if not skill:
            print(f"skip {skill_name}: no matching skill")
            continue
        ref_path = skill.path.parent / LEARNED_REF
        seen = existing_ids(ref_path)
        new_records = [record for record in skill_records if str(record.get("id", "")) not in seen]
        if not new_records:
            print(f"skip {skill.name}: no new approved learnings")
            continue

        rendered = "\n\n".join(render_entry(record) for record in new_records)
        if not write:
            print(f"would promote {len(new_records)} learning(s) to {ref_path.relative_to(REPO_ROOT)}")
            print(rendered)
            continue

        ref_path.parent.mkdir(parents=True, exist_ok=True)
        if ref_path.exists():
            existing = ref_path.read_text(encoding="utf-8").rstrip()
            content = existing + "\n\n" + rendered + "\n"
        else:
            content = "# Learned Usage Notes\n\nPromoted reusable learnings from prior skill use.\n\n" + rendered + "\n"
        ref_path.write_text(content, encoding="utf-8")
        ensure_router_link(skill.path)
        promoted += len(new_records)
        print(f"promoted {len(new_records)} learning(s) to {ref_path.relative_to(REPO_ROOT)}")
    return promoted


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_LOG, help=f"JSONL input path (default: {DEFAULT_LOG})")
    parser.add_argument("--skill", help="limit promotion to one skill name/folder")
    parser.add_argument("--promote-all", action="store_true", help="promote candidate records without requiring status=approved")
    parser.add_argument("--include-untracked", action="store_true", help="allow promotion into untracked top-level skills")
    parser.add_argument("--write", action="store_true", help="write changes; default is dry-run")
    args = parser.parse_args()

    records = selected_records(read_records(args.input), args.promote_all, args.skill)
    lookup = skill_lookup(include_untracked=args.include_untracked)
    promoted = promote(records, lookup, args.write)
    if not args.write:
        print("dry run only; pass --write to update skill files")
    return 0 if promoted or not args.write else 1


if __name__ == "__main__":
    raise SystemExit(main())
