# Shared Rules — このリポジトリについて

このリポジトリは複数の git リポジトリで共通利用するルールを一元管理します。
各リポジトリの `CLAUDE.md` からこのリポジトリのルールファイルを参照・インポートしてください。

## ルールファイル一覧

| ファイル | 内容 |
|---|---|
| [rules/folder-structure.md](rules/folder-structure.md) | フォルダ構成の規約 |
| [rules/code-conventions.md](rules/code-conventions.md) | コーディング規約 |
| [rules/external-connections.md](rules/external-connections.md) | 外部システム接続ルール |
| [rules/git-workflow.md](rules/git-workflow.md) | Git 運用ルール |

## 参照先リポジトリへの導入方法

各リポジトリの `CLAUDE.md` に以下を追記してください:

```markdown
<!-- shared-rules の絶対パスは環境に合わせて変更してください -->
@/path/to/shared-rules/rules/folder-structure.md
@/path/to/shared-rules/rules/code-conventions.md
@/path/to/shared-rules/rules/external-connections.md
@/path/to/shared-rules/rules/git-workflow.md
```

> Claude Code の `@file` import 構文を使うことで、このリポジトリのルールを
> 参照先リポジトリのコンテキストに自動で取り込めます。

## AI 駆動開発ワークフロー用テンプレート

`templates/` ディレクトリに AI 駆動開発ワークフロー（Structure.md）の雛形ファイルを格納しています。
新規プロジェクトのセットアップ時にコピーして使用してください。

| ファイル | 用途 | コピー先 |
|---|---|---|
| [templates/CLAUDE.md](templates/CLAUDE.md) | プロジェクト用 Claude Code 指示 | `<project>/CLAUDE.md` |
| [templates/AGENTS.md](templates/AGENTS.md) | Codex 用指示 | `<project>/AGENTS.md` |
| [templates/claude-sessions/planner.md](templates/claude-sessions/planner.md) | Planner セッション指示 | `<project>/docs/claude-sessions/planner.md` |
| [templates/claude-sessions/coder.md](templates/claude-sessions/coder.md) | Coder セッション指示 | `<project>/docs/claude-sessions/coder.md` |
| [templates/claude-sessions/devops.md](templates/claude-sessions/devops.md) | DevOps セッション指示 | `<project>/docs/claude-sessions/devops.md` |
| [templates/claude-sessions/reviewer.md](templates/claude-sessions/reviewer.md) | Reviewer セッション指示 | `<project>/docs/claude-sessions/reviewer.md` |
| [templates/docs/SPEC.md](templates/docs/SPEC.md) | 機能仕様書テンプレート | `<project>/docs/SPEC.md` |
| [templates/docs/change-request.md](templates/docs/change-request.md) | 変更依頼テンプレート | `<project>/docs/change-requests/YYYY-MM-DD-xxxx.md` |

### 役割別セッションの起動方法

各 Claude セッション開始時に対応する指示ファイルを最初のメッセージで提示してください：

```
@docs/claude-sessions/planner.md
変更依頼 docs/change-requests/2026-06-03-xxxx.md を読んで SPEC.md を作成してください。
```
