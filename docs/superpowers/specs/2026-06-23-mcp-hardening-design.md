# MCP Kawakami Hardening Design

## Objetivo

Tornar o servidor MCP seguro entre usuários, resiliente à renovação de autenticação,
implantável com healthcheck real e capaz de entregar a UI React pelo padrão MCP Apps.

## Arquitetura

- O backend continua em Python com `mcp==1.28.0`.
- Carrinhos e listas usam um `session_id` explícito, opaco e persistido no SQLite.
- Tools de catálogo retornam texto compatível com clientes MCP e dados estruturados para a UI.
- A UI é registrada como resource `ui://kawakami/catalog-v2.html` e usa JSON-RPC 2.0
  sobre `postMessage`.
- O servidor expõe `/health` sem consultar a API externa, para que a saúde do processo não
  dependa do fornecedor.

## Sessões

Uma tool `criar_sessao` cria um identificador com 128 bits de entropia. Todas as tools de
carrinho e listas exigem esse identificador. O backend valida formato e existência antes de
ler ou alterar dados. Não haverá fallback global.

## Autenticação VIP Commerce

O cliente HTTP monta os headers de autenticação em cada tentativa. Quando uma resposta 401
for renovada com sucesso, a tentativa seguinte usa imediatamente o novo token. Falhas de
leitura e escrita do arquivo de token são registradas sem incluir o token.

## Catálogo e CEP

CEP será propagado para departamentos, produtos, detalhes e ofertas. A paginação por
departamento buscará todas as páginas necessárias até o limite solicitado. Falhas parciais
de departamentos serão registradas; falha total será retornada como indisponibilidade, não
como lista vazia.

## MCP Apps

As tools visuais retornam um `CallToolResult` com:

- `content`: resumo textual para compatibilidade;
- `structuredContent`: seções e produtos tipados;
- `_meta.ui.resourceUri`: resource versionado da UI.

O resource usa `text/html;profile=mcp-app`, CSS/JS embutidos e CSP restrita ao CDN de imagens.
A UI inicializa a bridge, recebe `ui/notifications/tool-result` e chama tools por `tools/call`.
Carrinho local deixa de ser autoridade; todas as mutações passam pelo backend.

## Deploy

- `/health` retorna HTTP 200 quando o processo está pronto.
- Docker persiste o SQLite em volume.
- O healthcheck chama `/health`.
- `deploy.sh` usa `python -m src.main` por meio do `uv` encontrado no PATH.

## Testes

- Unitários para sessão explícita, refresh de token, paginação e resultados estruturados.
- Integração Streamable HTTP para duas sessões independentes.
- Teste de resource MCP Apps e `/health`.
- `pytest`, Ruff, TypeScript, ESLint e Vite build como verificação final.
