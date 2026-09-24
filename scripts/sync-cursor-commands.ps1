# sync-cursor-commands.ps1 — Alias retrocompatible de sync-tooling.ps1
#
# Preferir: powershell -ExecutionPolicy Bypass -File scripts/sync-tooling.ps1

$ErrorActionPreference = 'Stop'
$here = $PSScriptRoot
& (Join-Path $here 'sync-tooling.ps1') @args
exit $LASTEXITCODE
