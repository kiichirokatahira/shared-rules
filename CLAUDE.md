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

**`<project>`（コードリポジトリ）へコピーするファイル:**

| ファイル | 用途 | コピー先 |
|---|---|---|
| [templates/CLAUDE.md.template](templates/CLAUDE.md.template) | プロジェクト用 Claude Code 指示 | `<project>/CLAUDE.md` |
| [templates/AGENTS.md](templates/AGENTS.md) | Codex 用指示 | `<project>/AGENTS.md` |
| [templates/scripts/list-change-requests.py](templates/scripts/list-change-requests.py) | 変更依頼のステータス一覧を表形式で出力するスクリプト | `<project>/scripts/list-change-requests.py` |
| [templates/scripts/watch-change-requests.py](templates/scripts/watch-change-requests.py) | change-requests フォルダを監視し `_ai` フォルダへの変更依頼フォルダ移動で自動起動するスクリプト | `<project>/scripts/watch-change-requests.py` |
| [templates/SETUP.md](templates/SETUP.md) | Claude Code・Codex のインストール手順（事前準備ガイド） | `<project>/SETUP.md` |
| [templates/x30_仕様書/index.md](templates/x30_仕様書/index.md) | 仕様書フォルダ インデックスノート（Obsidian MOC） | `<project>/x30_仕様書/index.md` |
| [templates/x30_仕様書/CORE_XX/spec-template.md](templates/x30_仕様書/CORE_XX/spec-template.md) | 仕様書テンプレート（Obsidian frontmatter 付き） | `<project>/x30_仕様書/CORE_XX/<name>.md` |

**`<project-cr>`（変更依頼リポジトリ）へコピーするファイル:**

| ファイル | 用途 | コピー先 |
|---|---|---|
| [templates/step-instructions/010_backlog_person.md](templates/step-instructions/010_backlog_person.md) | Step 010 変更依頼作成手順（Planning Mode） | `<project-cr>/step-instructions/010_backlog_person.md` |
| [templates/step-instructions/020_planning_ai.md](templates/step-instructions/020_planning_ai.md) | Step 020 依頼明確化・仕様策定の指示 | `<project-cr>/step-instructions/020_planning_ai.md` |
| [templates/step-instructions/050_implementation_ai.md](templates/step-instructions/050_implementation_ai.md) | Step 050 実装の指示 | `<project-cr>/step-instructions/050_implementation_ai.md` |
| [templates/step-instructions/055_code_review_ai.md](templates/step-instructions/055_code_review_ai.md) | Step 055 コードレビューの指示 | `<project-cr>/step-instructions/055_code_review_ai.md` |
| [templates/step-instructions/060_infra_person.md](templates/step-instructions/060_infra_person.md) | Step 060 インフラ事前作業の指示 | `<project-cr>/step-instructions/060_infra_person.md` |
| [templates/step-instructions/070_testing_ai.md](templates/step-instructions/070_testing_ai.md) | Step 070 テスト実行の指示 | `<project-cr>/step-instructions/070_testing_ai.md` |
| [templates/step-instructions/080_review_ai.md](templates/step-instructions/080_review_ai.md) | Step 080 テスト結果レビューの指示 | `<project-cr>/step-instructions/080_review_ai.md` |
| [templates/step-instructions/090_test_person.md](templates/step-instructions/090_test_person.md) | Step 090 動作確認手順 | `<project-cr>/step-instructions/090_test_person.md` |
| [templates/step-instructions/100_docs_ai.md](templates/step-instructions/100_docs_ai.md) | Step 100 ドキュメント更新の指示 | `<project-cr>/step-instructions/100_docs_ai.md` |
| [templates/step-instructions/110_pr_ai.md](templates/step-instructions/110_pr_ai.md) | Step 110 PR 作成の指示 | `<project-cr>/step-instructions/110_pr_ai.md` |
| [templates/ChangeRequest.md](templates/ChangeRequest.md) | 変更依頼テンプレート | `<project-cr>/ChangeRequest.md` |
| [templates/change-requests/](templates/change-requests/) | 変更依頼ステップフォルダ Step 010〜120（`_person`/`_ai` で担当を表示） | `<project-cr>/change-requests/` にコピー |

### ステップ別セッションの起動方法

各 Claude セッション開始時に、変更依頼が置かれているフォルダと同名の指示ファイルを提示してください：

```
@step-instructions/020_planning_ai.md
変更依頼 change-requests/020_planning_ai/20260603-xxxx/ChangeRequest.md を読んで仕様書を作成してください。
```

フォルダと指示ファイルが 1:1 対応しているため、変更依頼の現在地から参照する指示ファイルが一目で分かります。
