# Step 070 — AI: テスト実行と結果レポート生成

あなたは **AI** として動作します。
このステップの役割は「テスト実行と結果レポートの生成」です。

## 入力

- 変更依頼ファイル（プロンプトで**絶対パス**として渡されます）
  - 末尾の `## 機能仕様書` セクションの「受け入れ基準」を使用します

> **パス解決の注意（重要）**  
> プロンプトで受け取った変更依頼ファイルの絶対パスを基点に、すべてのパスを導出してください。  
>
> 例: 入力が `/path/to/project/x20_変更依頼/change-requests/070_testing_ai/20260604-xxx/change-request.md` の場合  
> - CR フォルダ: `/path/to/project/x20_変更依頼/change-requests/070_testing_ai/20260604-xxx/`  
> - テスト結果の保存先: `/path/to/project/x20_変更依頼/change-requests/070_testing_ai/20260604-xxx/test-results.md`  
> - ログの保存先: `/path/to/project/x20_変更依頼/change-requests/070_testing_ai/20260604-xxx/logs/070_testing_ai.md`  
> - 移動先フォルダ: `/path/to/project/x20_変更依頼/change-requests/080_review_ai/20260604-xxx/`

## テスト種別と判定基準

| テスト種別 | 例 | 環境依存で実行不可の場合 |
|---|---|---|
| 静的チェック（構文・規約等） | `py_compile`、SELECT * チェック | **FAIL** → 050 へ差し戻し |
| Fabric テーブル定義チェック | スコープ内の `CREATE TABLE` が Pipeline 用成果物へ変換済みか確認 | **FAIL** → 050 へ差し戻し |
| ローカル単体テスト（接続不要） | pytest（モック使用） | **FAIL** → 050 へ差し戻し |
| インフラ依存テスト（DB / API 接続等） | Oracle / Fabric 接続テスト | **SKIP**（FAIL ではない） |

インフラ依存テストのみが SKIP の場合は全体判定を **「PASS（インフラ接続テスト SKIP）」** とする。

## 手順

1. 変更依頼ファイルの `## 機能仕様書` セクションにある受け入れ基準を読む
2. フィーチャーブランチをチェックアウトする

   ```bash
   git checkout ai-YYYYMMDD-xxxx
   ```

3. 受け入れ基準に基づきテストを実装・実行する
4. 既存テストのリグレッションチェックを実施する
5. テスト結果サマリーを CR フォルダ内の `test-results.md` に保存してコミットする
6. CR フォルダごと `080_review_ai/` に移動する

   ```bash
   mv /path/to/070_testing_ai/20260604-xxx \
      /path/to/080_review_ai/
   ```

## テスト結果サマリーのフォーマット

`{CR フォルダ}/test-results.md` に以下の形式で保存してください:

```markdown
# テスト結果: [ブランチ名]

**実行日時**: YYYY-MM-DD HH:MM
**対象変更依頼**: x20_変更依頼/change-requests/070_testing_ai/YYYYMMDD-xxxx/change-request.md
**ブランチ**: ai-YYYYMMDD-xxxx

## 受け入れ基準テスト

| # | テスト内容 | 結果 | 備考 |
|---|---|---|---|
| 1 | 〇〇が動作すること | PASS | — |
| 2 | エラーケースが処理されること | PASS | — |

## リグレッションテスト

| テストスイート | 件数 | PASS | FAIL | SKIP |
|---|---|---|---|---|
| 単体テスト | 100 | 100 | 0 | 0 |

## 判定

**PASS** <!-- FAIL / PASS（インフラ接続テスト SKIP）のいずれかに変更 -->

## 失敗詳細（FAIL の場合のみ記載）

（失敗したテストの内容・エラーメッセージ・原因）

## SKIP 理由（インフラ接続テスト SKIP がある場合のみ記載）

（SKIP したテストの一覧と接続不可の理由）
```

## 制約

- `main` へのコミット禁止
- テスト結果サマリーはフィーチャーブランチにコミットする
- テスト失敗時は自動修正を行わず、結果を記録して終了する
