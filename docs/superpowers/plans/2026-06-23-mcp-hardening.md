# MCP Kawakami Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Corrigir isolamento, autenticação, catálogo, deploy e integração da UI MCP Apps.

**Architecture:** Manter FastMCP/Python e React, introduzir sessão explícita persistida,
resultados MCP estruturados e resource HTML versionado. Cada comportamento crítico recebe
um teste de regressão antes da implementação.

**Tech Stack:** Python 3.13, MCP Python SDK 1.28, httpx, SQLite, pytest, React 19,
TypeScript, Vite.

---

### Task 1: Sessões explícitas

**Files:**
- Modify: `src/infrastructure/session_store.py`
- Replace: `src/infrastructure/sessions.py`
- Modify: `src/tools/carrinho.py`
- Modify: `src/tools/listas.py`
- Modify: `src/server.py`
- Create: `tests/test_sessions.py`

- [ ] Escrever testes que provem que IDs são opacos, persistidos e obrigatórios.
- [ ] Executar `uv run pytest tests/test_sessions.py -v` e confirmar falha.
- [ ] Implementar `criar_sessao` e validação de `session_id`.
- [ ] Executar testes de sessão e confirmar sucesso.

### Task 2: Refresh de autenticação

**Files:**
- Modify: `src/infrastructure/auth.py`
- Modify: `src/infrastructure/vipcommerce_client.py`
- Create: `tests/test_auth.py`

- [ ] Escrever teste 401 → refresh → retry usando o novo header.
- [ ] Executar o teste e confirmar que o segundo request ainda usa o token antigo.
- [ ] Montar headers por tentativa e registrar falhas de arquivo sem segredos.
- [ ] Executar o teste e confirmar sucesso.

### Task 3: CEP, paginação e falhas do catálogo

**Files:**
- Modify: `src/infrastructure/vipcommerce_client.py`
- Modify: `src/tools/catalogo.py`
- Modify: `src/tools/ofertas.py`
- Modify: `src/tools/listas.py`
- Create: `tests/test_vipcommerce_client.py`

- [ ] Escrever testes para CEP propagado, múltiplas páginas e falha total.
- [ ] Executar os testes e confirmar falhas.
- [ ] Implementar paginação limitada, propagação de CEP e tratamento explícito.
- [ ] Executar os testes e confirmar sucesso.

### Task 4: Resultados estruturados e resource MCP Apps

**Files:**
- Create: `src/presentation/structured.py`
- Create: `src/presentation/widget.py`
- Modify: `src/tools/busca.py`
- Modify: `src/tools/catalogo.py`
- Modify: `src/tools/ofertas.py`
- Modify: `src/tools/carrinho.py`
- Modify: `src/server.py`
- Create: `tests/test_mcp_app.py`

- [ ] Escrever testes para `structuredContent`, metadata e resource MIME type.
- [ ] Executar os testes e confirmar falhas.
- [ ] Implementar builders de resultado e registrar resource versionado.
- [ ] Executar os testes e confirmar sucesso.

### Task 5: Bridge e build React

**Files:**
- Modify: `ui/src/bridge.ts`
- Modify: `ui/src/App.tsx`
- Modify: `ui/src/components/CartDrawer.tsx`
- Modify: `ui/src/components/ProductCard.tsx`
- Modify: `ui/src/data.ts`
- Modify: `ui/src/main.tsx`
- Modify: `ui/package.json`
- Delete: `ui/src/App.css`
- Delete: `ui/src/index.css`
- Delete: `ui/src/assets/react.svg`
- Delete: `ui/src/assets/vite.svg`

- [ ] Implementar bridge JSON-RPC com validação de origem e timeouts.
- [ ] Renderizar `structuredContent` e encaminhar mutações por `tools/call`.
- [ ] Remover `console.log`, dados fictícios como fallback e imports de template Vite.
- [ ] Corrigir propriedades obrigatórias dos componentes.
- [ ] Executar `npm run lint` e `npm run build`.

### Task 6: Healthcheck, Docker e deploy

**Files:**
- Modify: `src/server.py`
- Modify: `docker-compose.yml`
- Modify: `deploy.sh`
- Modify: `Dockerfile`
- Create: `tests/test_health.py`

- [ ] Escrever teste HTTP para `/health`.
- [ ] Executar o teste e confirmar 404.
- [ ] Registrar rota, volume SQLite e comando systemd correto.
- [ ] Executar o teste e validar configuração Docker.

### Task 7: Qualidade e documentação

**Files:**
- Modify: `ruff.toml`
- Modify: `pyproject.toml`
- Modify: `README.md`
- Modify: `.env.example`
- Modify: arquivos Python apontados pelo Ruff

- [ ] Corrigir configuração Ruff e erros reais, sem alterações de comportamento.
- [ ] Documentar sessão explícita, UI, healthcheck e variáveis.
- [ ] Executar a suíte completa, lint Python, lint UI e build UI.
- [ ] Inspecionar `git diff` e confirmar ausência de segredos e artefatos.
