# Native Widget UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Remover a moldura externa do widget e tornar cards e ação de compra visualmente nativos ao ChatGPT.

**Architecture:** O servidor controla a preferência de moldura e a URI de cache do resource. A UI React mantém o comportamento atual e altera somente classes de apresentação e atributos acessíveis do botão.

**Tech Stack:** Python, FastMCP, MCP Apps, React, TypeScript, Tailwind CSS, Vite.

---

### Task 1: Metadados do widget

**Files:**
- Modify: `tests/test_mcp_app.py`
- Modify: `src/presentation/widget.py`
- Modify: `README.md`
- Modify: `docs/superpowers/specs/2026-06-23-mcp-hardening-design.md`

- [x] **Step 1: Escrever o teste falhando**

Adicionar asserções para `WIDGET_URI == "ui://kawakami/catalog-v2.html"` e
`WIDGET_RESOURCE_META["ui"]["prefersBorder"] is False`.

- [x] **Step 2: Confirmar a falha**

Run: `uv run pytest tests/test_mcp_app.py -q`

Expected: falha porque a URI ainda é `catalog-v1.html` e a preferência é `True`.

- [x] **Step 3: Implementar o metadado**

Atualizar `WIDGET_URI`, definir `prefersBorder` como `False` e alinhar as
referências documentais.

- [x] **Step 4: Confirmar o teste**

Run: `uv run pytest tests/test_mcp_app.py -q`

Expected: todos os testes do arquivo aprovados.

### Task 2: Cards e ação compacta

**Files:**
- Modify: `ui/src/App.tsx`
- Modify: `ui/src/components/ProductCard.tsx`

- [x] **Step 1: Integrar a superfície ao host**

Trocar o fundo estrutural do elemento `main` por `bg-transparent`, preservando
as cores semânticas de texto.

- [x] **Step 2: Arredondar os cards**

Trocar `rounded-xl` por `rounded-2xl`, mantendo bordas neutras e dimensões.

- [x] **Step 3: Compactar a ação**

Usar botão circular `size-8`, ícone centralizado, `aria-label` e `title`.
Manter verde somente no acento e no estado confirmado.

- [x] **Step 4: Validar a UI**

Run: `npm run lint && npm run build`

Expected: ESLint e Vite encerram com código zero.

### Task 3: Verificação local

**Files:**
- Verify: `docker-compose.yml`

- [x] **Step 1: Executar backend**

Run: `uv run pytest tests/ -q && uv run ruff check src/ tests/`

Expected: suíte e lint aprovados.

- [x] **Step 2: Reconstruir o ambiente**

Run: `docker compose up -d --build --force-recreate`

Expected: serviço `kawakami` marcado como `healthy`.

- [x] **Step 3: Validar saúde**

Run: `Invoke-RestMethod http://127.0.0.1:8000/health`

Expected: `status` igual a `ok`.
