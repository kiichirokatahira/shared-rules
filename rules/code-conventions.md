# コーディング規約

## 共通ルール（言語問わず）

- インデントは **スペース 2 つ**（YAML/Python は例外あり）
- 1 行の最大文字数は **120 文字**
- ファイル末尾には必ず**改行を 1 つ**入れる
- コメントは「何をするか」でなく「**なぜそうするか**」を書く
- マジックナンバーは必ず**定数として定義**する

## 命名規則

| 対象 | 規則 | 例 |
|---|---|---|
| 変数・関数 | camelCase | `getUserName()` |
| クラス・型 | PascalCase | `UserProfile` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| ファイル名 | kebab-case | `user-profile.ts` |
| DB カラム | snake_case | `created_at` |

## TypeScript / JavaScript

- `any` 型の使用は禁止（やむを得ない場合は `// eslint-disable` コメントと理由を記載）
- `null` より `undefined` を優先する
- 非同期処理は `async/await` を使用し、`.then()` チェーンは避ける

## Python

- 型ヒントを必ず付ける
- Docstring は Google スタイルで記述する
- `import *` は禁止

## コードレビュー基準

1. セキュリティ（OWASP Top 10 への対応）
2. 可読性・保守性
3. テストカバレッジ（新規コードは原則 80% 以上）
4. パフォーマンスへの影響
