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
 ├─ src/                         ← プログラム本体
 ├─ docs/
 │   ├─ SPEC.md                  ← 機能仕様書（Claude Code推奨形式）
 │   ├─ test-specs/              ← テスト仕様書（受け入れ基準）
 │   └─ change-requests/         ← 変更依頼ファイル
 │       └─ 2026-06-03-xxxx.md
 ├─ test-results/                ← テスト結果サマリー（git管理）
 ├─ CLAUDE.md                    ← Claude Code 用コンテキスト指示
 ├─ AGENTS.md                    ← Codex 用コンテキスト指示（3階層で読まれる）
 └─ .claude/
     └─ settings.json            ← 権限・フック設定
```

### SPEC.md と AGENTS.md の役割分担

| ファイル | 対象 AI | 内容 |
|---|---|---|
| `SPEC.md` | Claude Code | 機能仕様・実装対象ファイル・スコープ外・検証手順を網羅した自己完結型仕様書 |
| `AGENTS.md` | Codex | コーディング規約・禁止操作・テスト実行コマンド。グローバル／リポジトリ／ディレクトリの3階層で読み込まれ、近いファイルが優先される |

> **注意**: AGENTS.md はグローバルスコープ（`~/.codex/`）の読み込みバグが報告されており（GitHub Issue #8759 等）、リポジトリ直下への配置を優先する。

---

## 3. 権限・自動化設計

```
main / develop ブランチ    ← 保護。AI は直接触らない
 └─ feature/ai-YYYYMMDD-xxxx   ← AI が作業するブランチ
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
Phase 1: 要件定義    [人間 + Claude]
Phase 2: 仕様確定    [人間 + Claude]
Phase 3: 実装        [Claude Coder / Codex]
Phase 4: テスト      [Claude DevOps / Codex]
Phase 5: レビュー    [Claude Reviewer（別セッション）]
Phase 6: CI + 統合   [GitHub Actions + 人間]
```

---

### ステップ詳細

#### Step 1｜変更依頼の作成（人間）

変更依頼ファイル（`docs/change-requests/YYYY-MM-DD-xxxx.md`）に以下のテンプレートで記載する：

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

#### Step 2｜SPEC.md の作成・更新（Claude）

Claude が変更依頼を読み、`docs/SPEC.md` を作成または更新する。SPEC.md に含める内容：

- 変更対象のファイル名とインターフェース
- スコープ外（変更しない箇所）の明示
- エンドツーエンドの検証手順
- 曖昧点がある場合は、同ファイル内 `## 確認事項` セクションに質問を記載する

> Claude Code 公式: 「最も有用な仕様書は自己完結型で、関係するファイルとインターフェースを明記し、スコープ外を述べ、エンドツーエンドの検証手順で締めくくる」

---

#### Step 3｜仕様の確認・回答（人間）

SPEC.md の `## 確認事項` に回答を記入し、Claude に処理再開を伝える。問題がなければ即 Step 4 へ。

---

#### Step 4｜Codex タスク設計（Claude Planner セッション）

Claude が SPEC.md を読み、Codex 向けのタスク仕様を作成する：

- 作業ブランチ名（例：`feature/ai-20260603-xxxx`）
- 変更対象ファイル一覧と変更してはいけない箇所
- **受け入れ基準（テスト仕様）** ← コーディング前に定義する
- AGENTS.md の更新が必要な場合は合わせて更新する

---

#### Step 5｜実装（Claude Coder セッション または Codex）

**【初版からの改善】** 実装は別セッションで行う（SPEC.md を読み込んだ新鮮なコンテキスト）。

- Step 4 で指定されたブランチを作成して作業する
- `main` / `develop` への直接コミットは禁止
- 実装完了後、フィーチャーブランチにプッシュする

**ヘッドレス実行オプション**（PowerShell スクリプトで自動化する場合）：

```powershell
claude -p "SPEC.mdを読んでfeature/ai-xxブランチに実装してください" `
       --output-format json
```

---

#### Step 6｜テスト実行（Claude DevOps セッション または Codex）

- Step 4 で定義した受け入れ基準に基づきテストを実装・実行する
- 既存テストのリグレッションチェックを必ず実施する
- テスト結果サマリーを `test-results/` に保存する

---

#### Step 7｜レビュー（Claude Reviewer セッション）

レビュー観点：

| チェック項目 | 内容 |
|---|---|
| 要件適合性 | SPEC.md の完了条件を満たしているか |
| コード品質 | コーディング規約への準拠、可読性 |
| テスト網羅性 | 受け入れ基準が全てカバーされているか |
| セキュリティ | OWASP Top 10 相当の問題がないか |
| リグレッション | 既存機能への影響がないか |

**審査結果の分岐：**

- **承認** → Step 8 へ
- **軽微な修正** → 修正指示を出し Step 5 へ戻る
- **致命的問題** → ブランチを破棄し Step 4 から再設計

---

#### Step 8｜PR 作成と CI 自動フィードバックループ（GitHub Actions）

**PR 作成後に動く自動処理：**

```yaml
# claude-code-action: @claude メンションで Claude がコード変更・回答を自律実行
# codex-action: PR open/synchronize 時に Codex が自動コードレビューを投稿
```

**CI フィードバックループ（ComposioHQ/agent-orchestrator パターン）：**

```
PR 作成
 ├─ CI 失敗 → エージェントがログを取得して自動修正（最大2回リトライ）
 ├─ レビュアーの修正依頼 → エージェントに再ルーティング（30分でエスカレート）
 └─ 承認 + CI 通過 → 通知（auto-merge は opt-in 設定で可能）
```

---

#### Step 9｜仕様書・ドキュメント更新（Claude または Codex）

- Claude 審査通過後に SPEC.md・README 等を更新する
- 変更依頼ファイルに完了ラベルを付与する

---

#### Step 10｜人間レビュー・マージ（人間）

1. PR の内容と CI 結果を確認する
2. 最低 1 名がコードレビューし承認する
3. squash merge または rebase merge で `main` / `develop` に統合する
4. フィーチャーブランチを削除する

---

### フロー図

```
人間: 変更依頼を記載（change-request.md）
        ↓
Claude Planner: SPEC.md を作成・確認事項を記載
        ↓ 確認点あり
人間: SPEC.md に回答
        ↓ 問題なし
Claude Planner: Codex タスク設計・受け入れ基準を定義（Step 4）
        ↓
Claude Coder（別セッション）: feature ブランチを切って実装（Step 5）
        ↓
Claude DevOps: テスト実行・サマリー保存（Step 6）
        ↓
Claude Reviewer（別セッション・Writer/Reviewerパターン）: レビュー（Step 7）
  ├─ 軽微修正 → Step 5 へ戻る
  ├─ 致命的問題 → ブランチ破棄、Step 4 へ
  └─ 承認
        ↓
GitHub Actions: PR 作成・CI 実行
  ├─ CI 失敗 → エージェントが自動修正（最大2回）
  ├─ レビュー依頼 → エージェントに再ルーティング
  └─ 承認 + CI 通過
        ↓
Claude/Codex: SPEC.md・ドキュメント更新（Step 9）
        ↓
人間: 最終確認・マージ（Step 10）
```

---

### 各役割の責任範囲

| 役割 | 担当 |
|---|---|
| 人間 | 変更依頼の作成、SPEC.md の確認・回答、最終 PR レビュー・マージ承認 |
| Claude Planner | SPEC.md 作成、Codex タスク設計、受け入れ基準定義 |
| Claude Coder | 実装（SPEC.md を読んだ別セッション） |
| Claude DevOps | テスト実行・結果レポート生成 |
| Claude Reviewer | コードレビュー（実装とは別の新鮮なセッション） |
| Codex | 実装・テスト・PR 自動レビュー（GitHub Action 経由） |
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
