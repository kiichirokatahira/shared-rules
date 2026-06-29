# [プロジェクト名] — Claude Code コンテキスト

## 共通ルール（shared-rules）

<!-- shared-rules の絶対パスは環境に合わせて変更してください -->
@C:/path/to/shared-rules/rules/folder-structure.md
@C:/path/to/shared-rules/rules/code-conventions.md
@C:/path/to/shared-rules/rules/external-connections.md
@C:/path/to/shared-rules/rules/git-workflow.md

## プロジェクト概要

（このプロジェクトの目的・概要を記載してください）

## 技術スタック

- 言語：
- フレームワーク：
- データベース：
- CI/CD：

## Fabric テーブル作成の扱い

Microsoft Fabric の SQL analytics endpoint ではテーブル作成 DDL を直接実行しません。
`CREATE TABLE` 文を扱う変更依頼では、スコープ内のすべてのテーブル定義を Pipeline 用成果物へ変換し、
Step 060 で Pipeline のインポート・接続設定・実行確認を行います。

## AI 駆動開発ワークフロー

このプロジェクトは以下のワークフローで開発します。各フェーズは専用セッションで実行します。

### リポジトリ構成（2リポジトリ推奨）

変更依頼・仕様書はコードとは**別リポジトリ**で管理します。

```
[project-repo]/         ← コードリポジトリ（このリポジトリ）
  src/
  x30_仕様書/           ← 仕様書（コードと同じリポジトリで管理）
  CLAUDE.md
  scripts/              ← watch / list スクリプト
  ...

[project-cr-repo]/      ← 変更依頼リポジトリ（常に main で管理）
  change-requests/
  step-instructions/
```

- **project-repo**: コード＋仕様書。`ai-YYYYMMDD-xxxx` ブランチで変更管理
- **project-cr-repo**: 変更依頼のみ。ブランチを切らず常に `main` に直接コミット

> watch スクリプトはプロジェクトリポジトリのルートから起動します。  
> `--cr-repo` で変更依頼リポジトリのパスを渡すと、2つのリポジトリを跨いで動作します。

各変更依頼は **`YYYYMMDD-xxxx/` サブフォルダ**単位で管理します。
フォルダの中に依頼書・テスト結果・ログを格納し、フォルダごと次のステップへ移動します。

```
change-requests/
  {step_folder}/
    YYYYMMDD-xxxx/          ← 変更依頼フォルダ（フォルダごと移動）
      ChangeRequest.md       ← 依頼書（常に存在）
      test-results.md         ← テスト結果（Step 070 で作成）
      logs/                   ← AI セッションログ（各ステップで保存）
        020_planning_ai.md
        ...
```

| ステップ | 担当 | 変更依頼フォルダの移動先 | 参照ファイル |
|---|---|---|---|
| 010: 変更依頼作成 | 人間（Planning Mode） | `010_backlog_person/` → `020` | — |
| 020: 依頼明確化・仕様策定 | AI | → `050_implementation_ai/`（質問あり→`010`） | `ChangeRequest.md`（仕様書追記） |
| 050: 実装 | AI | → `055_code_review_ai/`（055 からの戻りも同フォルダ） | `ChangeRequest.md` |
| 055: コードレビュー | AI | → `060_infra_person/`（問題あり→`050`） | `ChangeRequest.md` |
| 060: インフラ事前作業 | 人間 | → `070_testing_ai/` | `ChangeRequest.md` |
| 070: テスト実行 | AI | → `080_review_ai/` | `ChangeRequest.md` → `test-results.md` 作成 |
| 080: テスト結果レビュー | AI | → `090_test_person/`（問題あり→`070`） | `test-results.md` |
| 090: 動作確認 | 人間 | → `100_docs_ai/`（実装バグ→`050`、仕様不備→`020`） | `ChangeRequest.md` |
| 100: ドキュメント更新 | AI | → `110_pr_ai/` | `ChangeRequest.md` |
| 110: PR 作成 | AI | → `120_done_person/` | `ChangeRequest.md` |
| 120: マージ | 人間 | — | — |

ステップ別の詳細指示: `step-instructions/` ディレクトリを参照してください。
変更依頼のフォルダ名と指示ファイル名が 1:1 対応しています（例: `020_planning_ai/` → `step-instructions/020_planning_ai.md`）。

### 変更依頼ステータス一覧の確認

全変更依頼のステータスをまとめた表を出力するには以下を実行してください:

```bash
# ターミナルに表示（CR リポジトリが別の場合）
python scripts/list-change-requests.py --cr-repo ../myproject-cr

# ファイルに保存
python scripts/list-change-requests.py --cr-repo ../myproject-cr --output-file ../myproject-cr/STATUS.md
```

### 変更依頼フォルダの自動監視

CR リポジトリの `change-requests/` を監視し、`_ai` フォルダに変更依頼フォルダが届いた時点で
エージェントを**プロジェクトリポジトリのルート**で起動します。**1件ずつ処理**するため、処理中の変更依頼（020〜110 のステップ）がある場合、次の変更依頼は自動待機し、完了後に自動起動します:

```bash
# 監視開始（CR リポジトリが別の場合）
python scripts/watch-change-requests.py --cr-repo ../myproject-cr

# 起動時に既存ファイルも処理する場合
python scripts/watch-change-requests.py --cr-repo ../myproject-cr --check-existing

# どの AI が各ステップを担当するかをカスタマイズする場合
python scripts/watch-change-requests.py --cr-repo ../myproject-cr \
  --claude-steps "020_planning_ai,055_code_review_ai,080_review_ai,100_docs_ai,110_pr_ai" \
  --codex-steps  "050_implementation_ai,070_testing_ai"
```

| フォルダ種別 | 動作 |
|---|---|
| `_ai` | 担当 AI を自動起動（処理中の依頼がある場合は待機、完了後に自動起動） |
| `_person` | 通知メッセージを表示（人間待ち） |

デフォルトの AI 割り当て:

| ステップ | デフォルト担当 |
|---|---|
| 020_planning_ai | Claude |
| 050_implementation_ai | Codex |
| 055_code_review_ai | Claude |
| 070_testing_ai | Codex |
| 080_review_ai | Claude |
| 100_docs_ai | Claude |
| 110_pr_ai | Claude |

変更依頼フォルダを次のステップへ移動するだけでエージェントが動き出します。
020〜110 には常に1件のみ存在するため、ブランチ競合やコード干渉は起きません。

## ブランチ戦略

### 1件ずつ処理による直列開発

変更依頼は **1件ずつ**処理します。エージェントはプロジェクトリポジトリのルートで直接作業し、git worktree は使用しません。

```
[project-repo]/               ← エージェントの作業場所（cwd）
  main / develop              ← PR マージ先
  ai-YYYYMMDD-xxxx            ← 処理中の変更依頼用ブランチ（1本のみ）

[project-cr-repo]/            ← 変更依頼・仕様書の置き場
  main                        ← 常にここへ直接コミット（ブランチを切らない）
```

- Step 050 でエージェントが project-repo に `ai-YYYYMMDD-xxxx` ブランチを作成・チェックアウト
- Step 050〜110 の間はこのブランチでコード変更が続く
- CR ファイル（ChangeRequest.md、test-results.md、x30_仕様書/）は project-cr-repo の main に直接コミット
- 次の変更依頼は前の変更依頼が 120_done_person（マージ待ち）に移動してから開始

### ブランチ命名規則

- project-repo の `main` / `develop`: 保護ブランチ。**直接コミット・プッシュ禁止**
- project-repo の `ai-YYYYMMDD-xxxx`: 変更依頼ごとの AI 作業ブランチ（同時に1本のみ）
- project-cr-repo は常に `main` へ直接コミット（ブランチ不使用）

### マージ後のクリーンアップ（Step 120 完了時）

```powershell
# project-repo: PR マージ後にブランチを削除して main に戻す
git checkout main
git pull
git branch -d ai-YYYYMMDD-xxxx
```

## 重要ファイル・ディレクトリ

### project-cr-repo（変更依頼リポジトリ）

| パス | 用途 |
|---|---|
| `change-requests/010_backlog_person/` | Step 010: 草案・未着手（Planning Mode で精査） |
| `change-requests/020_planning_ai/` | Step 020: AI が仕様策定中 |
| `change-requests/050_implementation_ai/` | Step 050: AI が実装中 |
| `change-requests/055_code_review_ai/` | Step 055: AI がコードレビュー中 |
| `change-requests/060_infra_person/` | Step 060: 人間がインフラ事前作業中 |
| `change-requests/070_testing_ai/` | Step 070: AI がテスト中 |
| `change-requests/080_review_ai/` | Step 080: AI がテスト結果レビュー中 |
| `change-requests/090_test_person/` | Step 090: 人間が動作確認中 |
| `change-requests/100_docs_ai/` | Step 100: AI がドキュメント更新中 |
| `change-requests/110_pr_ai/` | Step 110: AI が PR 作成中 |
| `change-requests/120_done_person/` | Step 120: 人間が PR 確認・マージ待ち |
| `step-instructions/` | ステップ別 AI 指示（フォルダ名と 1:1 対応） |

### project-repo（コードリポジトリ、このリポジトリ）

| パス | 用途 |
|---|---|
| `x30_仕様書/` | 仕様書（Obsidian で管理） |
| `scripts/watch-change-requests.py` | 変更依頼フォルダ監視スクリプト |
| `scripts/list-change-requests.py` | 変更依頼ステータス一覧スクリプト |
| `.claude/settings.json` | Claude Code 権限・フック設定 |

変更依頼フォルダの内部構造（各 CR フォルダ共通）:

| パス（CR フォルダ内） | 用途 |
|---|---|
| `ChangeRequest.md` | 依頼書・仕様書（必須） |
| `test-results.md` | テスト結果サマリー（Step 070 で作成） |
| `logs/020_planning_ai.md` | Step 020 AI セッションログ（推奨） |
| `logs/055_code_review_ai.md` | Step 055 AI セッションログ（推奨） |
| `logs/070_testing_ai.md` | Step 070 AI セッションログ（推奨） |
| `logs/080_review_ai.md` | Step 080 AI セッションログ（推奨） |

## Claude への制約

- **project-repo**: `main` / `develop` への直接コミットは**禁止**
- **project-repo**: コード変更は必ず `ai-YYYYMMDD-xxxx` ブランチで行う（Step 050 でブランチを作成・チェックアウト）
- **project-repo**: ブランチの切り替えは Step 050 のみ。それ以外のステップでは既存ブランチを維持する
- **project-cr-repo**: ブランチを切らず、常に `main` へ直接コミットする
- `rm -rf`、`git push --force`、`git reset --hard` は実行前に**必ず確認する**
- セキュリティ上の懸念（OWASP Top 10 等）は実装前に報告する
- 仕様が不明確な場合は実装を止めて仕様書の `## 確認事項` に質問を記載する
