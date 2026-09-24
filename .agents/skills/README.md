# `.agents/skills/`

Este directorio aloja **skills agente** instaladas en este repo. El
template AI-DLC **no trae ninguna pre-instalada** — cada repo decide
qué skills usar.

## Por qué vacío

Las skills concretas (`shadcn`, `playwright-best-practices`,
`vitest`, etc.) dependen del stack del repo. Un repo Python no
necesita las mismas que un Next.js. Pre-instalarlas en el template
contamina repos que tienen otro stack y desperdicia tokens.

## Cómo agregar skills

Hay varias formas, y la metodología es **agnóstica al método**:

- **Manual**: clonar / copiar la skill a `.agents/skills/<name>/SKILL.md`
  desde su repo de origen.
- **Vía meta-skill `find-skills`** (vercel-labs/skills, lee de
  skills.sh): instalar `find-skills`, invocarla con el `stack/`
  completo, aprobar las skills propuestas. Genera o actualiza
  `skills-lock.json` con `source`, `sourceType`, `skillPath`,
  `computedHash` para verificación de integridad.
- **Vía `skills.sh` / `agnix` / otra herramienta**: cualquier
  package manager de skills agente. El formato `SKILL.md` con
  frontmatter está estandarizado.
- **Crear desde cero**: escribir tu propia `SKILL.md` con frontmatter
  `name` + `description` y body en markdown. Claude Code y OpenCode leen
  `.agents/skills/<name>/SKILL.md`; `ai-dlc-init` / `ai-dlc-upgrade`
  espejan además a `.opencode/skills/<name>/` para el tool `skill` de OpenCode.

## Formato de una skill

Cada skill vive en su propio sub-directorio:

```
.agents/skills/<name>/
├── SKILL.md          # principal, con frontmatter (name + description)
└── (otros archivos)  # references, examples, sub-docs (opcional)
```

`SKILL.md` con frontmatter mínimo:

```markdown
---
name: <kebab-case-name>
description: <una línea — el agente la lee para decidir cuándo usar la skill>
---

# <Título>

<Body markdown libre>
```

## Lock file

Si usas meta-skills tipo `find-skills` que validan integridad, suelen
generar un `skills-lock.json` al root del repo. Si instalas
manualmente, no hace falta.
