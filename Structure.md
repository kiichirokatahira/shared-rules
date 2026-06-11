# AI 駆動開発 — 全体構成・ワークフロー

## 1. ベースOS・実行環境

**Windows** を開発環境として使用する（社内開発者が Ubuntu に不慣れなため）。

```
Windows (ホスト)
 ├─ Node.js (winget または公式インストーラ)
 ├─ Python (公式インストーラ / uv)
 ├─ Git for Windows
 ├─ Claude Code v2.1.32 以降（agent-teams 機能を使う場合）
 └─ Codex CLI
```

**Windows 環境での注意事項：**

- シェルスクリプトは PowerShell で記述する
- `git config core.autocrlf input` で改行コードを LF に統一する
- Claude Code agent-teams のターミナル分割表示（split-pane）は tmux / iTerm2 が前提のため、**Windows では複数の PowerShell ウィンドウで代替する**（公式ドキュメントで確認済みの制約）
- Codex GitHub Action を Windows ランナーで使う場合は `safety-strategy: unsafe` が必須（サンドボックス非対応。公式ドキュメントに明記）

---

## 2. ディレクトリ・プロジェクト構成

```
project-a/
 ├─ src/                                    ← プログラム本体
 ├─ docs/
 │   ├─ specs/                              ← 変更依頼ごとの仕様書（YYYY-MM-DD-xxxx.md）
 │   └─ change-requests/                    ← 変更依頼ファイル（フォルダ位置＝進捗ステータス）
 │       ├─ 010_backlog_person/             ← 草案・未着手
 │       ├─ 020_planning_claude/            ← Claude Planner が仕様策定中
 │       ├─ 030_planning_confirmation_person/ ← 人間が質問に回答待ち
 │       ├─ 040_planning_check_codex/       ← Codex が仕様精査中
 │       ├─ 050_implementation_codex/       ← Codex が実装中
 │       ├─ 060_implementation_claude/      ← Claude Reviewer が実装レビュー中
 │       ├─ 070_testing_codex/              ← Codex がテスト中
 │       ├─ 080_review_claude/              ← Claude Reviewer がテスト結果レビュー中
 │       ├─ 090_test_person/                ← 人間が動作確認中
 │       ├─ 100_docs_claude/               ← Claude がドキュメント更新中
 │       ├─ 110_pr_claude/                 ← Claude が PR 作成中
 │       └─ 120_done_person/               ← 人間が PR 確認・マージ待ち
 ├─ test-results/                           ← テスト結果サマリー（git管理）
 ├─ CLAUDE.md                              ← Claude Code 用コンテキスト指示
 ├─ AGENTS.md                              ← Codex 用コンテキスト指示（3階層で読まれる）
 └─ .claude/
     └─ settings.json                      ← 権限・フック設定
```

### SPEC.md と AGENTS.md の役割分担

| ファイル | 対象 AI | 内容 |
|---|---|---|
| `docs/specs/YYYY-MM-DD-xxxx.md` | Claude Code / Codex | 変更依頼ごとの仕様書。機能仕様・実装対象ファイル・スコープ外・検証手順を網羅した自己完結型 |
| `AGENTS.md` | Codex | コーディング規約・禁止操作・テスト実行コマンド。グローバル／リポジトリ／ディレクトリの3階層で読み込まれ、近いファイルが優先される |

> **注意**: AGENTS.md はグローバルスコープ（`~/.codex/`）の読み込みバグが報告されており（GitHub Issue #8759 等）、リポジトリ直下への配置を優先する。

---

## 3. 権限・自動化設計

```
main / develop ブランチ    ← 保護。AI は直接触らない
 └─ ai-YYYYMMDD-xxxx           ← AI が作業するブランチ
```

- `.claude/settings.json` で許可コマンドをホワイトリスト化する
- 危険な操作（`rm -rf`、`git push --force`、`git reset --hard`）は確認を挟む
- Codex GitHub Action を使う場合、Windows ランナーでは `safety-strategy: unsafe` を設定する

---

## 4. ドキュメント管理方針

プログラムと同一リポジトリ（`docs/` 配下）で管理する。理由：
- PR 単位でコード変更と仕様変更を同期できズレが起きにくい
- Claude / Codex が同じコンテキストでコードと仕様を参照できる

| テスト成果物の種類 | 保存場所 |
|---|---|
| テスト結果サマリー（合否・件数） | git 管理（`test-results/`） |
| HTML / XML 詳細レポート | CI アーティファクト |
| スクリーンショット・動画 | CI アーティファクトまたは別途ストレージ |

---

## 5. AI 駆動開発ワークフロー

### フェーズ構成

```
Step 010: 変更依頼              [人間]             → 010_backlog_person/
Step 020: 依頼明確化・仕様策定   [Claude Planner]   → 020_planning_claude/
Step 030: 質問への回答           [人間]             → 030_planning_confirmation_person/ (→ 020 に戻す)
Step 040: 仕様書精査             [Codex]            → 040_planning_check_codex/
Step 050: 実装                  [Codex]            → 050_implementation_codex/
Step 060: 実装レビュー           [Claude Reviewer]  → 060_implementation_claude/
Step 070: テスト実行             [Codex]            → 070_testing_codex/
Step 080: テスト結果レビュー     [Claude Reviewer]  → 080_review_claude/
Step 090: 動作確認               [人間]             → 090_test_person/
Step 100: ドキュメント更新        [Claude]           → 100_docs_claude/
Step 110: PR 作成                [Claude]           → 110_pr_claude/
Step 120: マージ                 [人間]             → 120_done_person/
```

---

### ステップ詳細

#### Step 010｜変更依頼の作成（人間）

変更依頼ファイルを `docs/change-requests/010_backlog_person/YYYY-MM-DD-xxxx.md` に作成する：

```markdown
## 変更依頼

### 背景・目的
（なぜこの変更が必要か）

### 変更内容
（何を変えたいか）

### 影響範囲（わかる範囲で）
（ファイル・機能・画面）

### 完了条件
（どうなれば完了か）

### 制約・注意事項
（触ってはいけない箇所等）
```

---

#### Step 020｜依頼明確化・仕様策定（Claude Planner）

変更依頼ファイルを `020_planning_claude/` へ移動し、Claude Planner セッションを起動する。

**質問がない場合（依頼内容が明確）**：

- `docs/specs/YYYY-MM-DD-xxxx.md` を作成する
- 変更依頼ファイルを `040_planning_check_codex/` へ移動する

仕様書に含める内容：変更対象ファイル・インターフェース・スコープ外・受け入れ基準・エンドツーエンド検証手順

**質問がある場合（依頼内容が不明確）**：

- 変更依頼ファイル末尾に `## Claude からの質問` を追記する
- 変更依頼ファイルを `030_planning_confirmation_person/` へ移動する

---

#### Step 030｜質問への回答（人間）

変更依頼ファイルの `## Claude からの質問` に `**回答**: ...` 形式で回答を記入し、
`020_planning_claude/` へ戻す。

---

#### Step 040｜仕様書精査（Codex）

変更依頼ファイルを `040_planning_check_codex/` へ移動し、Codex に仕様書の技術精査を依頼する。

チェック観点：実装可能性・インターフェース整合性・スコープ漏れ・受け入れ基準の具体性

- **問題なし** → `050_implementation_codex/` へ移動
- **問題あり** → `## Codex 精査コメント` を追記し `030_planning_confirmation_person/` へ戻す

---

#### Step 050｜実装（Codex）

変更依頼ファイルを `050_implementation_codex/` へ移動し、Codex に実装を依頼する。

- `ai-YYYYMMDD-xxxx` ブランチを作成して作業する
- `main` / `develop` への直接コミットは禁止
- 実装完了後、フィーチャーブランチにプッシュし `060_implementation_claude/` へ移動

---

#### Step 060｜実装レビュー（Claude Reviewer）

変更依頼ファイルを `060_implementation_claude/` へ移動し、Claude Reviewer セッションを起動する。

チェック観点：要件適合性・スコープ遵守・コード品質・セキュリティ（OWASP Top 10）

- **問題なし** → `070_testing_codex/` へ移動
- **問題あり** → `## Claude レビュー指摘 (060→050)` を追記し `050_implementation_codex/` へ戻す

---

#### Step 070｜テスト実行（Codex）

変更依頼ファイルを `070_testing_codex/` へ移動し、Codex にテストを依頼する。

- 受け入れ基準に基づきテストを実装・実行する
- 既存テストのリグレッションチェックを実施する
- テスト結果サマリーを `test-results/YYYY-MM-DD-xxxx.md` に保存してコミットする
- 完了後 `080_review_claude/` へ移動

---

#### Step 080｜テスト結果レビュー（Claude Reviewer）

変更依頼ファイルを `080_review_claude/` へ移動し、Claude Reviewer セッションを起動する。

チェック観点：要件適合性・スコープ遵守・テスト網羅性・セキュリティ・リグレッション

- **問題なし** → `090_test_person/` へ移動
- **問題あり** → `## Claude レビュー指摘 (080→070)` を追記し `070_testing_codex/` へ戻す

---

#### Step 090｜動作確認（人間）

変更依頼ファイルを `090_test_person/` へ移動し、仕様書のエンドツーエンド検証手順に従って動作確認する。

- **問題なし** → `100_docs_claude/` へ移動
- **問題あり** → `## 人間テスト指摘 (090→020)` を追記し `020_planning_claude/` へ戻す

---

#### Step 100｜ドキュメント更新（Claude）

変更依頼ファイルを `100_docs_claude/` へ移動し、Claude にドキュメント更新を依頼する。

- 仕様書・README・AGENTS.md を実装内容に合わせて更新する
- 完了後 `110_pr_claude/` へ移動する

---

#### Step 110｜PR 作成（Claude）

変更依頼ファイルを `110_pr_claude/` へ移動し、Claude に GitHub PR の作成を依頼する。

- `gh pr create` で概要・変更内容・受け入れ基準・テスト結果を含む PR を作成する
- PR URL を変更依頼ファイルに追記する
- 完了後 `120_done_person/` へ移動する

---

#### Step 120｜マージ（人間）

変更依頼ファイルを `120_done_person/` へ移動する。

1. PR の内容と CI 結果を確認する
2. 最低 1 名がコードレビューし承認する
3. squash merge または rebase merge で `main` / `develop` に統合する
4. フィーチャーブランチを削除する

---

### フロー図

```
人間: 変更依頼を作成 → 010_backlog_person/ に配置（Step 010）
        ↓
Claude Planner: 依頼明確化・仕様書作成 → 020_planning_claude/（Step 020）
  ├─ 質問あり → 030_planning_confirmation_person/ へ（Step 030）
  │       ↓ 人間が回答 → 020 に戻す
  └─ 質問なし
        ↓
        040_planning_check_codex/ へ（Step 040）
Codex: 仕様書精査
  ├─ 問題あり → 030_planning_confirmation_person/ へ戻す
  └─ 問題なし
        ↓
        050_implementation_codex/ へ（Step 050）
Codex: feature ブランチを切って実装 → 060_implementation_claude/ へ
        ↓
Claude Reviewer: 実装レビュー（Step 060）
  ├─ 問題あり → 050_implementation_codex/ へ戻す
  └─ 問題なし → 070_testing_codex/ へ
        ↓
Codex: テスト実行・サマリー保存（Step 070） → 080_review_claude/ へ
        ↓
Claude Reviewer: テスト結果レビュー（Step 080）
  ├─ 問題あり → 070_testing_codex/ へ戻す
  └─ 問題なし → 090_test_person/ へ
        ↓
人間: 動作確認（Step 090）
  ├─ 問題あり → 020_planning_claude/ へ戻す
  └─ 問題なし → 100_docs_claude/ へ
        ↓
Claude: ドキュメント更新（Step 100） → 110_pr_claude/ へ
        ↓
Claude: GitHub PR 作成（Step 110） → 120_done_person/ へ
        ↓
人間: PR 確認・マージ（Step 120）
```

---

### 各役割の責任範囲

| 役割 | 担当 |
|---|---|
| 人間 | 変更依頼の作成（010）、質問への回答（030）、動作確認（090）、PR マージ承認（120） |
| Claude Planner | 依頼明確化・仕様書作成（020） |
| Claude Reviewer | 実装レビュー（060）、テスト結果レビュー（080） |
| Claude | ドキュメント更新（100）、PR 作成（110） |
| Codex | 仕様書精査（040）、実装（050）、テスト実行（070） |
| GitHub Actions | CI 実行・自動フィードバックループ・通知 |

---

## 6. 段階的な導入ロードマップ

一度に全機能を導入するのではなく、段階的に自動化レベルを上げることを推奨する。

| フェーズ | 導入内容 | 効果 |
|---|---|---|
| **Phase A（今すぐ）** | SPEC.md ファースト・Writer/Reviewer パターン | 品質向上、設定不要 |
| **Phase B（慣れたら）** | claude-code-action・codex-action の導入 | PR レビューの自動化 |
| **Phase C（安定後）** | agent-orchestrator による CI フィードバックループ | CI 修正の自動化 |
| **Phase D（将来）** | Claude Code agent-teams による並列実装 | 複数タスクの並列処理 |

---

## 7. 調査で確認された制約・注意点

1. **agent-teams の Windows 制約**: split-pane 表示は tmux/iTerm2 専用。Windows では複数 PowerShell ウィンドウで代替する
2. **AGENTS.md のバグ**: グローバルスコープ（`~/.codex/`）の読み込みバグあり（Issue #8759）。リポジトリ直下への配置を優先する
3. **agent-orchestrator の並列性**: 異なる AI ツール（Claude と Codex）の真の同時実行ではなく、単一エージェントの複数インスタンス並列起動
4. **auto-merge は opt-in**: agent-orchestrator のデフォルトは通知のみ。自動マージには明示的な設定変更が必要
5. **情報の新鮮さ**: agent-teams は 2026年2月リリースで実運用事例が限定的。Phase D 導入前に最新情報を確認する

---

## 参考ソース（調査で確認した一次情報源）

| ソース | 内容 |
|---|---|
| [Claude Code 公式ベストプラクティス](https://code.claude.com/docs/en/best-practices) | SPEC.md ワークフロー・Writer/Reviewer パターン |
| [Claude Code agent-teams](https://code.claude.com/docs/en/agent-teams) | マルチエージェント並列開発・フック品質ゲート |
| [anthropics/claude-code-action](https://github.com/anthropics/claude-code-action) | GitHub PR/Issue 連携 Action |
| [openai/codex-action](https://developers.openai.com/codex/github-action) | Codex CI 統合・PR 自動レビュー |
| [ComposioHQ/agent-orchestrator](https://github.com/ComposioHQ/agent-orchestrator) | CI フィードバックループ・自動修正パターン |
| [aws-samples/sample-claude-code-agent-team](https://github.com/aws-samples/sample-claude-code-agent-team) | 逐次-並列ハイブリッドマルチエージェントパターン |
| [Codex AGENTS.md ガイド](https://developers.openai.com/codex/guides/agents-md) | AGENTS.md 3階層読み込み仕様 |
