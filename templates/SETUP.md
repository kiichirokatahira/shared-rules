# 事前準備ガイド — AI 駆動開発ワークフローのセットアップ

このドキュメントは `watch-change-requests.py` を使った AI 駆動開発ワークフローを
動かすために必要なツールのインストール手順です。

---

## 前提条件

| ツール | 最低バージョン | 確認コマンド |
|---|---|---|
| Node.js | 18 以上 | `node --version` |
| Git | 2.x 以上 | `git --version` |
| Python | 3.8 以上 | `python --version` |

### Node.js のインストール（npm が見つからない場合）

`npm` が見つからない場合は Node.js をインストールしてください。

**Windows（推奨: winget）:**

```powershell
winget install OpenJS.NodeJS.LTS
```

インストール後、PowerShell を**一度閉じて開き直す**と `node` / `npm` コマンドが使えるようになります。

```powershell
node --version   # v20.x.x などが表示されれば OK
npm --version
```

---

## 1. Claude Code のインストール

Claude Code は Anthropic が提供する AI コーディングエージェントの CLI ツールです。
`_ai` フォルダへの変更依頼フォルダ移動をトリガーに自動起動されます。

### インストール

```powershell
npm install -g @anthropic-ai/claude-code
```

### 認証

**claude.ai サブスクリプション（Pro/Max）を使用している場合（推奨）:**

API キーは不要です。以下のコマンドでブラウザ認証します。

```powershell
claude login
```

**API キーを直接使用する場合:**

[Anthropic Console](https://console.anthropic.com/) で API キーを取得し、環境変数に設定します。

```powershell
# PowerShell（現在のユーザーに永続設定）
[System.Environment]::SetEnvironmentVariable("ANTHROPIC_API_KEY", "sk-ant-...", "User")
```

### 動作確認

```powershell
claude --version
```

バージョン番号が表示されれば成功です。

---

## 2. Codex CLI のインストール

Codex CLI は OpenAI が提供する AI コーディングエージェントの CLI ツールです。
`_codex` フォルダへのファイル移動をトリガーに自動起動されます。

### インストール

```powershell
npm install -g @openai/codex
```

### API キーの設定

[OpenAI Platform](https://platform.openai.com/api-keys) で API キーを取得し、環境変数に設定します。

**システム環境変数に永続設定する（推奨）:**

```powershell
# PowerShell（現在のユーザーに永続設定）
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

### 動作確認

```powershell
codex --version
```

バージョン番号が表示されれば成功です。

---

## 3. 環境変数の反映

> **claude.ai サブスクリプションで `claude login` 認証済みの場合、`ANTHROPIC_API_KEY` の設定は不要です。**
> API キー方式を使う場合のみ以下の手順が必要です。

`SetEnvironmentVariable` で設定した環境変数は **新しく開いた PowerShell ウィンドウ** から有効になります。
設定後は一度 PowerShell を閉じて開き直してください。

現在のセッションで即時反映したい場合:

```powershell
$env:ANTHROPIC_API_KEY = "sk-ant-..."   # API キー方式の場合のみ
$env:OPENAI_API_KEY    = "sk-..."       # Codex を使う場合
```

---

## 4. Python 依存ライブラリ

`watch-change-requests.py` および `list-change-requests.py` は Python 標準ライブラリのみを使用するため、
追加インストールは不要です。

---

## 5. セットアップ確認チェックリスト

```
[ ] node --version   → v18 以上
[ ] python --version → 3.8 以上
[ ] git --version
[ ] claude --version
[ ] codex --version

# 認証（いずれかを選択）
[ ] claude login 済み（claude.ai サブスクリプション使用の場合）
    または
[ ] $env:ANTHROPIC_API_KEY が設定済み（API キー使用の場合）

[ ] $env:OPENAI_API_KEY が設定済み（Codex を使用する場合）
```

---

## 6. watch-change-requests.py の起動

すべての確認が完了したら、プロジェクトルートで以下を実行してください:

```powershell
# 監視開始（ターミナルは閉じないでください）
python scripts/watch-change-requests.py

# 自動実行モード（許可プロンプトなし）
python scripts/watch-change-requests.py --auto

# 起動時に既存ファイルも処理する場合
python scripts/watch-change-requests.py --auto --check-existing
```

`_ai` フォルダ（`020_planning_ai/` など）に変更依頼フォルダ（`YYYYMMDD-xxxx/`）を移動すると、
worktree の作成とエージェントの起動が自動で行われます。
