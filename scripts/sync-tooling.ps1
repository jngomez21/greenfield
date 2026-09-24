# sync-tooling.ps1 — Sincroniza mirrors de Cursor, OpenCode y Copilot desde .agents/
#
# Cursor slash commands:  .agents/commands/ → .cursor/commands/
# OpenCode slash commands: .agents/commands/ → .opencode/commands/
# OpenCode skills:         .agents/skills/<name>/ → .opencode/skills/<name>/
# Copilot slash commands:  .agents/commands/<n>.md → .github/prompts/<n>.prompt.md
#
# El sufijo `.prompt.md` es parte del contrato de Copilot: sin el, el
# archivo no aparece en el menu `/` del chat.
#
# ai-dlc-init y ai-dlc-upgrade lo hacen automáticamente; usa este script
# si adoptaste antes de la versión con soporte OpenCode/Cursor.
#
# Uso (desde el root del repo adoptado):
#   powershell -ExecutionPolicy Bypass -File scripts/sync-tooling.ps1

$ErrorActionPreference = 'Stop'

$Root = $PSScriptRoot
if ((Split-Path -Leaf $Root) -eq 'scripts') {
    $Root = Split-Path -Parent $Root
}

$agentCmdDir = Join-Path $Root '.agents\commands'
$agentSkillsDir = Join-Path $Root '.agents\skills'
$cursorDir = Join-Path $Root '.cursor\commands'
$openCodeCmdDir = Join-Path $Root '.opencode\commands'
$openCodeSkillsDir = Join-Path $Root '.opencode\skills'
$copilotPromptDir = Join-Path $Root '.github\prompts'

if (-not (Test-Path -LiteralPath $agentCmdDir)) {
    [Console]::Error.WriteLine('ERROR: no existe .agents/commands/')
    exit 1
}

New-Item -ItemType Directory -Force -Path $cursorDir, $openCodeCmdDir, $openCodeSkillsDir, $copilotPromptDir | Out-Null

$cmdCount = 0
Get-ChildItem -LiteralPath $agentCmdDir -Filter '*.md' -File | ForEach-Object {
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $cursorDir $_.Name) -Force
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $openCodeCmdDir $_.Name) -Force
    $promptName = [System.IO.Path]::GetFileNameWithoutExtension($_.Name) + '.prompt.md'
    Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $copilotPromptDir $promptName) -Force
    Write-Host "comando: $($_.Name) → .cursor/commands/, .opencode/commands/ y .github/prompts/$promptName"
    $cmdCount++
}

$skillCount = 0
if (Test-Path -LiteralPath $agentSkillsDir) {
    Get-ChildItem -LiteralPath $agentSkillsDir -Directory | ForEach-Object {
        $skillMd = Join-Path $_.FullName 'SKILL.md'
        if (-not (Test-Path -LiteralPath $skillMd)) { return }
        $destDir = Join-Path $openCodeSkillsDir $_.Name
        New-Item -ItemType Directory -Force -Path $destDir | Out-Null
        Copy-Item -LiteralPath $skillMd -Destination (Join-Path $destDir 'SKILL.md') -Force
        Get-ChildItem -LiteralPath $_.FullName -File | Where-Object { $_.Name -ne 'SKILL.md' } | ForEach-Object {
            Copy-Item -LiteralPath $_.FullName -Destination (Join-Path $destDir $_.Name) -Force
        }
        Write-Host "skill: $($_.Name) → .opencode/skills/$($_.Name)/"
        $skillCount++
    }
}

Write-Host ''
Write-Host "Listo: $cmdCount comando(s), $skillCount skill(s) sincronizados."
Write-Host 'Cursor: Ctrl+Shift+P → Reload Window, luego / en Agent.'
Write-Host 'OpenCode: reinicia el TUI, luego / en el proyecto.'
Write-Host 'Copilot (VS Code): Ctrl+Shift+P → Reload Window, y pon el chat en MODO AGENTE.'
Write-Host '  En modo Ask no se adjunta AGENTS.md: el agente opera sin contrato y sin error.'
