# コーディング規約

## 共通ルール（言語問わず）

- インデントは **スペース 2 つ**（YAML/Python は例外あり）
- 1 行の最大文字数は **120 文字**
- ファイル末尾には必ず**改行を 1 つ**入れる
- コメントは「何をするか」でなく「**なぜそうするか**」を書く
- マジックナンバーは必ず**定数として定義**する

## 命名規則

| 対象 | 規則 | 例 |
|---|---|---|
| 変数・関数 | camelCase | `getUserName()` |
| クラス・型 | PascalCase | `UserProfile` |
| 定数 | UPPER_SNAKE_CASE | `MAX_RETRY_COUNT` |
| ファイル名 | kebab-case | `user-profile.ts` |
| DB カラム | snake_case | `created_at` |

## TypeScript / JavaScript

- `any` 型の使用は禁止（やむを得ない場合は `// eslint-disable` コメントと理由を記載）
- `null` より `undefined` を優先する
- 非同期処理は `async/await` を使用し、`.then()` チェーンは避ける

## Python

- 型ヒントを必ず付ける
- Docstring は Google スタイルで記述する
- `import *` は禁止

## DB 開発規約

### DB・スキーマ構成

| DB名 | 用途 | 主なスキーマ |
|---|---|---|
| `CORE_Kaonavi` | カオナビ API から取得した生データ | `dbo` |
| `CORE_JinjiBugyo` | 人事奉行サーバから取得した生データ | `dbo` |
| `CORE_HRFiles` | 人事申請ファイルの取込・確定処理 | `dbo` |
| `HR` | 連携・レポート用の統合ビュー・マスタ | `dbo`（共通）, `AG`/`AV`/`DV`/`ZL`/`ID`（事業会社別） |

> `queryinsights` / `sys` スキーマは Fabric 自動生成のシステムオブジェクト。手動編集禁止。

---

### テーブル命名規則

テーブル名は `{プレフィックス}_{データ種別}` の形式で、**アンダースコア区切り**で記述する。

| プレフィックス | 用途 | 例 |
|---|---|---|
| `WK_` | ワークテーブル（一時処理・ステージング用） | `WK_EMPLOYEE_AVANT`, `WK_ORG_H` |
| `申請_` | 事業会社から申請中のデータ | `申請_社員組織マスタ_AVANT` |
| `確定_` | 申請が確定されたデータ | `確定_人事奉行マスタ`, `確定_組織マスタ` |
| `申請確定_` | 申請〜確定を統合した HR スキーマのテーブル | `申請確定_人事奉行マスタ` |
| `人事奉行_` | 人事奉行ソースデータ | `人事奉行_社員_基本`, `人事奉行_組織_体系` |
| `カオナビ_` | カオナビソースデータ（HR スキーマ） | `カオナビ_基本情報`, `カオナビ_資格` |
| `アカウント管理_` | アカウント管理テーブル | `アカウント管理_USER` |
| （プレフィックスなし） | CORE スキーマの正規化済みテーブル | `members`, `departments`, `career_history` |

**事業会社サフィックス**（複数会社のデータを分けて管理する場合）

| サフィックス | 対象会社 |
|---|---|
| `_AVANT` / `_avant` | アバント |
| `_AVANTGROUP` / `_avantgroup` | アバントグループ |
| `_DIVA` / `_diva` | DIVA |
| `_ZEAL` / `_zeal` | ZEAL |

---

### ビュー命名規則

ビュー名は `{用途プレフィックス}_{対象システム}_{内容}` の形式で記述する。
スキーマ別ビューはファイル名に `{ビュー名}.sql` の形式を使う。

| プレフィックス | 用途 | スキーマ | 例 |
|---|---|---|---|
| `連携処理_` | 外部システムへのデータ連携用 | `dbo` | `連携処理_カオナビ_基本情報` |
| `レポート_` | 帳票・レポート出力用 | `dbo`, `AG`/`AV`/`DV`/`ZL`/`ID` | `レポート_人事奉行_社員番号` |
| `申請確定_` | 申請確定処理の参照用 | `AG`/`AV`/`DV`/`ZL`/`ID` | `申請確定_組織マスタ` |

---

### ファンクション・プロシージャ命名規則

| 対象 | プレフィックス | 例 |
|---|---|---|
| ファンクション | `f_` | `f_人事奉行_社員_基本`, `f_FullKanaToHalfKana` |
| ストアドプロシージャ | `sp_` | `sp_確定処理` |

---

### その他の命名規則

| 対象 | 規則 | 例 |
|---|---|---|
| カラム | snake_case | `employee_id`, `created_at` |
| インデックス | `ix_{テーブル名}_{カラム名}` | `ix_Employee_department_id` |
| 主キー制約 | `pk_{テーブル名}` | `pk_Employee` |
| 外部キー制約 | `fk_{テーブル名}_{参照テーブル名}` | `fk_Employee_Department` |

### SQL 記述スタイル

- **予約語は大文字**で記述する（`SELECT`, `FROM`, `WHERE`, `JOIN` 等）
- **インデントはスペース 4 つ**（SQL は例外として 4 スペース）
- `SELECT *` は禁止。必ず**カラム名を明示**する
- `JOIN` には必ず **結合条件（`ON` 句）** を記述する（クロスジョインを防ぐ）
- サブクエリより **CTE（`WITH` 句）** を優先して使用する

```sql
-- Good
WITH active_employees AS (
    SELECT
        employee_id,
        employee_name,
        department_id
    FROM Employee
    WHERE is_active = 1
)
SELECT
    e.employee_id,
    e.employee_name,
    d.department_name
FROM active_employees AS e
INNER JOIN Department AS d
    ON e.department_id = d.department_id
;

-- Bad
SELECT * FROM Employee e, Department d WHERE e.department_id = d.department_id
```

### テーブル設計

- すべてのテーブルに以下の**管理カラムを必ず含める**

  | カラム名 | 型 | 説明 |
  |---|---|---|
  | `created_at` | DATETIME | レコード作成日時 |
  | `updated_at` | DATETIME | レコード更新日時 |
  | `created_by` | NVARCHAR | 作成者（プログラム名 or ユーザー名） |

- **NULL 許容は最小限**にする。NOT NULL を原則とし、NULL を許容する場合はコメントで理由を記載する
- 論理削除を使う場合は `is_deleted BIT NOT NULL DEFAULT 0` カラムで管理する

### ビュー設計

- ビューに**ビジネスロジックを持たせない**（集計・フィルタのみ）
- ビュー定義ファイルの冒頭に以下を記載する

  ```sql
  -- ビュー名  : vw_連携処理_カオナビ_組織
  -- 用途      : カオナビAPI連携用の組織データ抽出
  -- 仕様書    : fabricSpec/Local/Kaonavi/処理仕様書/vw_連携処理_カオナビ_組織仕様書.md
  -- 更新履歴  : YYYY-MM-DD 変更内容
  ```

### トランザクション・エラー処理

- データ変更（INSERT/UPDATE/DELETE）は必ず **`BEGIN TRANSACTION` / `COMMIT` / `ROLLBACK`** で囲む
- ストアドプロシージャには **`TRY...CATCH`** を必ず実装する

```sql
BEGIN TRY
    BEGIN TRANSACTION
        -- 処理
    COMMIT TRANSACTION
END TRY
BEGIN CATCH
    IF @@TRANCOUNT > 0 ROLLBACK TRANSACTION
    THROW
END CATCH
```

### パフォーマンス

- `WHERE` 句で使用するカラムには適切なインデックスを設定する
- `SELECT` 結果が大量になる可能性がある場合は `TOP` や `OFFSET-FETCH` でページングする
- 本番実行前に**実行プランを確認**し、Table Scan が発生していないことを検証する

---

## コードレビュー基準

1. セキュリティ（OWASP Top 10 への対応 / SQL インジェクション対策）
2. 可読性・保守性
3. テストカバレッジ（新規コードは原則 80% 以上）
4. パフォーマンスへの影響（DB は実行プランも確認）
