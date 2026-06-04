#!/usr/bin/env python3
"""
watch-change-requests.py
x20_変更依頼/change-requests/ を監視し、_claude / _codex フォルダにファイルが届いたら
変更依頼ごとに git worktree + ブランチを作成してエージェントを自動起動する

使い方:
  python scripts/watch-change-requests.py
  python scripts/watch-change-requests.py --check-existing
  python scripts/watch-change-requests.py --claude-command "claude --model claude-opus-4-8"

worktree の配置場所（デフォルト）:
  ../[プロジェクト名]-[変更依頼ファイル名のベース]
  例: ../myproject-2026-06-04-add-user-auth

worktree の削除（マージ後）:
  git worktree remove ../myproject-2026-06-04-add-user-auth
  git branch -d feature/ai-2026-06-04-add-user-auth
"""

import argparse
import base64
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path


STATUS_MAP = {
    "010_backlog_person":               {"label": "草案・未着手",         "role": "person"},
    "020_planning_claude":              {"label": "依頼明確化・仕様策定", "role": "claude", "prompt": "変更依頼 {} を読んで仕様書を作成してください。"},
    "030_planning_confirmation_person": {"label": "質問への回答待ち",     "role": "person"},
    "040_planning_check_codex":         {"label": "仕様書精査",           "role": "codex",  "prompt": "変更依頼 {} の仕様書を技術精査してください。"},
    "050_implementation_codex":         {"label": "実装",                 "role": "codex",  "prompt": "変更依頼 {} を実装してください。"},
    "060_implementation_claude":        {"label": "実装レビュー",         "role": "claude", "prompt": "変更依頼 {} の実装をレビューしてください。"},
    "070_testing_codex":                {"label": "テスト実行",           "role": "codex",  "prompt": "変更依頼 {} のテストを実行してください。"},
    "080_review_claude":                {"label": "テスト結果レビュー",   "role": "claude", "prompt": "変更依頼 {} のテスト結果をレビューしてください。"},
    "090_test_person":                  {"label": "動作確認",             "role": "person"},
    "100_docs_claude":                  {"label": "ドキュメント更新",     "role": "claude", "prompt": "変更依頼 {} に基づきドキュメントを更新してください。"},
    "110_pr_claude":                    {"label": "PR 作成",              "role": "claude", "prompt": "変更依頼 {} に基づき PR を作成してください。"},
    "120_done_person":                  {"label": "完了・マージ待ち",     "role": "person"},
}


class C:
    GRAY    = "\033[90m"
    WHITE   = "\033[97m"
    CYAN    = "\033[96m"
    GREEN   = "\033[92m"
    MAGENTA = "\033[95m"
    YELLOW  = "\033[93m"
    RED     = "\033[91m"
    RESET   = "\033[0m"


def enable_ansi():
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetConsoleMode(
            ctypes.windll.kernel32.GetStdHandle(-11), 7
        )


def get_worktree_path(base_name, project_root, project_name, worktree_base_dir):
    base_dir = Path(worktree_base_dir) if worktree_base_dir else project_root.parent
    return base_dir / f"{project_name}-{base_name}"


def create_worktree(base_name, project_root, project_name, worktree_base_dir):
    branch_name   = f"feature/ai-{base_name}"
    worktree_path = get_worktree_path(base_name, project_root, project_name, worktree_base_dir)

    if worktree_path.exists():
        print(f"       {C.GRAY}worktree 再利用: {worktree_path}{C.RESET}")
        return worktree_path

    result = subprocess.run(
        ["git", "-C", str(project_root), "branch", "--list", branch_name],
        capture_output=True, text=True,
    )
    branch_exists = result.stdout.strip() != ""

    if branch_exists:
        cmd = ["git", "-C", str(project_root), "worktree", "add", str(worktree_path), branch_name]
    else:
        cmd = ["git", "-C", str(project_root), "worktree", "add", str(worktree_path), "-b", branch_name]

    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"       {C.RED}[エラー] worktree の作成に失敗しました:{C.RESET}")
        print(f"       {C.RED}{result.stderr or result.stdout}{C.RESET}")
        return None

    print(f"       {C.GRAY}worktree 作成: {worktree_path}  (branch: {branch_name}){C.RESET}")
    return worktree_path


def start_agent_session(command, worktree_path, cr_full_path, instr_full_path, prompt_template):
    instr_ref   = "@" + str(instr_full_path).replace("\\", "/")
    cr_path     = str(cr_full_path).replace("\\", "/")
    full_prompt = f"{instr_ref}\n{prompt_template.format(cr_path)}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(full_prompt)
        tmp_path = tmp.name

    wt_escaped = str(worktree_path).replace("'", "''")
    script = (
        f"Set-Location '{wt_escaped}'\n"
        f"$p = Get-Content -Raw '{tmp_path}' -Encoding UTF8\n"
        f"Remove-Item '{tmp_path}' -ErrorAction SilentlyContinue\n"
        f"& {command} $p\n"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    subprocess.Popen(
        ["powershell", "-NoExit", "-EncodedCommand", encoded],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def process_file(full_path, project_root, project_name, step_instructions_dir,
                 claude_command, codex_command, worktree_base_dir):
    if full_path.suffix != ".md":
        return
    if not full_path.exists():
        return

    folder_name     = full_path.parent.name
    file_name       = full_path.name
    base_name       = full_path.stem
    instr_full_path = project_root / step_instructions_dir / f"{folder_name}.md"

    info  = STATUS_MAP.get(folder_name, {})
    label = info.get("label", folder_name)
    role  = info.get("role", "unknown")

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{C.GRAY}[{ts}]{C.RESET} {C.WHITE}{file_name}{C.RESET}  →  {C.CYAN}{label}{C.RESET}")

    if role in ("claude", "codex"):
        if not instr_full_path.exists():
            print(f"       {C.YELLOW}[警告] 指示ファイルが見つかりません: {instr_full_path}{C.RESET}")
            return
        wt = create_worktree(base_name, project_root, project_name, worktree_base_dir)
        if not wt:
            return
        if role == "claude":
            print(f"       {C.GREEN}Claude Code を起動します{C.RESET}")
            start_agent_session(claude_command, wt, full_path, instr_full_path, info["prompt"])
        else:
            print(f"       {C.MAGENTA}Codex を起動します{C.RESET}")
            start_agent_session(codex_command, wt, full_path, instr_full_path, info["prompt"])

    elif role == "person":
        print(f"       {C.YELLOW}人間の対応をお待ちしています{C.RESET}")

    else:
        print(f"       {C.RED}不明なフォルダです ({folder_name}){C.RESET}")


def main():
    parser = argparse.ArgumentParser(description="変更依頼フォルダを監視してエージェントを自動起動")
    parser.add_argument("--change-requests-dir",   default="x20_変更依頼/change-requests")
    parser.add_argument("--step-instructions-dir", default="x20_変更依頼/step-instructions")
    parser.add_argument("--claude-command",         default="claude")
    parser.add_argument("--codex-command",          default="codex")
    parser.add_argument("--worktree-base-dir",      default="")
    parser.add_argument("--check-existing",         action="store_true",
                        help="起動時に既存ファイルも処理する")
    parser.add_argument("--poll-interval",          type=float, default=2.0,
                        help="監視ポーリング間隔（秒, default: 2.0）")
    args = parser.parse_args()

    enable_ansi()

    project_root = Path.cwd()
    project_name = project_root.name
    cr_dir       = Path(args.change_requests_dir)

    if not cr_dir.exists():
        print(f"ディレクトリが見つかりません: {cr_dir}", file=sys.stderr)
        sys.exit(1)

    processed = set()

    if args.check_existing:
        print(f"{C.GRAY}既存のファイルを確認中...{C.RESET}")
    for md_file in sorted(cr_dir.rglob("*.md")):
        resolved = md_file.resolve()
        processed.add(resolved)
        if args.check_existing:
            process_file(
                md_file, project_root, project_name,
                args.step_instructions_dir, args.claude_command,
                args.codex_command, args.worktree_base_dir,
            )

    print(f"\n{C.GREEN}変更依頼フォルダを監視中: {cr_dir}{C.RESET}")
    print(f"{C.GREEN}  _claude → worktree 作成 + Claude Code 自動起動{C.RESET}")
    print(f"{C.MAGENTA}  _codex  → worktree 作成 + Codex 自動起動{C.RESET}")
    print(f"{C.YELLOW}  _person → 通知のみ{C.RESET}")
    print(f"{C.GRAY}終了: Ctrl+C{C.RESET}\n")

    try:
        while True:
            for md_file in cr_dir.rglob("*.md"):
                resolved = md_file.resolve()
                if resolved not in processed:
                    processed.add(resolved)
                    process_file(
                        md_file, project_root, project_name,
                        args.step_instructions_dir, args.claude_command,
                        args.codex_command, args.worktree_base_dir,
                    )
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}監視を終了しました。{C.RESET}")


if __name__ == "__main__":
    main()
