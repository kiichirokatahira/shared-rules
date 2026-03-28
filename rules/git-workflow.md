# Git 運用ルール

## ブランチ戦略

```
main          # 本番リリース済みコード（直接 push 禁止）
develop       # 開発統合ブランチ
feature/*     # 機能開発
fix/*         # バグ修正
hotfix/*      # 本番緊急修正
chore/*       # ビルド・依存関係・ドキュメント更新
```

## コミットメッセージ規約（Conventional Commits）

```
<type>(<scope>): <subject>

<body>  # 任意：なぜこの変更が必要か

<footer>  # 任意：breaking change, issue 番号など
```

### type 一覧

| type | 用途 |
|---|---|
| `feat` | 新機能追加 |
| `fix` | バグ修正 |
| `refactor` | リファクタリング（動作変更なし） |
| `test` | テスト追加・修正 |
| `docs` | ドキュメントのみの変更 |
| `chore` | ビルド・CI・依存関係の更新 |
| `perf` | パフォーマンス改善 |

### 例

```
feat(auth): Google OAuth ログインを追加

セキュリティ要件に基づき、パスワードレス認証の選択肢として追加。
既存のメール認証との併用が可能。

Closes #42
```

## プルリクエストのルール

1. PR タイトルもコミットメッセージ規約に従う
2. **1 PR = 1 つの目的**（機能追加と大規模リファクタを混在させない）
3. レビュアーは最低 1 名のアサインが必須
4. CI（テスト・lint）がすべて通過してからマージする
5. マージ後はブランチを削除する

## その他

- `main` への直接 push は禁止
- force push は `main`/`develop` に対して禁止
- merge commit は使用せず、**squash merge** または **rebase merge** を使う
