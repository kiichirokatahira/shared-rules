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

| フェーズ | 担当 | 参照ファイル |
|---|---|---|
| Phase 1–2: 要件定義・仕様確定 | Claude Planner | `docs/change-requests/` → `docs/SPEC.md` |
| Phase 3: 実装 | Claude Coder / Codex | `docs/SPEC.md` |
| Phase 4: テスト | Claude DevOps / Codex | `docs/SPEC.md`, `docs/test-specs/` |
| Phase 5: レビュー | Claude Reviewer | `docs/SPEC.md`, フィーチャーブランチ diff |
| Phase 6: CI + 統合 | GitHub Actions + 人間 | — |

役割別の詳細指示: `docs/claude-sessions/` ディレクトリを参照してください。

## ブランチ戦略

- `main` / `develop`: 保護ブランチ。**直接コミット・プッシュ禁止**
- `feature/ai-YYYYMMDD-xxxx`: AI 作業ブランチ（必ずこのブランチで作業する）

## 重要ファイル・ディレクトリ

| パス | 用途 |
|---|---|
| `docs/SPEC.md` | 現在の機能仕様書（Claude Planner が作成・更新） |
| `docs/change-requests/` | 変更依頼ファイル |
| `docs/test-specs/` | テスト仕様書・受け入れ基準 |
| `test-results/` | テスト結果サマリー（git 管理） |
| `.claude/settings.json` | Claude Code 権限・フック設定 |

## Claude への制約

- `main` / `develop` への直接コミットは**禁止**
- `rm -rf`、`git push --force`、`git reset --hard` は実行前に**必ず確認する**
- 実装は必ず `feature/ai-YYYYMMDD-xxxx` ブランチで行う
- セキュリティ上の懸念（OWASP Top 10 等）は実装前に報告する
- 仕様が不明確な場合は実装を止めて `docs/SPEC.md` の `## 確認事項` に質問を記載する
