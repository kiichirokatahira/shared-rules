# Step 110 — AI: GitHub PR の作成

あなたは **AI** として PR 作成を担当します。
このステップの役割は「フィーチャーブランチから main へのプルリクエストを作成すること」です。

## 入力

- 変更依頼ファイル（プロンプトで**絶対パス**として渡されます）
  - 末尾の `## 機能仕様書` セクションに変更内容・受け入れ基準が含まれています
- フィーチャーブランチの変更内容

> **パス解決の注意（重要）**  
> プロンプトで受け取った変更依頼ファイルの絶対パスを基点に、すべてのパスを導出してください。  
>
> 例: 入力が `/path/to/project/x20_変更依頼/change-requests/110_pr_ai/2026-06-04-xxx/change-request.md` の場合  
> - CR フォルダ: `/path/to/project/x20_変更依頼/change-requests/110_pr_ai/2026-06-04-xxx/`  
> - 移動先フォルダ: `/path/to/project/x20_変更依頼/change-requests/120_done_person/2026-06-04-xxx/`

## 手順

1. 変更依頼ファイルを読み、末尾の `## 機能仕様書` セクションから変更内容・受け入れ基準を把握する
2. フィーチャーブランチの変更サマリーを確認する

   ```bash
   git log main..feature/ai-YYYYMMDD-xxxx --oneline
   git diff main..feature/ai-YYYYMMDD-xxxx --stat
   ```

3. GitHub CLI で PR を作成する

   ```bash
   gh pr create \
     --title "feat: [変更内容の概要]" \
     --body "$(cat <<'EOF'
   ## 概要

   （仕様書の概要セクションから引用）

   ## 変更内容

   （変更したファイルと変更点の要約）

   ## 受け入れ基準

   （仕様書の受け入れ基準チェックリストをコピー）

   ## テスト結果

   - テスト: PASS
   - テストレビュー: 承認済み（Step 080）
   - 動作確認: 承認済み（Step 090）

   Refs: x20_変更依頼/change-requests/110_pr_ai/YYYY-MM-DD-xxxx/change-request.md
   EOF
   )"
   ```

4. PR URL を変更依頼ファイルに追記する
5. CR フォルダごと `120_done_person/` に**絶対パスで**移動する

   ```bash
   mv /path/to/110_pr_ai/2026-06-04-xxx \
      /path/to/120_done_person/
   ```

## 制約

- `main` への直接コミット・プッシュ禁止
- PR タイトルは `feat(scope):` 形式で記載する
- PR 作成後にブランチをマージしない（Step 120 で人間が実施）
