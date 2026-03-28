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
