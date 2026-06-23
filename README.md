# Kawakami MCP Server

MCP Server que expõe o catálogo do **Supermercados Kawakami** (Paraguaçu Paulista/SP) como ferramentas para Claude, ChatGPT, OpenCode e qualquer cliente MCP.

## Arquitetura

```
Cliente MCP (ChatGPT/Claude/OpenCode)
        │
        ▼
Cloudflare Tunnel (kawakami.axischat.com.br)
        │
        ▼
FastMCP (Python) ← httpx → VIP Commerce API
        │
        ▼
SQLite (sessoes/carrinho/listas)
```

```
src/
├── main.py                 # Entrypoint + argparse
├── server.py               # FastMCP + tool registration
├── config.py               # Settings via env vars
├── domain/
│   ├── models.py           # Produto, Oferta, CarrinhoItem...
│   └── exceptions.py       # VipCommerceUnavailable, TokenExpired...
├── infrastructure/
│   ├── auth.py             # TokenManager (load/save/refresh)
│   ├── vipcommerce_client.py  # HTTP client + retry + cache + circuit breaker
│   ├── session_store.py    # SQLite-backed sessions
│   ├── circuit_breaker.py  # Circuit breaker state machine
│   ├── validation.py       # Input sanitization
│   └── error_handler.py    # @safe_tool decorator
├── presentation/
│   └── formatters.py       # Text formatting
└── tools/
    ├── busca.py            # buscar_produtos, buscar_por_ean
    ├── catalogo.py         # listar_departamentos, produtos_por_departamento, detalhes_produto
    ├── ofertas.py          # ofertas_do_dia, verificar_estoque
    ├── carrinho.py         # adicionar, ver, remover, limpar
    └── listas.py           # salvar, minhas, ver, excluir
```

## Deploy rápido

```bash
cp .env.example .env   # Preencha KWK_VIP_TOKEN e KWK_VIP_SESSAO_ID
make up                # Build + sobe API + tunnel
```

## Tools (15)

| Tool | Descrição |
|---|---|
| `buscar_produtos` | Busca produtos por nome |
| `buscar_por_ean` | Busca por código de barras |
| `listar_departamentos` | Lista departamentos com contagem |
| `produtos_por_departamento` | Produtos de um departamento |
| `detalhes_produto` | Detalhes completos por ID |
| `ofertas_do_dia` | Ranking de melhores ofertas |
| `verificar_estoque` | Estoque de um produto |
| `adicionar_ao_carrinho` | Adiciona item ao carrinho |
| `ver_carrinho` | Mostra carrinho atual |
| `remover_do_carrinho` | Remove item do carrinho |
| `limpar_carrinho` | Esvazia carrinho |
| `salvar_lista` | Salva lista de compras |
| `minhas_listas` | Lista listas salvas |
| `ver_lista` | Detalha uma lista |
| `excluir_lista` | Remove uma lista |

## Variáveis de ambiente

Ver `.env.example` para todas as opções. Essenciais:

| Var | Descrição |
|---|---|
| `KWK_VIP_TOKEN` | Token JWT da sessão anônima VIP Commerce |
| `KWK_VIP_SESSAO_ID` | Session ID do VIP Commerce |
| `KWK_DEFAULT_CEP` | CEP padrão (default: 19700000) |

## Desenvolvimento

```bash
make dev        # stdio (para testar no OpenCode/Claude Desktop)
make dev-http   # HTTP (para testar no navegador)
make test       # pytest
make lint       # ruff
```
