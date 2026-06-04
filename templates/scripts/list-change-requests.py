#!/usr/bin/env python3
"""
list-change-requests.py
使い方: python scripts/list-change-requests.py
オプション: --output-file x20_変更依頼/STATUS.md でファイルに出力
"""

import argparse
import re
import sys
from pathlib import Path

STATUS_MAP = {
    "010_backlog_person":               {"label": "草案・未着手",           "assignee": "人間"},
    "020_planning_claude":              {"label": "依頼明確化・仕様策定中", "assignee": "Claude"},
    "030_planning_confirmation_person": {"label": "質問への回答待ち",       "assignee": "人間"},
    "040_planning_check_codex":         {"label": "仕様書精査中",           "assignee": "Codex"},
    "050_implementation_codex":         {"label": "実装中",                 "assignee": "Codex"},
    "060_implementation_claude":        {"label": "実装レビュー中",         "assignee": "Claude"},
    "070_testing_codex":                {"label": "テスト実行中",           "assignee": "Codex"},
    "080_review_claude":                {"label": "テスト結果レビュー中",   "assignee": "Claude"},
    "090_test_person":                  {"label": "動作確認中",             "assignee": "人間"},
    "100_docs_claude":                  {"label": "ドキュメント更新中",     "assignee": "Claude"},
    "110_pr_claude":                    {"label": "PR 作成中",              "assignee": "Claude"},
    "120_done_person":                  {"label": "完了・マージ待ち",       "assignee": "人間"},
}


def main():
    parser = argparse.ArgumentParser(description="変更依頼ステータス一覧を出力")
    parser.add_argument("--change-requests-dir", default="x20_変更依頼/change-requests",
                        help="変更依頼ディレクトリ (default: x20_変更依頼/change-requests)")
    parser.add_argument("--output-file", default="",
                        help="出力ファイルパス（省略時は標準出力）")
    args = parser.parse_args()

    cr_dir = Path(args.change_requests_dir)
    if not cr_dir.exists():
        print(f"ディレクトリが見つかりません: {cr_dir}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for folder in sorted(cr_dir.iterdir()):
        if not folder.is_dir():
            continue
        folder_name = folder.name
        for md_file in sorted(folder.glob("*.md")):
            base_name = md_file.stem
            date = ""
            title = base_name
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", base_name)
            if m:
                date = m.group(1)
                title = m.group(2)

            m2 = re.match(r"^(\d+)_", folder_name)
            step = int(m2.group(1)) if m2 else 999

            info = STATUS_MAP.get(folder_name, {})
            rows.append({
                "step":     step,
                "date":     date,
                "title":    title,
                "status":   info.get("label", folder_name),
                "assignee": info.get("assignee", "-"),
                "folder":   folder_name,
                "filename": md_file.name,
            })

    if not rows:
        print("変更依頼が見つかりませんでした。")
        sys.exit(0)

    rows.sort(key=lambda r: (r["step"], r["date"]))

    lines = [
        "# 変更依頼 ステータス一覧",
        "",
        "| 変更依頼 | 作成日 | ステータス | 担当 | Step |",
        "|---|---|---|---|:---:|",
    ]
    for row in rows:
        link = f"{args.change_requests_dir}/{row['folder']}/{row['filename']}"
        lines.append(
            f"| [{row['title']}]({link}) | {row['date']} | {row['status']} | {row['assignee']} | {row['step']} |"
        )

    output = "\n".join(lines)

    if args.output_file:
        Path(args.output_file).write_text(output, encoding="utf-8")
        print(f"出力しました: {args.output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
