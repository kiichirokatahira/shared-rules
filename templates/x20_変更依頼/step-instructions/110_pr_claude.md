# Step 110 — Claude: GitHub PR の作成

あなたは **Claude** として PR 作成を担当します。
このステップの役割は「フィーチャーブランチから main へのプルリクエストを作成すること」です。

## 入力

- 変更依頼ファイル（プロンプトで**絶対パス**として渡されます）
- `docs/specs/YYYY-MM-DD-xxxx.md`（変更依頼ファイルと同名）
- フィーチャーブランチの変更内容

> **パス解決の注意（重要）**  
> Claude は worktree ディレクトリで起動されます。カレントディレクトリからの相対パスは使えません。  
> プロンプトで受け取った変更依頼ファイルの絶対パスを基点に、すべてのパスを導出してください。  
>
> 例: 入力が `/path/to/project/x20_変更依頼/change-requests/110_pr_claude/2026-06-04-xxx.md` の場合  
> - 移動先: `/path/to/project/x20_変更依頼/change-requests/120_done_person/2026-06-04-xxx.md`

## 手順

1. `docs/specs/YYYY-MM-DD-xxxx.md`（変更依頼ファイルと同名）を読み、変更内容・受け入れ基準を把握する
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
   - 実装レビュー: 承認済み（Step 060）
   - テストレビュー: 承認済み（Step 080）
   - 動作確認: 承認済み（Step 090）

   Refs: docs/specs/YYYY-MM-DD-xxxx.md
   EOF
   )"
   ```

4. PR URL を変更依頼ファイルに追記する
5. 変更依頼ファイルを `x20_変更依頼/change-requests/120_done_person/` に**絶対パスで**移動する

## 制約

- `main` への直接コミット・プッシュ禁止
- PR タイトルは `feat(scope):` 形式で記載する
- PR 作成後にブランチをマージしない（Step 120 で人間が実施）
