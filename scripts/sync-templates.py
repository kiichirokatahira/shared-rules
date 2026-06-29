#!/usr/bin/env python3
# shared-rules の scripts/ と step-instructions/ を各リポジトリへ同期するスクリプト
# 使い方: python scripts/sync-templates.py

import shutil
import sys
from pathlib import Path

shared_rules_root = Path(__file__).parent.parent

# 同期対象リポジトリのリスト（環境に合わせて追加・編集してください）
target_repos = [
    Path("C:/Users/kiichiro.katahira.AD/OneDrive - AVANT GROUP/git/ag-groupit-dwh-azurefunction"),
    Path("C:/Users/kiichiro.katahira.AD/OneDrive - AVANT GROUP/git/ag-groupit-dwh-fabric-it"),
]

source_scripts_dir = shared_rules_root / "templates/scripts"
source_step_instructions_dir = shared_rules_root / "templates/step-instructions"

for repo in target_repos:
    if not repo.exists():
        print(f"警告: リポジトリが見つかりません: {repo}", file=sys.stderr)
        continue

    # scripts/ の同期
    dest_scripts_dir = repo / "scripts"
    dest_scripts_dir.mkdir(parents=True, exist_ok=True)
    for file in source_scripts_dir.iterdir():
        if file.is_file():
            shutil.copy2(file, dest_scripts_dir / file.name)
            print(f"  コピー: {file.name} -> {repo}/scripts/")

    # step-instructions/ の同期
    dest_step_instructions_dir = repo / "step-instructions"
    dest_step_instructions_dir.mkdir(parents=True, exist_ok=True)
    for file in source_step_instructions_dir.iterdir():
        if file.is_file():
            shutil.copy2(file, dest_step_instructions_dir / file.name)
            print(f"  コピー: {file.name} -> {repo}/step-instructions/")

    print(f"[完了] {repo}")

print()
print("同期完了。")
