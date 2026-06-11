---
tags:
  - 仕様書/index
aliases:
  - 仕様書一覧
---

# 仕様書一覧

このフォルダは Microsoft Fabric Lakehouse へのデータ連携仕様書を管理します。
各 Lakehouse（CORE_XX）単位でフォルダを分けて格納しています。

## Lakehouse 別

| Lakehouse | データソース | 仕様書 |
|---|---|---|
| CORE_XX | （データソース） | [[spec-template\|XX連携仕様書]] |

## 共通事項

- **実行場所**:
- **書き込み先**: Microsoft Fabric OneLake（Delta Lake）
- **認証方式**: Service Principal（Entra ID App Registration）+ bearer_token

## 関連ドキュメント

- 変更依頼フォルダ: `x20_変更依頼/`
