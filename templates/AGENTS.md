# Codex エージェント指示

このファイルはリポジトリ直下に配置し、Codex が参照するコンテキストを提供します。
（グローバルスコープ `~/.codex/` の読み込みバグがあるため、リポジトリ直下を優先する）

## コーディング規約

- インデント: スペース 2 つ（SQL は 4 スペース）
- 1 行最大: 120 文字
- ファイル末尾: 改行 1 つ
- コメント: 「なぜそうするか」を記述（何をするかは不要）
- 命名: 変数・関数は camelCase / クラス・型は PascalCase / 定数は UPPER_SNAKE_CASE / ファイル名は kebab-case

## 禁止操作

- `main` / `develop` への直接コミット・プッシュ禁止
- `git push --force`（`main`/`develop` に対して）禁止
- `rm -rf` の無確認実行禁止
- TypeScript の `any` 型使用禁止（やむを得ない場合は理由をコメントに記載）
- SQL の `SELECT *` 禁止（カラム名を明示する）
- Fabric SQL analytics endpoint へのテーブル `CREATE TABLE` / `ALTER TABLE` / `DROP TABLE` 直接実行禁止
- テーブル `CREATE TABLE` 文は Pipeline 用成果物へ変換する

## ブランチ操作

1. 作業開始前に `ai-YYYYMMDD-xxxx` ブランチを作成する
2. すべての変更は作業ブランチにコミットする
3. 完了後は作業ブランチにプッシュする（マージは人間が行う）

## テスト実行コマンド

```shell
# TODO: プロジェクトに合わせて変更してください
npm test              # 単体テスト
npm run test:e2e      # E2E テスト
npm run lint          # Lint チェック
```

## テスト成果物の保存先

| 種類 | 保存先 |
|---|---|
| テスト結果サマリー（合否・件数） | `test-results/` に git コミット |
| HTML / XML 詳細レポート | CI アーティファクト（git に含めない） |

## 参照仕様

実装前に必ず `docs/SPEC.md` を読み、完了条件・スコープ外を確認してください。
スコープ外のファイルは変更しないでください。
