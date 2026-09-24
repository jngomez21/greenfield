#!/usr/bin/env bash
# restore-symlinks.sh — Recrea los symlinks del repo:
#   .claude/commands/*.md    → ../../.agents/commands/*.md
#   .agents/commands/adopt.md → ../../ADOPT.md
#
# Cuándo usar:
#   1) Recién transferiste el repo desde otra máquina (zip, cloud sync, email) y
#      los symlinks se rompieron — `ls -la .claude/commands/` muestra archivos
#      normales o vacíos en vez de líneas con flecha `->`.
#   2) Cloneaste en Windows sin `core.symlinks=true` + developer mode.
#   3) Sospechas drift entre wrappers y canonical.
#
# Uso (desde el directorio donde están .claude/ y .agents/):
#   bash scripts/restore-symlinks.sh
#
# O con path explícito (ejecutable desde cualquier dir):
#   bash /path/to/syc-ai-dlc/template/scripts/restore-symlinks.sh /path/to/target
#
# Idempotente: borra y recrea cada symlink. Seguro de re-ejecutar.
#
# Plataforma: macOS / Linux con bash. Para Windows ver nota al final.

set -euo pipefail

TARGET_DIR="${1:-.}"

# Resolver path absoluto
if [[ ! -d "$TARGET_DIR" ]]; then
  echo "ERROR: no existe el directorio $TARGET_DIR" >&2
  exit 1
fi

cd "$TARGET_DIR"
TARGET_ABS=$(pwd)

# Verificar estructura AI-DLC
if [[ ! -d ".agents/commands" ]]; then
  echo "ERROR: No existe $TARGET_ABS/.agents/commands/" >&2
  echo "       ¿Estás en el directorio correcto? Este script asume estructura AI-DLC." >&2
  exit 1
fi

# Crear .claude/commands/ si no existe
mkdir -p .claude/commands

CREATED=0
SKIPPED=0

# ── .agents/commands/adopt.md → ../../ADOPT.md ──
# Va primero: es el canonical de /adopt y el resto del script asume que los
# archivos de .agents/commands/ son legibles.
if [[ -f "ADOPT.md" ]]; then
  if [[ -L ".agents/commands/adopt.md" && "$(readlink .agents/commands/adopt.md)" == "../../ADOPT.md" ]]; then
    SKIPPED=$((SKIPPED + 1))
  else
    rm -rf ".agents/commands/adopt.md"
    ln -s "../../ADOPT.md" ".agents/commands/adopt.md"
    CREATED=$((CREATED + 1))
  fi
else
  echo "AVISO: no existe ADOPT.md en $TARGET_ABS — se omite .agents/commands/adopt.md" >&2
fi

# ── .claude/commands/*.md → ../../.agents/commands/*.md ──
for cmd_file in .agents/commands/*.md; do
  if [[ ! -f "$cmd_file" ]]; then
    # Glob no matcheó nada
    continue
  fi

  cmd_name=$(basename "$cmd_file")
  link_path=".claude/commands/$cmd_name"

  # Si ya es un symlink correcto, skip
  if [[ -L "$link_path" ]]; then
    expected="../../.agents/commands/$cmd_name"
    actual=$(readlink "$link_path")
    if [[ "$actual" == "$expected" ]]; then
      SKIPPED=$((SKIPPED + 1))
      continue
    fi
  fi

  # Borrar lo que haya (archivo, symlink roto, dir)
  rm -rf "$link_path"

  # Recrear symlink relativo
  ln -s "../../.agents/commands/$cmd_name" "$link_path"
  CREATED=$((CREATED + 1))
done

echo "Symlinks en $TARGET_ABS:"
echo "  Creados/recreados: $CREATED"
echo "  Ya estaban OK:    $SKIPPED"
echo ""
echo "Verificación:"
ls -la .agents/commands/adopt.md 2>/dev/null || echo "  (.agents/commands/adopt.md ausente)"
ls -la .claude/commands/ | grep -E "\.md" || echo "  (.claude/commands/ vacío)"

# Nota Windows:
# Este script no corre en Windows nativo. Opciones:
#   - WSL2: corre normal.
#   - Git Bash: corre, pero los symlinks creados pueden ser "pseudo-symlinks" según
#     git config core.symlinks. Verificar.
#   - PowerShell: hay equivalente: New-Item -ItemType SymbolicLink -Path ... -Target ...
#     (requiere developer mode o admin).
