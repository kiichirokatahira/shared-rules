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

| ステップ | 担当 | 変更依頼の移動先 | 参照ファイル |
|---|---|---|---|
| 010: 変更依頼 | 人間 | `010_backlog_person/` | — |
| 020: 依頼明確化・仕様策定 | Claude Planner | → `020_planning_claude/` | `docs/specs/YYYY-MM-DD-xxxx.md` 作成 |
| 030: 質問への回答 | 人間 | → `030_planning_confirmation_person/` (→ `020` に戻す) | — |
| 040: 仕様書精査 | Codex | → `040_planning_check_codex/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 050: 実装 | Codex | → `050_implementation_codex/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 060: 実装レビュー | Claude Reviewer | → `060_implementation_claude/` | `docs/specs/YYYY-MM-DD-xxxx.md`, diff |
| 070: テスト実行 | Codex | → `070_testing_codex/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 080: テスト結果レビュー | Claude Reviewer | → `080_review_claude/` | `test-results/` |
| 090: 動作確認 | 人間 | → `090_test_person/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 100: ドキュメント更新 | Claude | → `100_docs_claude/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 110: PR 作成 | Claude | → `110_pr_claude/` | `docs/specs/YYYY-MM-DD-xxxx.md` |
| 120: マージ | 人間 | → `120_done_person/` | — |

ステップ別の詳細指示: `x20_変更依頼/step-instructions/` ディレクトリを参照してください。
変更依頼のフォルダ名と指示ファイル名が 1:1 対応しています（例: `020_planning_claude/` → `step-instructions/020_planning_claude.md`）。

### 変更依頼ステータス一覧の確認

全変更依頼のステータスをまとめた表を出力するには以下を実行してください:

```bash
# ターミナルに表示
python scripts/list-change-requests.py

# ファイルに保存
python scripts/list-change-requests.py --output-file x20_変更依頼/STATUS.md
```

### 変更依頼フォルダの自動監視

`x20_変更依頼/change-requests/` を監視し、`_claude` / `_codex` フォルダにファイルが届いた時点で
**変更依頼ごとに git worktree + ブランチを自動作成**してエージェントを起動します:

```bash
# 監視開始（起動中はターミナルを開いたままにしてください）
python scripts/watch-change-requests.py

# 起動時に既存ファイルも処理する場合
python scripts/watch-change-requests.py --check-existing
```

| フォルダ種別 | 動作 |
|---|---|
| `_claude` | worktree 作成 → Claude Code を自動起動 |
| `_codex` | worktree 作成 → Codex を自動起動 |
| `_person` | 通知メッセージを表示（人間待ち） |

変更依頼ファイルを次のフォルダへ移動するだけで、独立した worktree 上でエージェントが動き出します。
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
| `docs/specs/` | 変更依頼ごとの仕様書（Claude Planner が作成） |
| `x20_変更依頼/change-requests/010_backlog_person/` | Step 010: 草案・未着手 |
| `x20_変更依頼/change-requests/020_planning_claude/` | Step 020: Claude Planner が仕様策定中 |
| `x20_変更依頼/change-requests/030_planning_confirmation_person/` | Step 030: 人間が質問に回答待ち |
| `x20_変更依頼/change-requests/040_planning_check_codex/` | Step 040: Codex が仕様精査中 |
| `x20_変更依頼/change-requests/050_implementation_codex/` | Step 050: Codex が実装中 |
| `x20_変更依頼/change-requests/060_implementation_claude/` | Step 060: Claude が実装レビュー中 |
| `x20_変更依頼/change-requests/070_testing_codex/` | Step 070: Codex がテスト中 |
| `x20_変更依頼/change-requests/080_review_claude/` | Step 080: Claude がテスト結果レビュー中 |
| `x20_変更依頼/change-requests/090_test_person/` | Step 090: 人間が動作確認中 |
| `x20_変更依頼/change-requests/100_docs_claude/` | Step 100: Claude がドキュメント更新中 |
| `x20_変更依頼/change-requests/110_pr_claude/` | Step 110: Claude が PR 作成中 |
| `x20_変更依頼/change-requests/120_done_person/` | Step 120: 人間が PR 確認・マージ待ち |
| `x20_変更依頼/step-instructions/` | ステップ別 Claude/Codex 指示（フォルダ名と 1:1 対応） |
| `test-results/` | テスト結果サマリー（git 管理） |
| `.claude/settings.json` | Claude Code 権限・フック設定 |

## Claude への制約

- `main` / `develop` への直接コミットは**禁止**
- `rm -rf`、`git push --force`、`git reset --hard` は実行前に**必ず確認する**
- 実装は必ず割り当てられた worktree（`feature/ai-YYYY-MM-DD-xxxx` ブランチ）で行う
- **他の worktree のファイルを変更しない**（並行作業中の別変更依頼への干渉を防ぐ）
- セキュリティ上の懸念（OWASP Top 10 等）は実装前に報告する
- 仕様が不明確な場合は実装を止めて仕様書の `## 確認事項` に質問を記載する
