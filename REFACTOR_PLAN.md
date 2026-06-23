# Plano de Refatoração — Kawakami MCP Server

## Análise do Código Atual

### Estado atual
- **1 arquivo monolítico** (`server.py`) com 809 linhas
- **15 tools MCP** misturadas com infraestrutura, auth, formatação e estado
- **Token hardcoded** no código-fonte (problema de segurança)
- **Sessões em memória** (perdem ao reiniciar)
- **Sem testes**
- **Sem tipagem** (sem dataclasses/pydantic)
- **Sem logging estruturado**
- **`detalhes_produto` faz N+1** (itera todos os departamentos)
- **`ofertas_do_dia` faz N+1** (busca todos os produtos de todos os departamentos)
- **`_api_get` (retry) existe mas não é usado** nas tools — elas criam `httpx.AsyncClient` diretamente
- **Código morto**: linhas 641-659 (bloco `if __name__` duplicado dentro de `_get_ou_criar_sessao`)

### Problemas por categoria

#### Segurança
- Token JWT hardcoded no código (linha 19)
- Sem validação de input nas tools
- Sem rate limiting
- Credenciais do tunnel no repo

#### Arquitetura
- Tudo em um arquivo — viola Single Responsibility
- Sem separação de camadas (domain, infra, presentation)
- Tools contêm lógica de negócio + formatação + HTTP + estado
- Sem injeção de dependência
- Sem interfaces/contratos

#### Performance
- `detalhes_produto`: busca em TODOS os departamentos (14 requests) para achar 1 produto
- `ofertas_do_dia`: busca TODOS os produtos de TODOS os departamentos
- `salvar_lista`: 1 request HTTP por item (sequencial, não paralelo)
- Sem cache de department tree (buscada múltiplas vezes)
- `_api_get` (com retry) existe mas NÃO é usado nas tools

#### Resiliência
- Retry existe mas não é aplicado
- Sem circuit breaker
- Sem timeout configurado por tool
- Erros 503 do VIP Commerce não tratados nas tools (só no `_api_get` não usado)

#### Estado
- Sessões em memória dict — perde ao reiniciar
- Sem TTL/cleanup de sessões antigas
- Sem persistência de carrinho/listas

---

## Estrutura Alvo

```
kawakami-mcp-server/
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
├── src/
│   ├── __init__.py
│   ├── main.py                    # Entry point: argparse + mcp.run()
│   ├── config.py                  # Settings via env vars (pydantic-settings)
│   ├── server.py                  # FastMCP instance + registro de tools
│   │
│   ├── domain/
│   │   ├── __init__.py
│   │   ├── models.py              # Dataclasses/Pydantic: Produto, Oferta, CarrinhoItem, ListaCompras
│   │   └── exceptions.py          # VipCommerceError, TokenExpiredError, ProdutoNotFoundError
│   │
│   ├── infrastructure/
│   │   ├── __init__.py
│   │   ├── vipcommerce_client.py  # Cliente HTTP com retry, cache, auth
│   │   ├── auth.py                # Token management (load/save/refresh)
│   │   ├── cache.py               # Cache in-memory com TTL (department tree, busca)
│   │   └── session_store.py       # Session store com TTL + opcional SQLite
│   │
│   ├── tools/
│   │   ├── __init__.py
│   │   ├── busca.py               # buscar_produtos, buscar_por_ean
│   │   ├── catalogo.py            # listar_departamentos, produtos_por_departamento, detalhes_produto
│   │   ├── ofertas.py             # ofertas_do_dia, verificar_estoque
│   │   ├── carrinho.py            # adicionar, ver, remover, limpar
│   │   └── listas.py              # salvar, ver, minhas, excluir
│   │
│   └── presentation/
│       ├── __init__.py
│       └── formatters.py          # Formatação de preços, produtos, listas para texto
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures: mock VIP Commerce API
│   ├── test_vipcommerce_client.py
│   ├── test_auth.py
│   ├── test_tools_busca.py
│   ├── test_tools_carrinho.py
│   └── test_tools_ofertas.py
│
└── demo/                          # HTML demos (já existem)
```

---

## Fases de Implementação

### Fase 1 — Fundação (sem mudar comportamento)

**Objetivo:** Separar o monolito em módulos sem alterar o que funciona.

**Tarefas:**
1. Criar `src/config.py` com pydantic-settings:
   - `VIPCOMMERCE_BASE_URL`, `VIPCOMMERCE_ORG_ID`, `VIPCOMMERCE_DOMAIN_KEY`
   - `VIPCOMMERCE_TOKEN`, `VIPCOMMERCE_SESSAO_ID` (via env, não hardcoded)
   - `FASTMCP_HOST`, `FASTMCP_PORT`, `FASTMCP_LOG_LEVEL`
   - `DEFAULT_CEP`, `DEFAULT_CD_ID`
   - `IMG_BASE_URL`
   - `API_TIMEOUT_CONNECT`, `API_TIMEOUT_READ`
   - `RETRY_MAX_ATTEMPTS`, `RETRY_BACKOFF_BASE`

2. Criar `src/domain/models.py` com dataclasses:
   - `Produto` (produto_id, descricao, preco, preco_oferta, preco_antigo, em_oferta, tag, tag_nome, unidade_sigla, codigo_barras, sku, codigo_erp, quantidade_maxima, quantidade_vendida, disponivel, imagem, link, departamento)
   - `CarrinhoItem` (produto_id, nome, preco_unit, quantidade, subtotal, un, imagem, em_oferta, tag)
   - `ListaCompras` (nome, itens, total, criado_em, cep)
   - `Departamento` (id, nome, total_ofertas, total_produtos)

3. Criar `src/domain/exceptions.py`:
   - `KawakamiError` (base)
   - `VipCommerceUnavailableError` (503, timeout)
   - `TokenExpiredError` (401)
   - `ProdutoNotFoundError`

4. Criar `src/infrastructure/auth.py`:
   - Classe `TokenManager` com `get_headers()`, `refresh()`, `load()`, `save()`
   - Token do env var, não hardcoded
   - Refresh automático em 401

5. Criar `src/infrastructure/vipcommerce_client.py`:
   - Classe `VipCommerceClient` com todos os endpoints:
     - `search_products(termo, page) -> list[Produto]`
     - `get_departments() -> list[Departamento]` (com cache TTL 1h)
     - `get_products_by_department(dept_id, limit, only_offers) -> list[Produto]`
     - `get_product_by_id(produto_id) -> Produto` (busca otimizada, não N+1)
     - `get_best_offers(limit) -> list[Produto]` (paralelizado com asyncio.gather)
   - Retry com backoff exponencial em TODAS as chamadas
   - Circuit breaker: 5 falhas consecutivas → fast-fail por 60s
   - httpx.AsyncClient reutilizado (não cria novo por request)

6. Criar `src/infrastructure/session_store.py`:
   - Classe `SessionStore` com TTL (24h) e cleanup automático
   - Métodos: `get_session(sid)`, `add_to_cart(sid, item)`, `remove_from_cart(sid, termo)`, `get_cart(sid)`, `clear_cart(sid)`, `save_list(sid, nome, lista)`, `get_lists(sid)`, `get_list(sid, nome)`, `delete_list(sid, nome)`

7. Criar `src/presentation/formatters.py`:
   - `format_product_card(produto: Produto) -> str`
   - `format_product_list(produtos: list[Produto]) -> str`
   - `format_cart(cart: list[CarrinhoItem]) -> str`
   - `format_shopping_list(lista: ListaCompras) -> str`
   - `format_offers_ranking(ofertas: list[Produto]) -> str`
   - `format_price(value: float) -> str`

8. Criar `src/main.py`:
   - Argparse para `--transport`, `--host`, `--port`
   - Importa e registra todas as tools
   - Chama `mcp.run()`

**Critério de aceitação:**
- `docker compose up -d` funciona
- `https://kawakami.axischat.com.br/mcp` responde
- Todas as 15 tools funcionam igual ao comportamento atual
- Zero tokens hardcoded no código
- `grep -r "eyJ" src/` retorna vazio

---

### Fase 2 — Otimização de Performance

**Objetivo:** Eliminar N+1 e adicionar cache.

**Tarefas:**
1. Otimizar `get_product_by_id`:
   - Tentar busca textual primeiro (1 request)
   - Só iterar departamentos se a busca falhar
   - Paralelizar a busca em departamentos com `asyncio.gather`

2. Otimizar `get_best_offers`:
   - Buscar todos os departamentos em paralelo (`asyncio.gather`)
   - Filtrar ofertas em memória
   - Ordenar por desconto

3. Adicionar cache em `vipcommerce_client.py`:
   - Department tree: TTL 1 hora
   - Busca de produtos: TTL 5 minutos
   - Usar `cachetools.TTLCache` ou dict simples com timestamps

4. Paralelizar `salvar_lista`:
   - Buscar todos os itens em paralelo com `asyncio.gather`

5. Reutilizar `httpx.AsyncClient`:
   - Instância única criada no startup do servidor
   - Fechada no shutdown
   - Connection pooling nativo do httpx

**Critério de aceitação:**
- `detalhes_produto` faz no máximo 2 requests (busca + fallback)
- `ofertas_do_dia` faz 1 request por departamento em paralelo (não sequencial)
- Department tree é cacheada
- Tempo de resposta das tools melhora mensuravelmente

---

### Fase 3 — Resiliência e Segurança

**Objetivo:** Tratar falhas graciosamente e proteger o servidor.

**Tarefas:**
1. Circuit breaker no `VipCommerceClient`:
   - 5 falhas consecutivas → estado OPEN por 60s
   - Após 60s → HALF_OPEN (1 request de teste)
   - Sucesso → CLOSED
   - Retornar erro amigável quando OPEN

2. Tratamento de erros nas tools:
   - Try/except em todas as tools
   - Retornar mensagem clara: "API temporariamente indisponível. Tente novamente em alguns minutos."
   - Não propagar stack traces para o modelo

3. Validação de input:
   - Sanitizar `termo` (remover caracteres especiais, limitar length)
   - Validar `produto_id` > 0
   - Validar `quantidade` entre 1 e 999
   - Validar `cep` (8 dígitos numéricos)

4. Rate limiting por sessão:
   - Máximo 30 tool calls por minuto por sessão
   - Retornar erro 429 com retry-after

5. Logging estruturado:
   - `logging` module com formato JSON
   - Log de cada tool call (tool name, session_id, duration_ms, success)
   - Log de erros da API VIP (status_code, endpoint, duration_ms)
   - Nível configurável via env var

6. Health check endpoint:
   - `GET /health` retorna `{"status": "ok", "vip_commerce": "reachable|unreachable"}`
   - Usado pelo Docker healthcheck

**Critério de aceitação:**
- VIP Commerce cai → tools retornam mensagem clara, servidor não crasha
- VIP Commerce volta → circuit breaker fecha automaticamente
- Input inválido é rejeitado antes de chegar na API
- Logs estruturados visíveis via `docker compose logs`

---

### Fase 4 — Persistência e Testes

**Objetivo:** Sessões sobrevivem a restarts e código é testável.

**Tarefas:**
1. Persistência de sessões com SQLite:
   - Tabela `sessions` (id, created_at, last_access)
   - Tabela `cart_items` (session_id, produto_id, nome, preco_unit, quantidade, subtotal, un, imagem, em_oferta, tag)
   - Tabela `shopping_lists` (session_id, nome, itens_json, total, created_at, cep)
   - Migration automática no startup
   - Fallback para memória se SQLite falhar

2. Cleanup de sessões expiradas:
   - Job periódico (a cada 1h) remove sessões sem acesso há mais de 7 dias
   - Configurável via env var `SESSION_TTL_DAYS`

3. Testes unitários:
   - Mock do `VipCommerceClient` (respostas fixture)
   - Test de cada tool com mock
   - Test do `TokenManager` (refresh, expiry)
   - Test do `SessionStore` (add, remove, clear, TTL)
   - Test dos formatters

4. Testes de integração:
   - Subir servidor em porta de teste
   - Chamar tools via MCP client de teste
   - Verificar respostas

**Critério de aceitação:**
- Restart do container → carrinho e listas persistem
- `pytest` passa com 80%+ cobertura
- Sessões antigas são limpas automaticamente

---

### Fase 5 — DX e Deploy

**Objetivo:** Developer experience profissional.

**Tarefas:**
1. `.env.example` com todas as variáveis documentadas
2. `.gitignore` (`.env`, `*.json` com tokens, `__pycache__`, `.venv`)
3. `Makefile` ou `justfile`:
   - `make dev` — roda local com stdio
   - `make dev-http` — roda local com HTTP
   - `make build` — docker build
   - `make up` — docker compose up
   - `make down` — docker compose down
   - `make logs` — docker compose logs -f
   - `make test` — pytest
   - `make lint` — ruff check
4. `ruff.toml` para linting
5. GitHub Actions CI:
   - Lint + type check + tests em cada PR
   - Build Docker image em push para main
6. README.md com:
   - Arquitetura (diagrama)
   - Como rodar local
   - Como deployar
   - Lista de tools
   - Variáveis de ambiente

**Critério de aceitação:**
- Novo dev consegue rodar o projeto com `make dev`
- CI passa em cada PR
- README explica tudo sem precisar perguntar

---

## Regras para o implementador

1. **Não quebrar o que funciona** — cada fase é independente e deployable
2. **Um PR por fase** — revisão isolada
3. **Python 3.13+** com type hints em todas as funções
4. **Sem comentários óbvios** — só comentar o "porquê", nunca o "o quê"
5. **Ruff para lint** — linha máxima 100 chars
6. **Sem `print()`** — usar `logging` module
7. **Sem `except:` bare** — sempre especificar a exceção
8. **Sem mutable default args** — usar `None` + init dentro da função
9. **`async def` em todas as I/O** — nunca bloquear o event loop
10. **Pydantic para validação** — não validar manualmente com if/else
