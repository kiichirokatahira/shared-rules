# shared-rules の scripts/ を各リポジトリへ同期するスクリプト
# 使い方: powershell -File scripts/sync-templates.ps1

$sharedRulesRoot = $PSScriptRoot | Split-Path -Parent

# 同期対象リポジトリのリスト（環境に合わせて追加・編集してください）
$targetRepos = @(
    "C:/Users/kiichiro.katahira.AD/OneDrive - AVANT GROUP/git/ag-groupit-dwh-azurefunction",
    "C:/Users/kiichiro.katahira.AD/OneDrive - AVANT GROUP/git/ag-groupit-dwh-fabric-it"
)

# 同期対象ファイル（scripts/ 内のスクリプト群）
$sourceScriptsDir = Join-Path $sharedRulesRoot "templates/scripts"

foreach ($repo in $targetRepos) {
    $destScriptsDir = Join-Path $repo "scripts"

    if (-not (Test-Path $repo)) {
        Write-Warning "リポジトリが見つかりません: $repo"
        continue
    }

    if (-not (Test-Path $destScriptsDir)) {
        New-Item -ItemType Directory -Path $destScriptsDir | Out-Null
    }

    $files = Get-ChildItem -Path $sourceScriptsDir -File
    foreach ($file in $files) {
        $dest = Join-Path $destScriptsDir $file.Name
        Copy-Item -Path $file.FullName -Destination $dest -Force
        Write-Host "  コピー: $($file.Name) -> $repo/scripts/"
    }

    Write-Host "[完了] $repo"
}

Write-Host ""
Write-Host "同期完了。step-instructions は @import で自動参照されるためコピー不要です。"
