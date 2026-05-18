#!/usr/bin/env python3
# Claire Syntalion pytest consistency audit
# Repaired by v19 Structural Repair Pack 1.2

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path.cwd()
OUT = ROOT / '_claire_audit_pytest_consistency'
REPORT_JSON = OUT / 'pytest_consistency_audit.json'
REPORT_MD = OUT / 'pytest_consistency_audit.md'

def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def rel(path: Path) -> str:
    try:
        return str(path.resolve().relative_to(ROOT.resolve())).replace('\\', '/')
    except Exception:
        return str(path).replace('\\', '/')

def syntax_error(path: Path) -> dict[str, Any] | None:
    try:
        ast.parse(path.read_text(encoding='utf-8', errors='replace'))
        return None
    except SyntaxError as exc:
        return {
            'path': rel(path),
            'line': exc.lineno,
            'message': exc.msg,
            'text': exc.text.strip() if exc.text else '',
        }

def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    test_root = ROOT / 'tests'
    test_files = sorted(test_root.rglob('test_*.py')) if test_root.exists() else []
    syntax_failures = []
    for path in test_files:
        err = syntax_error(path)
        if err is not None:
            syntax_failures.append(err)
    report = {
        'audit': 'pytest_consistency_audit',
        'generated_at': utc_now(),
        'test_file_count': len(test_files),
        'syntax_failure_count': len(syntax_failures),
        'syntax_failures': syntax_failures,
        'stop_go': 'GO_PYTEST_COLLECTION_CHECK' if not syntax_failures else 'STOP_TEST_SYNTAX_FAILURES',
    }
    REPORT_JSON.write_text(json.dumps(report, indent=2, sort_keys=True) + '\n', encoding='utf-8')
    md = []
    md.append('# Pytest Consistency Audit')
    md.append('')
    md.append(f"- Generated: `{report['generated_at']}`")
    md.append(f"- Stop/Go: **{report['stop_go']}**")
    md.append(f"- Test files: **{report['test_file_count']}**")
    md.append(f"- Syntax failures: **{report['syntax_failure_count']}**")
    md.append('')
    md.append('## Syntax Failures')
    if syntax_failures:
        for item in syntax_failures:
            md.append(f"- `{item['path']}` line {item.get('line')}: {item.get('message')} | {item.get('text')}")
    else:
        md.append('- None.')
    REPORT_MD.write_text('\n'.join(md) + '\n', encoding='utf-8')
    print('Pytest consistency audit complete.')
    print('Stop/Go:', report['stop_go'])
    print('Report:', REPORT_MD)
    print('JSON:', REPORT_JSON)
    return 0 if not syntax_failures else 1

if __name__ == '__main__':
    raise SystemExit(main())
