---
tags:
  - 仕様書/index
aliases:
  - 仕様書一覧
---

# 仕様書一覧（全体 MOC）

このフォルダはプロジェクトの技術仕様書を管理します。
システム単位でサブフォルダを作り、各フォルダに `index.md`（システム MOC）を置く構成です。

## フォルダ構成

```
x30_仕様書/
  index.md              ← このファイル（全体 MOC）
  _templates/
    spec-template.md    ← 新規仕様書のテンプレート
  CORE_XX/              ← システム単位フォルダ
    index.md            ← システム MOC
    <機能名>.md         ← 仕様書本体
```

## システム別

| システム | 説明 | MOC |
|---|---|---|
| CORE_XX | （システムの一言説明） | [[CORE_XX/index\|CORE_XX 仕様書一覧]] |

## 共通事項

- **実行場所**:
- **書き込み先**: Microsoft Fabric OneLake（Delta Lake）
- **認証方式**: Service Principal（Entra ID App Registration）+ bearer_token

## 仕様書追加時のルール

1. `_templates/spec-template.md` をコピーして新しい仕様書を作成する
2. **概要優先**: 「何を・なぜ」を書く。「どのように」はコードを見ればわかるため書かない
3. 作成後、このファイル（全体 MOC）と所属システムの `index.md` にリンクを追記する
4. YAML frontmatter の `updated` を更新する

## 関連ドキュメント

- 変更依頼フォルダ: `x20_変更依頼/`
- 仕様書更新の AI 指示: `x20_変更依頼/step-instructions/100_docs_ai.md`
