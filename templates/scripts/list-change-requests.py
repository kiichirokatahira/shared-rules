#!/usr/bin/env python3
"""
list-change-requests.py
使い方: python scripts/list-change-requests.py
デフォルト: <change-requests-dir>/STATUS.md に出力
オプション: --output-file <path> で出力先を変更、--output-file "" で標準出力

フォルダ構造:
  change-requests/
    {step_folder}/
      {cr_name}/                    ← 変更依頼ごとのサブフォルダ
        ChangeRequest.md           ← 依頼書（必須）
"""

import argparse
import re
import sys
from pathlib import Path

STATUS_MAP = {
    "010_backlog_person":    {"label": "草案・未着手",           "assignee": "人間"},
    "020_planning_ai":       {"label": "依頼明確化・仕様策定中", "assignee": "AI"},
    "050_implementation_ai": {"label": "実装中",                 "assignee": "AI"},
    "055_code_review_ai":    {"label": "コードレビュー中",       "assignee": "AI"},
    "070_testing_ai":        {"label": "テスト実行中",           "assignee": "AI"},
    "080_review_ai":         {"label": "テスト結果レビュー中",   "assignee": "AI"},
    "090_test_person":       {"label": "動作確認中",             "assignee": "人間"},
    "100_docs_ai":           {"label": "ドキュメント更新中",     "assignee": "AI"},
    "110_pr_ai":             {"label": "PR 作成中",              "assignee": "AI"},
    "120_done_person":       {"label": "完了・マージ待ち",       "assignee": "人間"},
}


def main():
    parser = argparse.ArgumentParser(description="変更依頼ステータス一覧を出力")
    parser.add_argument("--cr-repo", default=None,
                        help="変更依頼リポジトリのパス（省略時はカレントディレクトリ）")
    parser.add_argument("--change-requests-dir", default="x20_変更依頼/change-requests",
                        help="変更依頼ディレクトリ (default: x20_変更依頼/change-requests)")
    parser.add_argument("--output-file", default=None,
                        help="出力ファイルパス（省略時は <change-requests-dir>/STATUS.md、\"\" で標準出力）")
    args = parser.parse_args()

    cr_base = Path(args.cr_repo).resolve() if args.cr_repo else Path(".")
    cr_dir  = cr_base / args.change_requests_dir

    if args.output_file is None:
        args.output_file = str(cr_dir / "STATUS.md")
    if not cr_dir.exists():
        print(f"ディレクトリが見つかりません: {cr_dir}", file=sys.stderr)
        sys.exit(1)

    rows = []
    for step_folder in sorted(cr_dir.iterdir()):
        if not step_folder.is_dir():
            continue
        step_folder_name = step_folder.name

        for cr_subfolder in sorted(step_folder.iterdir()):
            if not cr_subfolder.is_dir():
                continue
            cr_md = cr_subfolder / "ChangeRequest.md"
            if not cr_md.exists():
                continue

            cr_name = cr_subfolder.name
            date  = ""
            title = cr_name
            m = re.match(r"^(\d{4}-\d{2}-\d{2})-(.+)$", cr_name)
            if m:
                date  = m.group(1)
                title = m.group(2)

            m2   = re.match(r"^(\d+)_", step_folder_name)
            step = int(m2.group(1)) if m2 else 999

            info = STATUS_MAP.get(step_folder_name, {})
            rows.append({
                "step":     step,
                "date":     date,
                "title":    title,
                "status":   info.get("label", step_folder_name),
                "assignee": info.get("assignee", "-"),
                "folder":   step_folder_name,
                "cr_name":  cr_name,
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
        link = f"{args.change_requests_dir}/{row['folder']}/{row['cr_name']}/ChangeRequest.md"
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
