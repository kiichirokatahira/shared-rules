# Step 010 — 人間: 変更依頼の作成

このステップは**人間が対応**します。
変更依頼を作成し、Claude の **Planning Mode** で内容を精査してから提出します。

## 対応手順

1. `x20_変更依頼/change-requests/010_backlog_person/` に変更依頼フォルダを作成する
   - フォルダ名: `YYYY-MM-DD-xxxx`（例: `2026-06-04-add-user-auth`）
   - フォルダ内に `change-request.md` を作成する（テンプレート: `x20_変更依頼/change-request.md` を参照）

   ```
   010_backlog_person/
     2026-06-04-add-user-auth/     ← 変更依頼フォルダ
       change-request.md           ← 依頼書（テンプレートをコピーして記入）
   ```

2. Claude を **Planning Mode**（`/plan` コマンド）で起動し、以下を依頼する:

   ```
   @x20_変更依頼/change-requests/010_backlog_person/2026-06-04-add-user-auth/change-request.md
   この変更依頼のドラフトを確認して、依頼の目的・変更内容・完了条件が明確かどうか
   指摘してください。不明瞭な箇所があれば質問してください。
   ```

3. Claude の指摘・質問に回答し、`change-request.md` を修正する
4. Claude が「内容が明確」と判断したら、フォルダごと `020_planning_ai/` に移動する

   ```
   変更前: 010_backlog_person/2026-06-04-add-user-auth/
   変更後: 020_planning_ai/2026-06-04-add-user-auth/
   ```

## 備考

- Planning Mode の目的は「仕様の曖昧さを事前に潰すこと」です
- Claude が疑問を持たない状態にしてから 020 に送ることで、020→010 の往復を減らせます
- 「調査が必要」な項目は調査が必要と明記した上で提出してかまいません
