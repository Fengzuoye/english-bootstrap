# 一键生成：校验层 → 导出词典 → 一般词 → 缺词补全 → 语法 → 阅读版 → 网页版
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

if (-not $env:BOOTSTRAP_WORK) {
    $env:BOOTSTRAP_WORK = Join-Path $root 'data_src'
}
Write-Host "BOOTSTRAP_WORK = $env:BOOTSTRAP_WORK"
Write-Host "注意：WordNet 3.1 需先解压到 $env:BOOTSTRAP_WORK\wordnet_nltk\wordnet"

python tools/check.py
python tools/export_dict.py
python tools/build_general.py
python tools/build_orphans.py
python tools/build_grammar.py
python tools/build_read.py
python tools/build_web.py

Write-Host "完成。APK 需在 android/english-bootstrap-app 中用 Android Studio/Gradle 构建。"
