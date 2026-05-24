from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


FRONTEND_EXTENSIONS = {".html", ".js", ".jsx", ".ts", ".tsx"}

PATTERNS = [
    ("fetch", re.compile(r"fetch\s*\(\s*[\"']([^\"']+)[\"']")),
    ("axios", re.compile(r"axios(?:\.[a-zA-Z]+)?\s*\(\s*[\"']([^\"']+)[\"']")),
    ("xhr_open", re.compile(r"\.open\s*\(\s*[\"'][A-Z]+[\"']\s*,\s*[\"']([^\"']+)[\"']")),
    ("data_action", re.compile(r"data-action=[\"']([^\"']+)[\"']")),
    (
        "endpoint_literal",
        re.compile(
            r"[\"']((?:/api|/runtime|/system|/dashboard|/operator|/internet|/design-portal|/cad|/portfolio|/proof|/health)[^\"'` <>)]+)[\"']"
        ),
    ),
]


def discover_calls(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    seen: set[tuple[str, int, str, str]] = set()
    for path in sorted(item for item in root.rglob("*") if item.suffix in FRONTEND_EXTENSIONS):
        if ".bak" in path.name.lower():
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        rel = path.as_posix()
        for kind, pattern in PATTERNS:
            for match in pattern.finditer(text):
                endpoint = match.group(1).strip()
                if "${" in endpoint:
                    endpoint = endpoint.split("${", 1)[0]
                if not endpoint.startswith("/"):
                    continue
                if endpoint in {"/api/", "/runtime/", "/system/", "/dashboard/", "/operator/"}:
                    continue
                line = text.count("\n", 0, match.start()) + 1
                key = (rel, line, endpoint, kind)
                if key in seen:
                    continue
                seen.add(key)
                rows.append(
                    {
                        "file": rel,
                        "line": line,
                        "kind": kind,
                        "frontend_path": endpoint,
                    }
                )
    return sorted(rows, key=lambda row: (str(row["frontend_path"]), str(row["file"]), int(row["line"]), str(row["kind"])))


def write_reports(rows: list[dict[str, object]], report_date: str, reports_dir: Path) -> dict[str, object]:
    reports_dir.mkdir(parents=True, exist_ok=True)
    txt_path = reports_dir / f"frontend_fetch_map_{report_date}.txt"
    json_path = reports_dir / f"frontend_fetch_map_{report_date}.json"

    lines = [
        "# Frontend Fetch Map",
        f"Generated: {report_date}",
        "",
        f"Total caller entries: {len(rows)}",
        "",
        "| frontend_path | kind | file | line |",
        "|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| `{row['frontend_path']}` | {row['kind']} | `{row['file']}` | {row['line']} |"
        )
    txt_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    json_path.write_text(
        json.dumps(
            {
                "schema_version": "claire.frontend_fetch_map.v1",
                "generated_at": report_date,
                "caller_count": len(rows),
                "calls": rows,
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    return {"caller_count": len(rows), "txt": str(txt_path), "json": str(json_path)}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--frontend-root", default="frontend")
    parser.add_argument("--reports-dir", default="reports")
    parser.add_argument("--date", default="20260524")
    args = parser.parse_args()
    rows = discover_calls(Path(args.frontend_root))
    print(json.dumps(write_reports(rows, args.date, Path(args.reports_dir)), indent=2))


if __name__ == "__main__":
    main()
