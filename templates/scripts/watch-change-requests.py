#!/usr/bin/env python3
"""
watch-change-requests.py
x20_変更依頼/change-requests/ を監視し、_ai フォルダにファイルが届いたら
エージェントを自動起動する（1件ずつ処理）

使い方:
  python scripts/watch-change-requests.py
  python scripts/watch-change-requests.py --cr-repo ../myproject-cr
  python scripts/watch-change-requests.py --auto
  python scripts/watch-change-requests.py --auto --check-existing
  python scripts/watch-change-requests.py --claude-command "claude --model claude-opus-4-8"

オプション:
  --cr-repo          変更依頼リポジトリのパス（省略時はカレントディレクトリ）
                     プロジェクトリポジトリとは別に CR リポジトリを分離している場合に指定する
  --auto             Claude に --dangerously-skip-permissions、Codex に --dangerously-bypass-approvals-and-sandbox を渡して自動実行モードで起動する
  --check-existing   起動時に既存ファイルも処理する
  --claude-steps     Claude で実行するステップ名をカンマ区切りで指定（デフォルト: 020_planning_ai,080_review_ai,100_docs_ai,110_pr_ai）
  --codex-steps      Codex で実行するステップ名をカンマ区切りで指定（デフォルト: 040_planning_check_ai,050_implementation_ai,070_testing_ai）
  --poll-interval    ポーリング間隔（秒、デフォルト: 5.0）
  --retry-timeout    エージェントが CR を移動しないまま同フォルダに留まった場合にリトライするまでの秒数（デフォルト: 3600）

処理の順序:
  同一リポジトリで複数の変更依頼が発生した場合、1件ずつ順番に処理します。
  020〜110 のステップに変更依頼が存在する間は、次の変更依頼の起動を待機します。
  現在の変更依頼が 120_done_person に移動するとスクリプトが次を自動で起動します。

エージェントの実行場所:
  プロジェクトリポジトリのルート（カレントディレクトリ）で直接実行します（git worktree は使用しません）。
  変更依頼ファイルの絶対パスは CR リポジトリを指します（--cr-repo 指定時）。
  エージェントは Step 050 で ai-YYYYMMDD-xxxx ブランチを作成し、
  Step 120 のマージ後に人間が main へ戻します。
"""

import argparse
import base64
import subprocess
import sys
import tempfile
import time
from datetime import datetime
from pathlib import Path

DEFAULT_RETRY_TIMEOUT = 3600  # エージェントが起動しても CR を移動しない場合のリトライ間隔（秒）


STATUS_MAP = {
    "010_backlog_person":    {"label": "草案・未着手",         "role": "person"},
    "020_planning_ai":       {"label": "依頼明確化・仕様策定", "role": "ai", "default_agent": "claude", "prompt": "変更依頼 {} を読んで仕様書を作成してください。"},
    "040_planning_check_ai": {"label": "仕様書精査",           "role": "ai", "default_agent": "codex",  "prompt": "変更依頼 {} の仕様書を技術精査してください。"},
    "050_implementation_ai": {"label": "実装",                 "role": "ai", "default_agent": "codex",  "prompt": "変更依頼 {} を実装してください。"},
    "060_infra_person":      {"label": "インフラ事前作業",     "role": "person"},
    "070_testing_ai":        {"label": "テスト実行",           "role": "ai", "default_agent": "codex",  "prompt": "変更依頼 {} のテストを実行してください。"},
    "080_review_ai":         {"label": "テスト結果レビュー",   "role": "ai", "default_agent": "claude", "prompt": "変更依頼 {} のテスト結果をレビューしてください。"},
    "090_test_person":       {"label": "動作確認",             "role": "person"},
    "100_docs_ai":           {"label": "ドキュメント更新",     "role": "ai", "default_agent": "claude", "prompt": "変更依頼 {} に基づきドキュメントを更新してください。"},
    "110_pr_ai":             {"label": "PR 作成",              "role": "ai", "default_agent": "claude", "prompt": "変更依頼 {} に基づき PR を作成してください。"},
    "120_done_person":       {"label": "完了・マージ待ち",     "role": "person"},
}

# 「処理中」とみなすステップ（010_backlog_person と 120_done_person 以外）
IN_FLIGHT_STEPS = {k for k in STATUS_MAP if k not in ("010_backlog_person", "120_done_person")}

DEFAULT_CLAUDE_STEPS = "020_planning_ai,080_review_ai,100_docs_ai,110_pr_ai"
DEFAULT_CODEX_STEPS  = "040_planning_check_ai,050_implementation_ai,070_testing_ai"


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


def build_step_agent_map(claude_steps, codex_steps):
    """ステップ名 -> エージェント種別 ("claude" | "codex") のマップを構築する"""
    step_agent_map = {}
    for step in claude_steps.split(","):
        step = step.strip()
        if step:
            step_agent_map[step] = "claude"
    for step in codex_steps.split(","):
        step = step.strip()
        if step:
            step_agent_map[step] = "codex"
    return step_agent_map


def resolve_agent(folder_name, step_agent_map):
    """フォルダ名からエージェント種別を解決する（CLI 指定 > default_agent の順）"""
    if folder_name in step_agent_map:
        return step_agent_map[folder_name]
    info = STATUS_MAP.get(folder_name, {})
    return info.get("default_agent")


def find_in_flight_cr(cr_dir, exclude_key=None):
    """020〜110 のステップで処理中の変更依頼を返す（key, folder）。なければ None"""
    for md_file in sorted(Path(cr_dir).rglob("ChangeRequest.md")):
        if md_file.parent.name in IN_FLIGHT_STEPS:
            key    = md_file.stem
            folder = md_file.parent.name
        elif md_file.parent.parent.name in IN_FLIGHT_STEPS:
            key    = md_file.parent.name
            folder = md_file.parent.parent.name
        else:
            continue
        if key != exclude_key:
            return key, folder
    return None


def start_agent_session(command, project_root, cr_full_path, instr_full_path, prompt_template):
    instr_ref   = "@" + str(instr_full_path).replace("\\", "/")
    cr_path     = str(cr_full_path).replace("\\", "/")
    full_prompt = f"{instr_ref}\n{prompt_template.format(cr_path)}"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False, encoding="utf-8") as tmp:
        tmp.write(full_prompt)
        tmp_path = tmp.name

    root_escaped = str(project_root).replace("'", "''")
    script = (
        f"Set-Location '{root_escaped}'\n"
        f"$p = Get-Content -Raw '{tmp_path}' -Encoding UTF8\n"
        f"Remove-Item '{tmp_path}' -ErrorAction SilentlyContinue\n"
        f"& {command} $p\n"
        f"if ($LASTEXITCODE -ne 0) {{\n"
        f"    Write-Host ''\n"
        f"    Write-Host '[エラー] 終了コード: ' $LASTEXITCODE -ForegroundColor Red\n"
        f"    Write-Host 'エラー内容を確認してから Enter で閉じてください' -ForegroundColor Yellow\n"
        f"    Read-Host\n"
        f"}}\n"
    )
    encoded = base64.b64encode(script.encode("utf-16-le")).decode("ascii")
    subprocess.Popen(
        ["powershell", "-EncodedCommand", encoded],
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )


def process_file(full_path, project_root, cr_dir, step_instructions_base,
                 claude_command, codex_command, step_agent_map):
    """
    変更依頼ファイルを処理する。
    戻り値: True = 処理済み（processed に追加する）, False = 待機中（次のポーリングで再試行）
    """
    if full_path.suffix != ".md":
        return True
    if not full_path.exists():
        return True

    if full_path.parent.name in STATUS_MAP:
        folder_name = full_path.parent.name
        base_name   = full_path.stem
    elif full_path.parent.parent.name in STATUS_MAP:
        folder_name = full_path.parent.parent.name
        base_name   = full_path.parent.name
    else:
        return True

    file_name       = full_path.name
    instr_full_path = step_instructions_base / f"{folder_name}.md"

    info  = STATUS_MAP.get(folder_name, {})
    label = info.get("label", folder_name)
    role  = info.get("role", "unknown")

    ts = datetime.now().strftime("%H:%M:%S")
    print(f"\n{C.GRAY}[{ts}]{C.RESET} {C.WHITE}{file_name}{C.RESET}  →  {C.CYAN}{label}{C.RESET}")

    if role == "ai":
        if not instr_full_path.exists():
            print(f"       {C.YELLOW}[警告] 指示ファイルが見つかりません: {instr_full_path}{C.RESET}")
            return True

        # 1件ずつ処理: 別の変更依頼が処理中の場合は待機
        in_flight = find_in_flight_cr(cr_dir, exclude_key=base_name)
        if in_flight:
            in_flight_key, in_flight_folder = in_flight
            in_flight_label = STATUS_MAP.get(in_flight_folder, {}).get("label", in_flight_folder)
            print(f"       {C.YELLOW}[待機] 別の変更依頼が処理中: {in_flight_key} ({in_flight_label}){C.RESET}")
            print(f"       {C.YELLOW}       完了後に自動で起動します（次回ポーリング時に再確認）{C.RESET}")
            return False  # processed に追加しない → 次のポーリングで再試行

        agent = resolve_agent(folder_name, step_agent_map)
        if agent == "claude":
            print(f"       {C.GREEN}Claude Code を起動します{C.RESET}")
            start_agent_session(claude_command, project_root, full_path, instr_full_path, info["prompt"])
        elif agent == "codex":
            print(f"       {C.MAGENTA}Codex を起動します{C.RESET}")
            start_agent_session(codex_command, project_root, full_path, instr_full_path, info["prompt"])
        else:
            print(f"       {C.RED}[エラー] エージェントが解決できません ({folder_name}){C.RESET}")

    elif role == "person":
        print(f"       {C.YELLOW}人間の対応をお待ちしています{C.RESET}")

    else:
        print(f"       {C.RED}不明なフォルダです ({folder_name}){C.RESET}")

    return True


def main():
    parser = argparse.ArgumentParser(description="変更依頼フォルダを監視してエージェントを自動起動（1件ずつ処理）")
    parser.add_argument("--cr-repo",                default=None,
                        help="変更依頼リポジトリのパス（省略時はカレントディレクトリ）")
    parser.add_argument("--change-requests-dir",   default="x20_変更依頼/change-requests")
    parser.add_argument("--step-instructions-dir", default="x20_変更依頼/step-instructions")
    parser.add_argument("--claude-command",         default="claude")
    parser.add_argument("--codex-command",          default="codex exec")
    parser.add_argument("--claude-steps",           default=DEFAULT_CLAUDE_STEPS,
                        help=f"Claude で実行するステップ名（カンマ区切り、デフォルト: {DEFAULT_CLAUDE_STEPS}）")
    parser.add_argument("--codex-steps",            default=DEFAULT_CODEX_STEPS,
                        help=f"Codex で実行するステップ名（カンマ区切り、デフォルト: {DEFAULT_CODEX_STEPS}）")
    parser.add_argument("--auto",                   action="store_true", default=True,
                        help="Claude に --dangerously-skip-permissions、Codex に --dangerously-bypass-approvals-and-sandbox を渡して自動実行モードで起動する（デフォルト: 有効）")
    parser.add_argument("--check-existing",         action="store_true", default=True,
                        help="起動時に既存ファイルも処理する（デフォルト: 有効）")
    parser.add_argument("--poll-interval",          type=float, default=5.0,
                        help="監視ポーリング間隔（秒, default: 5.0）")
    parser.add_argument("--retry-timeout",           type=float, default=DEFAULT_RETRY_TIMEOUT,
                        help=f"エージェントが CR を移動しない場合に再起動するまでの秒数（default: {DEFAULT_RETRY_TIMEOUT}）")
    args = parser.parse_args()

    enable_ansi()

    if args.auto:
        args.claude_command = args.claude_command + " --dangerously-skip-permissions"
        args.codex_command  = args.codex_command  + " --dangerously-bypass-approvals-and-sandbox"

    step_agent_map = build_step_agent_map(args.claude_steps, args.codex_steps)

    project_root = Path.cwd()
    cr_repo      = Path(args.cr_repo).resolve() if args.cr_repo else project_root
    cr_dir       = cr_repo / args.change_requests_dir
    step_instructions_base = cr_repo / args.step_instructions_dir

    if not cr_dir.exists():
        print(f"ディレクトリが見つかりません: {cr_dir}", file=sys.stderr)
        sys.exit(1)

    # stem -> (現在のフォルダ名, 起動時刻) で管理する
    # 同じフォルダへの再移動も検出でき、エージェントが CR を移動しなかった場合は
    # retry_timeout 秒後に自動リトライする
    processed = {}  # type: dict[str, tuple[str, float]]

    if args.check_existing:
        print(f"{C.GRAY}既存のファイルを確認中...{C.RESET}")
    for md_file in sorted(cr_dir.rglob("ChangeRequest.md")):
        if md_file.parent.name in STATUS_MAP:
            key    = md_file.stem
            folder = md_file.parent.name
        elif md_file.parent.parent.name in STATUS_MAP:
            key    = md_file.parent.name
            folder = md_file.parent.parent.name
        else:
            continue
        if args.check_existing:
            done = process_file(
                md_file, project_root, cr_dir,
                step_instructions_base, args.claude_command,
                args.codex_command, step_agent_map,
            )
            if done:
                processed[key] = (folder, time.time())
        else:
            processed[key] = (folder, time.time())

    claude_steps_display = args.claude_steps.replace(",", ", ")
    codex_steps_display  = args.codex_steps.replace(",", ", ")
    print(f"\n{C.GREEN}変更依頼フォルダを監視中: {cr_dir}{C.RESET}")
    print(f"{C.GREEN}  Claude → {claude_steps_display}{C.RESET}")
    print(f"{C.MAGENTA}  Codex  → {codex_steps_display}{C.RESET}")
    print(f"{C.YELLOW}  _person → 通知のみ{C.RESET}")
    print(f"{C.GRAY}  ※ 1件ずつ処理（処理中の依頼がある場合は次の依頼は自動待機）{C.RESET}")
    print(f"{C.GRAY}終了: Ctrl+C{C.RESET}\n")

    try:
        while True:
            for md_file in cr_dir.rglob("ChangeRequest.md"):
                if md_file.parent.name in STATUS_MAP:
                    key    = md_file.stem
                    folder = md_file.parent.name
                elif md_file.parent.parent.name in STATUS_MAP:
                    key    = md_file.parent.name
                    folder = md_file.parent.parent.name
                else:
                    continue
                cached = processed.get(key)
                # 未処理 / フォルダが変わった / タイムアウトでリトライ の3条件でトリガー
                is_new_folder  = cached is None or cached[0] != folder
                is_timed_out   = (not is_new_folder) and (time.time() - cached[1] > args.retry_timeout)
                if is_new_folder or is_timed_out:
                    if is_timed_out:
                        elapsed = int(time.time() - cached[1])
                        print(f"\n{C.YELLOW}[リトライ] {key} が {elapsed // 60} 分間 {folder} に留まっているため再起動します{C.RESET}")
                    done = process_file(
                        md_file, project_root, cr_dir,
                        step_instructions_base, args.claude_command,
                        args.codex_command, step_agent_map,
                    )
                    if done:
                        processed[key] = (folder, time.time())
            time.sleep(args.poll_interval)
    except KeyboardInterrupt:
        print(f"\n{C.YELLOW}監視を終了しました。{C.RESET}")


if __name__ == "__main__":
    main()
