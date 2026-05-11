#!/usr/bin/env python3
"""
Generate tasks.csv and tasks.md from a tasks JSON file.

Both outputs are strictly identical in content, only differ in format.
Schema: ID, Epic, Task, Opt (h), Real (h), Pess (h), with a TOTAL row at the end.

Usage:
    python generate.py --input tasks.json --output-dir /path/to/out --project-name "GUI"

Input JSON shape:
    {
      "tasks": [
        {"epic": "Repo/Alap", "task": "...", "opt": 4, "real": 8, "pess": 16},
        ...
      ]
    }
"""

import argparse
import csv
import json
from datetime import datetime, timezone
from pathlib import Path

COLUMNS = ["ID", "Epic", "Task", "Opt (h)", "Real (h)", "Pess (h)"]


def load_tasks(input_path: Path) -> list[dict]:
    data = json.loads(input_path.read_text(encoding="utf-8"))
    if "tasks" not in data or not isinstance(data["tasks"], list):
        raise ValueError("Input JSON must have a 'tasks' array")
    tasks = data["tasks"]
    for i, t in enumerate(tasks, start=1):
        for k in ("epic", "task", "opt", "real", "pess"):
            if k not in t:
                raise ValueError(f"Task #{i} is missing required key: {k}")
        for k in ("opt", "real", "pess"):
            if not isinstance(t[k], int) or t[k] < 0:
                raise ValueError(
                    f"Task #{i} ({t['task']!r}): {k} must be a non-negative integer, got {t[k]!r}"
                )
    return tasks


def build_rows(tasks: list[dict]) -> list[list]:
    """Return rows including header, data rows with assigned IDs, and TOTAL row."""
    rows = [COLUMNS]
    total_opt = total_real = total_pess = 0
    for idx, t in enumerate(tasks, start=1):
        rows.append([idx, t["epic"], t["task"], t["opt"], t["real"], t["pess"]])
        total_opt += t["opt"]
        total_real += t["real"]
        total_pess += t["pess"]
    rows.append(["", "", "TOTAL", total_opt, total_real, total_pess])
    return rows


def write_csv(rows: list[list], path: Path) -> None:
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        for row in rows:
            writer.writerow(row)


def _md_table(rows: list[list]) -> str:
    """Build a markdown table with sample-style alignment.

    ID right-aligned, Epic + Task left-aligned, hour columns right-aligned.
    Column widths derived from the widest cell per column for readability.
    """
    header, *body = rows
    widths = [
        max(len(str(r[i])) for r in rows) for i in range(len(header))
    ]
    # Minimum header width so the alignment markers fit nicely
    widths = [max(w, 3) for w in widths]

    aligns = ["right", "left", "left", "right", "right", "right"]

    def fmt_row(row: list) -> str:
        cells = []
        for i, cell in enumerate(row):
            s = str(cell)
            if aligns[i] == "right":
                cells.append(s.rjust(widths[i]))
            else:
                cells.append(s.ljust(widths[i]))
        return "| " + " | ".join(cells) + " |"

    def sep_for(align: str, width: int) -> str:
        # Use width-1 dashes to make room for the alignment colon(s).
        # Leave at least 3 dashes total to be safe.
        dashes = "-" * max(width, 3)
        if align == "right":
            return dashes[:-1] + ":"
        elif align == "left":
            return ":" + dashes[1:]
        else:
            return ":" + dashes[1:-1] + ":"

    sep_cells = [sep_for(aligns[i], widths[i]) for i in range(len(header))]
    sep_line = "| " + " | ".join(sep_cells) + " |"

    lines = [fmt_row(header), sep_line]
    for row in body:
        lines.append(fmt_row(row))
    return "\n".join(lines)


def write_md(rows: list[list], path: Path, project_name: str) -> None:
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    title = f"{project_name} Task Estimates" if project_name else "Task Estimates"
    table = _md_table(rows)
    content = (
        f"Timestamp: {timestamp}\n"
        f"Version: 1.0.0\n"
        f"\n"
        f"# {title}\n"
        f"\n"
        f"This file is a direct Markdown export of `tasks.csv`.\n"
        f"**Content is identical; only the format differs.**\n"
        f"\n"
        f"{table}\n"
    )
    path.write_text(content, encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path, help="Input tasks JSON file")
    parser.add_argument(
        "--output-dir",
        required=True,
        type=Path,
        help="Directory to write tasks.csv and tasks.md into",
    )
    parser.add_argument(
        "--project-name",
        default="",
        help="Project name used as the markdown title prefix (e.g. 'GUI' -> 'GUI Task Estimates')",
    )
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    tasks = load_tasks(args.input)
    rows = build_rows(tasks)

    csv_path = args.output_dir / "tasks.csv"
    md_path = args.output_dir / "tasks.md"

    write_csv(rows, csv_path)
    write_md(rows, md_path, args.project_name)

    totals = rows[-1]
    print(json.dumps({
        "csv": str(csv_path),
        "md": str(md_path),
        "task_count": len(tasks),
        "total_opt": totals[3],
        "total_real": totals[4],
        "total_pess": totals[5],
    }, indent=2))


if __name__ == "__main__":
    main()
