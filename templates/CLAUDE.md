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

## AI 駆動開発ワークフロー

このプロジェクトは以下のワークフローで開発します。各フェーズは専用セッションで実行します。

各変更依頼は **`YYYY-MM-DD-xxxx/` サブフォルダ**単位で管理します。
フォルダの中に依頼書・テスト結果・ログを格納し、フォルダごと次のステップへ移動します。

```
change-requests/
  {step_folder}/
    YYYY-MM-DD-xxxx/          ← 変更依頼フォルダ（フォルダごと移動）
      change-request.md       ← 依頼書（常に存在）
      test-results.md         ← テスト結果（Step 070 で作成）
      logs/                   ← AI セッションログ（各ステップで保存）
        020_planning_ai.md
        ...
```

| ステップ | 担当 | 変更依頼フォルダの移動先 | 参照ファイル |
|---|---|---|---|
| 010: 変更依頼作成 | 人間（Planning Mode） | `010_backlog_person/` → `020` | — |
| 020: 依頼明確化・仕様策定 | AI | → `040_planning_check_ai/`（質問あり→`010`） | `change-request.md`（仕様書追記） |
| 040: 仕様書精査 | AI | → `050_implementation_ai/`（質問あり→`020`） | `change-request.md` |
| 050: 実装 | AI | → `070_testing_ai/` | `change-request.md` |
| 070: テスト実行 | AI | → `080_review_ai/` | `change-request.md` → `test-results.md` 作成 |
| 080: テスト結果レビュー | AI | → `090_test_person/`（問題あり→`070`） | `test-results.md` |
| 090: 動作確認 | 人間 | → `100_docs_ai/`（問題あり→`020`） | `change-request.md` |
| 100: ドキュメント更新 | AI | → `110_pr_ai/` | `change-request.md` |
| 110: PR 作成 | AI | → `120_done_person/` | `change-request.md` |
| 120: マージ | 人間 | — | — |

ステップ別の詳細指示: `x20_変更依頼/step-instructions/` ディレクトリを参照してください。
変更依頼のフォルダ名と指示ファイル名が 1:1 対応しています（例: `020_planning_ai/` → `step-instructions/020_planning_ai.md`）。

### 変更依頼ステータス一覧の確認

全変更依頼のステータスをまとめた表を出力するには以下を実行してください:

```bash
# ターミナルに表示
python scripts/list-change-requests.py

# ファイルに保存
python scripts/list-change-requests.py --output-file x20_変更依頼/STATUS.md
```

### 変更依頼フォルダの自動監視

`x20_変更依頼/change-requests/` を監視し、`_ai` フォルダに変更依頼フォルダが届いた時点で
**変更依頼ごとに git worktree + ブランチを自動作成**してエージェントを起動します:

```bash
# 監視開始（起動中はターミナルを開いたままにしてください）
python scripts/watch-change-requests.py

# 起動時に既存ファイルも処理する場合
python scripts/watch-change-requests.py --check-existing

# どの AI が各ステップを担当するかをカスタマイズする場合
python scripts/watch-change-requests.py \
  --claude-steps "020_planning_ai,080_review_ai,100_docs_ai,110_pr_ai" \
  --codex-steps  "040_planning_check_ai,050_implementation_ai,070_testing_ai"
```

| フォルダ種別 | 動作 |
|---|---|
| `_ai` | worktree 作成 → 担当 AI を自動起動（デフォルト割り当てはスクリプトのパラメータで制御） |
| `_person` | 通知メッセージを表示（人間待ち） |

デフォルトの AI 割り当て:

| ステップ | デフォルト担当 |
|---|---|
| 020_planning_ai | Claude |
| 040_planning_check_ai | Codex |
| 050_implementation_ai | Codex |
| 070_testing_ai | Codex |
| 080_review_ai | Claude |
| 100_docs_ai | Claude |
| 110_pr_ai | Claude |

変更依頼フォルダを次のステップへ移動するだけで、独立した worktree 上でエージェントが動き出します。
複数の変更依頼が並行していても物理フォルダが独立するため、ブランチ切り替えや競合は起きません。

## ブランチ戦略

### worktree による並行開発

各変更依頼は **独立した git worktree** 上で作業します。
`watch-change-requests.py` が自動で worktree とブランチを作成します。

```
[プロジェクト root]/          ← main / develop（変更依頼ファイルの置き場）
../[project]-YYYY-MM-DD-A/   ← feature/ai-YYYY-MM-DD-A  ← エージェントAの作業場所
../[project]-YYYY-MM-DD-B/   ← feature/ai-YYYY-MM-DD-B  ← エージェントBの作業場所
```

- 各 worktree は物理的に独立したフォルダなので、ブランチ切り替えが不要
- 複数エージェントが同時に別ブランチで作業しても互いに干渉しない
- `main` / `develop` は変更依頼ファイルの管理のみに使い、コードは変更しない

### ブランチ命名規則

- `main` / `develop`: 保護ブランチ。**直接コミット・プッシュ禁止**
- `feature/ai-YYYY-MM-DD-xxxx`: 変更依頼ごとの AI 作業ブランチ（worktree と 1:1 対応）

### worktree のライフサイクル

```powershell
# マージ完了後の削除
git worktree remove ../[project]-YYYY-MM-DD-xxxx
git branch -d feature/ai-YYYY-MM-DD-xxxx
```

## 重要ファイル・ディレクトリ

| パス | 用途 |
|---|---|
| `x20_変更依頼/change-requests/010_backlog_person/` | Step 010: 草案・未着手（Planning Mode で精査） |
| `x20_変更依頼/change-requests/020_planning_ai/` | Step 020: AI が仕様策定中 |
| `x20_変更依頼/change-requests/040_planning_check_ai/` | Step 040: AI が仕様精査中 |
| `x20_変更依頼/change-requests/050_implementation_ai/` | Step 050: AI が実装中 |
| `x20_変更依頼/change-requests/070_testing_ai/` | Step 070: AI がテスト中 |
| `x20_変更依頼/change-requests/080_review_ai/` | Step 080: AI がテスト結果レビュー中 |
| `x20_変更依頼/change-requests/090_test_person/` | Step 090: 人間が動作確認中 |
| `x20_変更依頼/change-requests/100_docs_ai/` | Step 100: AI がドキュメント更新中 |
| `x20_変更依頼/change-requests/110_pr_ai/` | Step 110: AI が PR 作成中 |
| `x20_変更依頼/change-requests/120_done_person/` | Step 120: 人間が PR 確認・マージ待ち |
| `x20_変更依頼/step-instructions/` | ステップ別 AI 指示（フォルダ名と 1:1 対応） |
| `.claude/settings.json` | Claude Code 権限・フック設定 |

変更依頼フォルダの内部構造（各 CR フォルダ共通）:

| パス（CR フォルダ内） | 用途 |
|---|---|
| `change-request.md` | 依頼書・仕様書（必須） |
| `test-results.md` | テスト結果サマリー（Step 070 で作成） |
| `logs/020_planning_ai.md` | Step 020 AI セッションログ（推奨） |
| `logs/040_planning_check_ai.md` | Step 040 AI セッションログ（推奨） |
| `logs/070_testing_ai.md` | Step 070 AI セッションログ（推奨） |
| `logs/080_review_ai.md` | Step 080 AI セッションログ（推奨） |

## Claude への制約

- `main` / `develop` への直接コミットは**禁止**
- `rm -rf`、`git push --force`、`git reset --hard` は実行前に**必ず確認する**
- 実装は必ず割り当てられた worktree（`feature/ai-YYYY-MM-DD-xxxx` ブランチ）で行う
- **他の worktree のファイルを変更しない**（並行作業中の別変更依頼への干渉を防ぐ）
- セキュリティ上の懸念（OWASP Top 10 等）は実装前に報告する
- 仕様が不明確な場合は実装を止めて仕様書の `## 確認事項` に質問を記載する
