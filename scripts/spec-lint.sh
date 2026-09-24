#!/usr/bin/env bash
#
# spec-lint.sh — Linter mecánico de specs AI-DLC.
#
# Capa "Garantía" de la metodología AI-DLC (§7 del methodology): verificación
# mecánica de la consistencia estructural de las specs en specs/<feature>/
# (status.md, requirements.md, tasks.md, checklists/requirements.md). Pensado para
# correr local (pre-commit) o en CI. Self-contained: solo bash + coreutils
# (grep/sed/awk portables).
#
# Uso:
#   spec-lint.sh [<repo-root>|.] [--feature <slug>] [--strict]
#   spec-lint.sh --help
#
# Salida: una línea por hallazgo con formato "ERROR <feature>: <mensaje>" o
# "WARN <feature>: <mensaje>" (más líneas "INFO <feature>: ..." del linteo
# versionado), y un resumen final.
# Exit 0 si no hay errores; exit 1 si hay >= 1 error (warnings/info no afectan).
#
# Linteo versionado (v0.24): cada spec declara `methodology_version:` en el
# frontmatter de status.md. Las reglas introducidas DESPUÉS de esa versión no
# bloquean specs antiguas: se acumulan en una línea INFO por feature y aplican
# recién cuando la spec se re-toca (/spec-amend, bug B/C) o con --strict.
#
# Equivalente PowerShell: spec-lint.ps1 (mismo comportamiento).

set -u

usage() {
  cat <<'EOF'
spec-lint — linter mecánico de specs AI-DLC (capa "Garantía", §7 del methodology).

Uso: spec-lint.sh [<repo-root>|.] [--feature <slug>] [--strict]

  <repo-root>        Raíz del repo adoptado (default: directorio actual).
  --feature <slug>   Lintea solo specs/<slug>/ en lugar de todas las features.
  --strict           Ignora la methodology_version de las specs y aplica TODAS
                     las reglas (uso: pre-G2 y migración al re-tocar una spec).
  --help, -h         Muestra esta ayuda.

Checks: E1-E10 (errores) y W1-W8 (warnings). Las reglas E6-E9/W2/W3 (v0.22),
W7 (v0.24) y E10/W8 (v0.118) sólo aplican a specs cuya methodology_version
(status.md) sea >= a la versión que las introdujo; para specs anteriores se
reportan agregadas en una línea INFO. Ignora specs/README.md, specs/spikes/ y
archivos sueltos bajo specs/.
Exit code: 0 si no hay errores, 1 si hay >= 1 error.
EOF
}

ROOT="."
FEATURE=""
STRICT=0

while [ $# -gt 0 ]; do
  case "$1" in
    --help|-h)
      usage
      exit 0
      ;;
    --feature)
      if [ $# -lt 2 ]; then
        echo "spec-lint: --feature requiere un <slug>" >&2
        exit 1
      fi
      FEATURE="$2"
      shift 2
      ;;
    --strict)
      STRICT=1
      shift
      ;;
    --*)
      echo "spec-lint: opción desconocida '$1'" >&2
      usage >&2
      exit 1
      ;;
    *)
      ROOT="$1"
      shift
      ;;
  esac
done

SPECS_DIR="$ROOT/specs"
if [ ! -d "$SPECS_DIR" ]; then
  echo "spec-lint: no existe el directorio '$SPECS_DIR'" >&2
  exit 1
fi

ERRORS=0
WARNINGS=0
NFEATURES=0
TODAY=$(date +%Y-%m-%d)

# ---- Linteo versionado (v0.24) ---------------------------------------------
# `methodology_version:` en status.md declara con qué versión del methodology
# se autoreó la spec. Reglas posteriores a esa versión NO bloquean la spec:
# se acumulan y se reportan como una línea INFO por feature. La migración
# ocurre al re-tocar la spec (/spec-amend, bug B/C) o al correr con --strict.
SINCE_SDD="0.22"      # E6, E7, E8, E9, W2, W3 (SDD guiado)
SINCE_GATES="0.24"    # W7 (drift de firma G2)
SINCE_COBERTURA="0.118" # E10, W8 (toda R citada por una task)
PRE_VERSIONING="0.21" # asumida cuando status.md no trae el stamp
SPEC_VERSION="$PRE_VERSIONING"
GATED_COUNT=0

# version_ge A B: exit 0 si A >= B. Compara "X.Y[.Z]" numéricamente; tolera
# prefijo "v" y sufijos tipo " (draft)".
version_ge() {
  local a b
  a=$(printf '%s' "$1" | sed -E 's/^[vV]//; s/[^0-9.].*$//')
  b=$(printf '%s' "$2" | sed -E 's/^[vV]//; s/[^0-9.].*$//')
  awk -v a="$a" -v b="$b" 'BEGIN {
    na = split(a, pa, "."); nb = split(b, pb, ".")
    n = (na > nb) ? na : nb
    for (i = 1; i <= n; i++) {
      x = (i <= na) ? pa[i] + 0 : 0
      y = (i <= nb) ? pb[i] + 0 : 0
      if (x < y) exit 1
      if (x > y) exit 0
    }
    exit 0
  }'
}

# gated <feature> <since> <ERROR|WARN> <mensaje>: emite el hallazgo si la
# regla aplica a la versión de la spec (siempre en --strict); si no aplica,
# lo acumula para la línea INFO del cierre de la feature.
gated() {
  local feat="$1" since="$2" sev="$3" msg="$4"
  if [ "$STRICT" -eq 1 ] || version_ge "$SPEC_VERSION" "$since"; then
    if [ "$sev" = "ERROR" ]; then err "$feat" "$msg"; else warn "$feat" "$msg"; fi
  else
    GATED_COUNT=$((GATED_COUNT + 1))
  fi
}

err() { # $1=feature $2=mensaje
  printf 'ERROR %s: %s\n' "$1" "$2"
  ERRORS=$((ERRORS + 1))
}

warn() { # $1=feature $2=mensaje
  printf 'WARN %s: %s\n' "$1" "$2"
  WARNINGS=$((WARNINGS + 1))
}

# Imprime el frontmatter YAML de un archivo (líneas entre el primer '---' en
# la línea 1 y el siguiente '---'). Tolera BOM UTF-8 y finales CRLF.
frontmatter() { # $1=file
  awk 'NR==1 {
         if (substr($0, 1, 3) == "\357\273\277") $0 = substr($0, 4)
         if ($0 !~ /^---[ \t\r]*$/) exit
         next
       }
       /^---[ \t\r]*$/ { exit }
       { print }' "$1"
}

# Valor de una clave simple del frontmatter (primera ocurrencia), sin comillas
# ni espacios finales.
# Imprime el archivo con los bloques <!-- ... --> vaciados, CONSERVANDO el
# número de líneas: así los checks que usan `grep -n` siguen reportando la
# línea real. Úsalo en todo check que cuente marcadores dentro del cuerpo
# de una spec — los guardrails de las plantillas son comentarios, y no son
# contenido que el equipo haya escrito.
sin_comentarios() { # $1 archivo
  awk '
    {
      out = ""; rest = $0
      while (length(rest) > 0) {
        if (dentro) {
          p = index(rest, "-->")
          if (p == 0) { rest = ""; break }
          rest = substr(rest, p + 3); dentro = 0
        } else {
          p = index(rest, "<!--")
          if (p == 0) { out = out rest; rest = ""; break }
          out = out substr(rest, 1, p - 1)
          rest = substr(rest, p + 4); dentro = 1
        }
      }
      print out
    }
  ' "$1"
}

fm_value() { # $1=file $2=key
  frontmatter "$1" \
    | sed -n "s/^$2:[[:space:]]*//p" \
    | head -n 1 \
    | sed -e 's/\r$//' -e 's/[[:space:]]*$//' -e 's/^"\(.*\)"$/\1/' -e "s/^'\(.*\)'\$/\1/"
}

# Imprime la sección ## OPEN_QUESTIONS (hasta el siguiente encabezado '## ').
# Lee de STDIN a propósito: el llamador le pasa el cuerpo ya pasado por
# `sin_comentarios`. Con el archivo crudo, un ejemplo de formato escrito
# dentro de un guardrail contaba como pregunta abierta de verdad.
open_questions_section() {
  awk '/^##[ \t]+OPEN_QUESTIONS/ { f = 1; next }
       f && /^##[ \t]/ { f = 0 }
       f { print }'
}

lint_feature() { # $1=dir $2=feature-slug
  local dir="$1" feat="$2"
  local status_file="$dir/status.md"
  local req_file="$dir/requirements.md"
  local chk_file="$dir/checklists/requirements.md"
  local tasks_file="$dir/tasks.md"
  local state="" modality="" state_ok=0
  local line tnum tstate env derived
  local total=0 n_cancelled=0 n_done_dep=0 any_deployed=0 any_prog=0 last_env=""

  NFEATURES=$((NFEATURES + 1))
  SPEC_VERSION="$PRE_VERSIONING"
  GATED_COUNT=0

  # ---- status.md -----------------------------------------------------------
  if [ ! -f "$status_file" ]; then
    err "$feat" "[E1] falta status.md"
  else
    state=$(fm_value "$status_file" "state")
    modality=$(fm_value "$status_file" "modality")

    # Linteo versionado: con qué versión del methodology se autoreó la spec.
    local mv
    mv=$(fm_value "$status_file" "methodology_version")
    if [ -n "$mv" ]; then
      SPEC_VERSION="$mv"
    elif [ "$state" != "legacy" ]; then
      # W6: sin stamp se asume pre-versionado (sólo reglas core aplican).
      warn "$feat" "[W6] status.md sin 'methodology_version:' — asumo $PRE_VERSIONING (sólo reglas core); agregar el stamp para linteo versionado"
    fi

    # E2: state ausente o fuera del set válido.
    if [ -z "$state" ]; then
      err "$feat" "[E2] falta 'state:' en el frontmatter de status.md"
    elif printf '%s\n' "$state" | grep -Eq '^(not-started|in-progress|feature-complete|live|cancelled|legacy|partial-deploy-[A-Za-z0-9_-]+|deployed:[A-Za-z0-9_-]+)$'; then
      state_ok=1
    else
      err "$feat" "[E2] state '$state' fuera del set válido en status.md"
    fi

    # Tasks: líneas "T<n>: <task-state> | ..."
    while IFS= read -r line; do
      line=${line%$'\r'}
      tnum=$(printf '%s\n' "$line" | sed -E 's/^[[:space:]]*T([0-9]+):.*/\1/')
      tstate=$(printf '%s\n' "$line" | sed -E 's/^[[:space:]]*T[0-9]+:[[:space:]]*//; s/[[:space:]|].*//')

      # E3: estado de task no parseable contra el set válido.
      if ! printf '%s\n' "$tstate" | grep -Eq '^(pending|blocked|in-progress|done|cancelled|deployed:[A-Za-z0-9_-]+)$'; then
        err "$feat" "[E3] task T$tnum con estado inválido '$tstate'"
        continue
      fi
      total=$((total + 1))

      case "$tstate" in
        pending)
          : ;;
        blocked)
          # E4: blocked sin blocked_by: en la misma línea.
          case "$line" in
            *blocked_by:*) : ;;
            *) err "$feat" "[E4] task T$tnum en 'blocked' sin 'blocked_by:' en la misma línea" ;;
          esac
          ;;
        in-progress)
          any_prog=1 ;;
        cancelled)
          n_cancelled=$((n_cancelled + 1)) ;;
        done|deployed:*)
          n_done_dep=$((n_done_dep + 1))
          if [ "$tstate" = "done" ]; then
            any_prog=1
          else
            any_deployed=1
            last_env=${tstate#deployed:}
          fi
          # W1: done/deployed sin hash de commit (heurística: falta "commit ").
          case "$line" in
            *"commit "*) : ;;
            *) warn "$feat" "[W1] task T$tnum '$tstate' sin hash de commit en la línea" ;;
          esac
          ;;
      esac
    done < <(grep -E '^[[:space:]]*T[0-9]+:' "$status_file" || true)

    # W4: drift entre el state declarado y el derivado de las tasks.
    derived="not-started"
    if [ "$total" -gt 0 ] && [ "$n_cancelled" -eq "$total" ]; then
      derived="cancelled"
    elif [ "$total" -gt 0 ] && [ "$n_done_dep" -eq "$total" ]; then
      # Todas las tasks done/deployed => feature-complete, ANTES de mirar
      # partial-deploy (orden del algoritmo de §6). Al revés, una feature
      # con todo desplegado a qa —el estado que el gate qa→main exige—
      # recibía W4 siempre.
      derived="feature-complete"
    elif [ "$any_deployed" -eq 1 ]; then
      derived="partial-deploy-$last_env"
    elif [ "$any_prog" -eq 1 ]; then
      derived="in-progress"
    fi
    if [ "$state_ok" -eq 1 ]; then
      case "$state" in
        live|legacy|cancelled) : ;; # dependen de información que el linter no tiene
        *)
          if [ "$derived" != "$state" ]; then
            warn "$feat" "[W4] drift de estado: declarado '$state' vs derivado de tasks '$derived'"
          fi
          ;;
      esac
    fi
  fi

  # ---- requirements.md -----------------------------------------------------
  if [ ! -f "$req_file" ]; then
    # W5: falta requirements.md y ni el state ni la modality lo eximen.
    local mod="$modality"
    [ -n "$mod" ] || mod="code"
    if [ "$state" != "legacy" ]; then
      case "$mod" in
        refactor-only|docs-only|catalog-only|config-only) : ;;
        *) warn "$feat" "[W5] falta requirements.md (state '$state', modality '$mod')" ;;
      esac
    fi
  else
    local rstatus nclar open_count=0 missing due id ln seg dup

    rstatus=$(fm_value "$req_file" "status")

    # E5: IDs de requirement **R<x>.<y>** duplicados.
    for dup in $(grep -oE '\*\*R[0-9]+\.[0-9]+\*\*' "$req_file" | sort | uniq -d | tr -d '*'); do
      err "$feat" "[E5] requirement ID duplicado: $dup"
    done

    # W2: requirement sin línea 'Tests:' en la misma línea o las 3 siguientes.
    for id in $(grep -oE '\*\*R[0-9]+\.[0-9]+\*\*' "$req_file" | tr -d '*' | sort -u); do
      ln=$(grep -nF "**$id**" "$req_file" | head -n 1 | cut -d: -f1)
      [ -n "$ln" ] || continue
      seg=$(sed -n "${ln},$((ln + 3))p" "$req_file")
      if ! printf '%s\n' "$seg" | grep -q 'Tests:'; then
        gated "$feat" "$SINCE_SDD" "WARN" "[W2] requirement $id sin línea 'Tests:' asociada"
      fi
    done

    # E10: requirement que NINGUNA task cita.
    #
    # La convención ya estaba escrita --la plantilla de `tasks.md` dice
    # "Cada task cita el R*.* que la origina"-- y nunca se comprobó. El
    # coste de no comprobarla está medido, y no en simulación:
    #
    #   `integrations-write` llegó a `deployed:main` con R4.3 sin
    #   implementar. El requisito estaba escrito, el mecanismo diseñado y
    #   el fixture planeado; lo único que faltó fue derivar la task. Las
    #   diecisiete tasks pasaron en verde, porque las puertas comprueban
    #   que las tasks estén hechas y NADIE comprobaba que las tasks
    #   cubrieran los requisitos.
    #
    # Es un gate que se satisface sin cubrir lo que dice cubrir. Por eso
    # es ERROR y no WARN: con un aviso, aquella feature habría salido
    # igual -- el linteo daba verde.
    #
    # Se compara por IGUALDAD EXACTA y no por subcadena: `grep -F R4.3`
    # también casa dentro de `R4.30`, y entonces un requisito sin task
    # pasaría por cubierto gracias a otro. Es el check vacuo de siempre,
    # y aquí sale gratis evitarlo.
    if [ -f "$tasks_file" ]; then
      citados=$(grep -oE 'R[0-9]+\.[0-9]+' "$tasks_file" | sort -u)
      for id in $(grep -oE '\*\*R[0-9]+\.[0-9]+\*\*' "$req_file" | tr -d '*' | sort -u); do
        if ! printf '%s\n' "$citados" | grep -qx "$id"; then
          gated "$feat" "$SINCE_COBERTURA" "ERROR" \
            "[E10] requirement $id no lo cita ninguna task de tasks.md"
        fi
      done
    else
      # Sin `tasks.md` no se puede comprobar, y eso se DICE. Callarse
      # aquí convertiría el check en vacuo para toda spec que no tenga
      # el archivo -- que es justo donde más falta haría.
      gated "$feat" "$SINCE_COBERTURA" "WARN" \
        "[W8] no hay tasks.md: no se puede comprobar que cada requirement tenga task"
    fi

    # E7: más de 3 marcadores [NEEDS CLARIFICATION ...].
    #
    # Se cuenta sobre el cuerpo SIN los bloques <!-- ... -->. La
    # plantilla de requirements.md trae un guardrail que dice, literal,
    # cómo se marca una ambigüedad —con `[NEEDS CLARIFICATION: ...]`— y
    # ese bloque se CONSERVA en la spec generada a propósito. Contarlo
    # hacía que toda spec naciera con un marcador fantasma: E7 empezaba
    # en 1 en vez de 0, y E8 bloqueaba cualquier spec `approved`.
    nclar=$(sin_comentarios "$req_file" | grep -o '\[NEEDS CLARIFICATION' | wc -l | tr -d '[:space:]')
    if [ "$nclar" -gt 3 ]; then
      gated "$feat" "$SINCE_SDD" "ERROR" "[E7] $nclar marcadores [NEEDS CLARIFICATION] en requirements.md (máximo 3)"
    fi

    # OPEN_QUESTIONS abiertas: E6 (sin owner/due) y W3 (due vencido).
    while IFS= read -r line; do
      line=${line%$'\r'}
      [ -n "$line" ] || continue
      open_count=$((open_count + 1))
      missing=""
      case "$line" in *owner:*) : ;; *) missing="owner:" ;; esac
      case "$line" in *due:*) : ;; *) missing="${missing:+$missing y }due:" ;; esac
      if [ -n "$missing" ]; then
        gated "$feat" "$SINCE_SDD" "ERROR" "[E6] OPEN_QUESTION abierta sin $missing ('${line:0:60}')"
      fi
      due=$(printf '%s\n' "$line" | sed -nE 's/.*due:[[:space:]]*([0-9]{4}-[0-9]{2}-[0-9]{2}).*/\1/p')
      if [ -n "$due" ] && [[ "$due" < "$TODAY" ]]; then
        gated "$feat" "$SINCE_SDD" "WARN" "[W3] OPEN_QUESTION abierta con due vencido ($due)"
      fi
    done < <(sin_comentarios "$req_file" | open_questions_section | grep -E '^[[:space:]]*- \[ \]' || true)

    # E8/E9: requirements en status approved/in-implementation/done.
    case "$rstatus" in
      approved|in-implementation|done)
        if [ "$nclar" -gt 0 ] || [ "$open_count" -gt 0 ]; then
          gated "$feat" "$SINCE_SDD" "ERROR" "[E8] requirements.md con status '$rstatus' pero contiene [NEEDS CLARIFICATION] u OPEN_QUESTIONS abiertas"
        fi
        if [ -f "$chk_file" ] && grep -Eq '^[[:space:]]*- \[ \]' "$chk_file"; then
          gated "$feat" "$SINCE_SDD" "ERROR" "[E9] requirements.md con status '$rstatus' pero checklists/requirements.md tiene items sin marcar"
        fi
        # W7: requirements firmados pero la fila G2 de la tabla Gates de
        # status.md sigue 'pending' (falta el commit de firma).
        if [ -f "$status_file" ] && grep -E '^\|[[:space:]]*G2' "$status_file" | head -n 1 | grep -q 'pending'; then
          gated "$feat" "$SINCE_GATES" "WARN" "[W7] requirements.md '$rstatus' pero la fila G2 de status.md sigue 'pending' (falta commit de firma)"
        fi
        ;;
    esac
  fi

  if [ "$GATED_COUNT" -gt 0 ]; then
    printf 'INFO %s: spec con methodology_version %s — %d hallazgo(s) de reglas posteriores omitidos (aplicarán al re-tocar la spec; ver con --strict)\n' "$feat" "$SPEC_VERSION" "$GATED_COUNT"
  fi
}

if [ -n "$FEATURE" ]; then
  if [ ! -d "$SPECS_DIR/$FEATURE" ]; then
    echo "spec-lint: no existe '$SPECS_DIR/$FEATURE'" >&2
    exit 1
  fi
  lint_feature "$SPECS_DIR/$FEATURE" "$FEATURE"
else
  for d in "$SPECS_DIR"/*/; do
    [ -d "$d" ] || continue
    feat=$(basename "$d")
    [ "$feat" = "spikes" ] && continue
    lint_feature "$d" "$feat"
  done
fi

printf 'spec-lint: %d error(es), %d warning(s) en %d feature(s).\n' "$ERRORS" "$WARNINGS" "$NFEATURES"
if [ "$ERRORS" -gt 0 ]; then
  exit 1
fi
exit 0
