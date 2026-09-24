# Instrucciones de agente

**El contrato de agente de este repo es [`AGENTS.md`](../AGENTS.md), en la
raiz.** Leelo antes de responder cualquier cosa sobre este repositorio y
sigue su protocolo: los gates, el ciclo de spec y las reglas de `stack/`
estan ahi.

Este archivo es un **puntero, no una copia**. No contiene ninguna regla
propia y no debe ganarlas: si algo aqui pareciera contradecir a
`AGENTS.md`, manda `AGENTS.md`. Una segunda casa para la norma es una
norma que se desincroniza.

## Por que existe

VS Code adjunta `AGENTS.md` solo en **modo Agente** — el setting
`chat.useAgentsMdFile`, que este repo activa en `.vscode/settings.json`,
gobierna el *Local agent harness*. En modo **Ask** no se adjunta, y el
fallo es mudo: el chat responde con fluidez y sin el contrato.

Este archivo, en cambio, lo carga GitHub Copilot **siempre y en todos los
modos**, sin depender de ningun setting. Su unico trabajo es mandarte a
leer el que manda.

> Si vas a trabajar de verdad sobre una spec, cambia a **modo Agente**:
> los slash commands (`/spec-new`, `/spec-design`, …) viven en
> `.github/prompts/` y necesitan herramientas de escritura.
