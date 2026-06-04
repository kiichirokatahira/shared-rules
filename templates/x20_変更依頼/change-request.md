## 変更依頼

**ファイル名**: `docs/change-requests/010_backlog_person/YYYY-MM-DD-xxxx.md`
**作成日**: YYYY-MM-DD

> **ステータス管理**: ファイルを対応するフォルダへ移動することで進捗を表します。
> サフィックスは次に実行する担当者を示します（`_person` = 人間待ち、`_claude` = Claude 待ち、`_codex` = Codex 待ち）。
>
> | フォルダ | ステータス | 次の担当 |
> |---|---|---|
> | `010_backlog_person/` | 草案・未着手 | 人間が Claude セッションを起動 |
> | `020_planning_claude/` | 依頼内容の明確化・仕様策定 | Claude Planner |
> | `030_planning_confirmation_person/` | Claude からの質問への回答待ち | 人間が回答を記入して 020 に戻す |
> | `040_planning_check_codex/` | 仕様書の技術精査 | Codex |
> | `050_implementation_codex/` | 実装中 | Codex |
> | `060_implementation_claude/` | 実装レビュー | Claude Reviewer |
> | `070_testing_codex/` | テスト実行 | Codex |
> | `080_review_claude/` | テスト結果レビュー | Claude Reviewer |
> | `090_test_person/` | 動作確認テスト | 人間 |
> | `100_docs_claude/` | ドキュメント更新 | Claude |
> | `110_pr_claude/` | PR 作成 | Claude |
> | `120_done_person/` | PR 確認・マージ待ち | 人間 |

---

### 背景・目的

（なぜこの変更が必要か。ビジネス上の理由・問題の内容を記載する）

### 変更内容

（何を変えたいか。できるだけ具体的に記載する）

### 影響範囲（わかる範囲で）

（変更が影響するファイル・機能・画面。不明な場合は「調査が必要」と記載する）

### 完了条件

（どうなれば完了か。テスト可能な条件で記載する）

- [ ] 〇〇が動作すること
- [ ] 〇〇画面で〇〇が表示されること

### 制約・注意事項

（触ってはいけない箇所、依存関係、締め切り等）
