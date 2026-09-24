<#
.SYNOPSIS
  Deja utilizables los comandos del repo en Windows.

.DESCRIPTION
  Gemelo de `restore-symlinks.sh`, que existe porque el `.sh` termina
  diciendo "este script no corre en Windows nativo" — y Windows es
  justo la plataforma donde el problema ocurre.

  EL PROBLEMA, MEDIDO EL 2026-09-12. En Windows sin Developer Mode,
  `git config core.symlinks false` es obligatorio para que el checkout
  no falle. Con esa config git materializa cada symlink como un archivo
  de texto cuyo contenido es la ruta del target: `.claude/commands/
  spec-implement.md` queda en 40 bytes que dicen
  `../../.agents/commands/spec-implement.md`.

  Consecuencia: los 15 comandos existen, pesan, y NO HACEN NADA. Un
  agente que lee `.claude/commands/` carga una ruta en vez de un
  comando, y `/spec-implement` simplemente no existe. Se midió clonando
  un repo adoptado y lanzando Claude Code contra él: los 15 archivos
  eran stubs.

  No falla con error: falla en silencio, que es el molde que este repo
  persigue. Por eso el script REPORTA cuántos stubs encontró aunque no
  pueda arreglarlos con symlinks reales.

.PARAMETER TargetDir
  Directorio donde viven `.claude/` y `.agents/`. Por defecto, el actual.

.EXAMPLE
  pwsh -File scripts/restore-symlinks.ps1
  pwsh -File scripts/restore-symlinks.ps1 -TargetDir D:\repos\mi-servicio
#>
[CmdletBinding()]
param(
    [string]$TargetDir = "."
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $TargetDir)) {
    Write-Error "no existe el directorio $TargetDir"
    exit 1
}
$target = (Resolve-Path -LiteralPath $TargetDir).Path

if (-not (Test-Path -LiteralPath (Join-Path $target ".agents\commands"))) {
    Write-Error "No existe $target\.agents\commands\ - este script asume estructura AI-DLC."
    exit 1
}

# ---- 1. ¿se pueden crear symlinks reales? ----
# Developer Mode o admin. Se prueba creando uno de verdad en lugar de
# consultar el registro: el registro dice qué está configurado, la
# prueba dice qué funciona, y son cosas distintas cuando hay directivas
# de grupo de por medio.
$puedeSymlink = $false
$probe = Join-Path ([System.IO.Path]::GetTempPath()) ("herdr-probe-" + [guid]::NewGuid().ToString("N"))
try {
    New-Item -ItemType SymbolicLink -Path $probe -Target ([System.IO.Path]::GetTempPath()) -ErrorAction Stop | Out-Null
    $puedeSymlink = $true
    Remove-Item -LiteralPath $probe -Force -ErrorAction SilentlyContinue
} catch {
    $puedeSymlink = $false
}

# ---- 2. enlazar o materializar ----
function Restore-One {
    param([string]$LinkPath, [string]$RelTarget, [string]$RealSource)

    if ($script:puedeSymlink) {
        if (Test-Path -LiteralPath $LinkPath) { Remove-Item -LiteralPath $LinkPath -Force -Recurse }
        New-Item -ItemType SymbolicLink -Path $LinkPath -Target $RelTarget -ErrorAction Stop | Out-Null
        return "link"
    }

    # Sin Developer Mode el symlink real no se puede. Se copia el
    # CONTENIDO, que deja el repo funcionando: es lo mismo que ve un
    # Linux al resolver el enlace. El coste está en el reporte de abajo.
    Copy-Item -LiteralPath $RealSource -Destination $LinkPath -Force
    return "copia"
}

$links = 0; $copias = 0; $stubs = 0

$adoptMd = Join-Path $target "ADOPT.md"
if (Test-Path -LiteralPath $adoptMd) {
    $r = Restore-One -LinkPath (Join-Path $target ".agents\commands\adopt.md") `
                     -RelTarget "..\..\ADOPT.md" -RealSource $adoptMd
    if ($r -eq "link") { $links++ } else { $copias++ }
} else {
    Write-Warning "no existe ADOPT.md en $target - se omite .agents/commands/adopt.md"
}

$claudeDir = Join-Path $target ".claude\commands"
if (-not (Test-Path -LiteralPath $claudeDir)) {
    New-Item -ItemType Directory -Path $claudeDir -Force | Out-Null
}

Get-ChildItem -LiteralPath (Join-Path $target ".agents\commands") -Filter *.md -File | ForEach-Object {
    $nombre = $_.Name
    $destino = Join-Path $claudeDir $nombre

    # Un stub es un archivo pequeño cuyo contenido entero es una ruta.
    if (Test-Path -LiteralPath $destino) {
        $contenido = (Get-Content -LiteralPath $destino -Raw -ErrorAction SilentlyContinue)
        if ($contenido -and $contenido.Trim() -match '^\.\.[\\/].*\.md$') { $stubs++ }
    }

    $r = Restore-One -LinkPath $destino -RelTarget "..\..\.agents\commands\$nombre" -RealSource $_.FullName
    if ($r -eq "link") { $links++ } else { $copias++ }
}

# ---- 3. reportar, y decir la consecuencia ----
Write-Host ""
Write-Host "Comandos en $target"
Write-Host "  stubs encontrados : $stubs   (archivos de texto con la ruta dentro: NO funcionaban)"
Write-Host "  symlinks reales   : $links"
Write-Host "  copias de contenido: $copias"
Write-Host ""

if ($copias -gt 0) {
    Write-Host "Esta maquina no puede crear symlinks (falta Developer Mode o admin),"
    Write-Host "asi que se copio el contenido. El repo YA FUNCIONA, con un efecto:"
    Write-Host "git ve esos archivos como modificados, porque en el index son modo"
    Write-Host "120000 y en disco son texto."
    Write-Host ""
    Write-Host "  Para ocultarlos del status sin perder el arreglo:"
    Write-Host "    git update-index --skip-worktree .claude/commands/*.md"
    Write-Host ""
    Write-Host "  Para volver al estado original (y romper los comandos otra vez):"
    Write-Host "    git checkout -- .claude/commands/"
    Write-Host ""
    Write-Host "  Para arreglarlo de raiz: activa Developer Mode en Windows,"
    Write-Host "  'git config --local core.symlinks true' y vuelve a clonar."
}
