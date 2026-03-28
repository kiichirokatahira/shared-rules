# リポジトリ一覧と関係性

## リポジトリ一覧

| リポジトリ名 | パス | 種別 | 概要 |
|---|---|---|---|
| `bidwh` | `git/bidwh` | コード | 統合DB（MASQL）のプログラム |
| `bidwhSpec` | `git/bidwhSpec` | 設計書 | 統合DB（MASQL）の仕様書 |
| `budget` | `git/budget` | コード | 予算・購買関係 |
| `cruise` | `git/cruise` | コード | AvantCruise のプログラム |
| `customer_support` | `git/customer_support` | コード | CustomerSupport のプログラム管理 |
| `customer_support_thema` | `git/customer_support_thema` | コード | CustomerSupport サポートページの Web プログラム |
| `fabric` | `git/fabric` | コード | 統合DB（Fabric）のプログラム |
| `fabricSpec` | `git/fabricSpec` | 設計書 | 統合DB（Fabric）の仕様書 |
| `Jinjibugyo` | `git/Jinjibugyo` | コード | 人事奉行サーバ内でのプログラム |
| `JinjibugyoSpec` | `git/JinjibugyoSpec` | 設計書 | 人事奉行サーバ内での仕様書 |
| `routineTasks` | `git/routineTasks` | コード | 定例業務の管理と実行 |
| `shared-rules` | `git/shared-rules` | 共通定義 | リポジトリ間の共通ルール（このリポジトリ） |
| `snowflake` | `git/snowflake` | コード | 統合DB（Snowflake）のプログラム |
| `work` | `git/work` | コード | 全作業の作業計画と作業実績管理 |

> **ベースパス**: `C:\Users\kiichiro.katahira\OneDrive - AVANT GROUP\`

---

## コード ↔ 設計書 の対応

| コードリポジトリ | 設計書リポジトリ |
|---|---|
| `bidwh` | `bidwhSpec` |
| `fabric` | `fabricSpec` |
| `Jinjibugyo` | `JinjibugyoSpec` |
| `budget` | （設計書リポジトリなし） |
| `cruise` | （設計書リポジトリなし） |
| `customer_support` | （設計書リポジトリなし） |
| `customer_support_thema` | （設計書リポジトリなし） |
| `routineTasks` | （設計書リポジトリなし） |
| `snowflake` | （設計書リポジトリなし） |
| `work` | （設計書リポジトリなし） |

---

## システム全体の関係図

```
外部システム
  ├── カオナビ ─────────────── fabric（Fabric DB 経由で連携）
  ├── AvantCruise ──────────── cruise / fabric
  ├── 人事奉行 ─────────────── Jinjibugyo
  └── CustomerSupport ──────── customer_support / customer_support_thema

統合DB
  ├── Fabric（クラウド） ────── fabric / fabricSpec
  ├── MASQL（オンプレ） ─────── bidwh / bidwhSpec
  └── Snowflake（クラウド） ─── snowflake

業務管理
  ├── 予算・購買 ───────────── budget
  ├── 定例業務 ─────────────── routineTasks
  └── 作業計画・実績 ───────── work

共通
  └── 共通ルール ───────────── shared-rules（このリポジトリ）
```

---

## 共通ルールの適用状況

各リポジトリの `CLAUDE.md` に以下を記載することで共通ルールを適用する。

```markdown
@C:/Users/kiichiro.katahira/OneDrive - AVANT GROUP/git/shared-rules/rules/folder-structure.md
@C:/Users/kiichiro.katahira/OneDrive - AVANT GROUP/git/shared-rules/rules/code-conventions.md
@C:/Users/kiichiro.katahira/OneDrive - AVANT GROUP/git/shared-rules/rules/external-connections.md
@C:/Users/kiichiro.katahira/OneDrive - AVANT GROUP/git/shared-rules/rules/git-workflow.md
```

| リポジトリ | 共通ルール適用 | 適用ルール | 備考 |
|---|---|---|---|
| `bidwh` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `bidwhSpec` | 済 | folder-structure, git-workflow | 設計書リポジトリのため code-conventions / external-connections は除外 |
| `budget` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `cruise` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `customer_support` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `customer_support_thema` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `fabric` | 済 | 全4ルール | 既存 CLAUDE.md に追記 |
| `fabricSpec` | 済 | 全4ルール | 既存 CLAUDE.md に追記 |
| `Jinjibugyo` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `JinjibugyoSpec` | 済 | folder-structure, git-workflow | 設計書リポジトリのため code-conventions / external-connections は除外 |
| `routineTasks` | 済 | 全4ルール | 既存 CLAUDE.md に追記 |
| `snowflake` | 済 | 全4ルール | CLAUDE.md 新規作成 |
| `work` | 済 | 全4ルール | 既存 CLAUDE.md に追記 |
