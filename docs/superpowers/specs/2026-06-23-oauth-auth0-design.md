# OAuth 2.1 — Auth0 + Kawakami MCP Design

## Objetivo

Carrinho e listas persistirem entre conversas do ChatGPT via autenticação OAuth 2.1 com Auth0.

## Arquitetura

```
ChatGPT (OAuth client)
  → Auth0 (Authorization Server)
    → emite JWT com sub=auth0|user123
  → Kawakami MCP (Resource Server)
    → TokenVerifier valida JWT via JWKS
    → criar_sessao extrai sub → user_id estável
    → SQLite carrinho/listas por user_id
```

O `mcp==1.28.0` suporta `token_verifier` nativo via `TokenVerifier` (Protocol). Implementamos `Auth0TokenVerifier` que valida JWTs contra o JWKS do Auth0. O FastMCP gerencia o middleware automaticamente.

## Decisões

- **Auth0** (não custom): CIMD nativo, PKCE `S256`, OIDC, gratuito até 25k MAU
- **`noauth` para catálogo**: usuário pode buscar produtos sem login (descoberta)
- **`oauth2` para carrinho/listas**: requer login 1x no Auth0
- **`user_id` = Auth0 `sub`**: identificador estável e imutável
- **JWKS validation**: `PyJWKClient` faz cache automático das chaves
- **Sem refresh token**: ChatGPT gerencia — se token expirar, re-autentica

## O que NÃO muda

- UI React — idêntica
- VIP Commerce token admin — continua igual
- Docker, Cloudflare Tunnel, deploy
- Tools de catálogo — continuam funcionando sem auth

## Ferramentas e seus securitySchemes

| Tool | securitySchemes |
|---|---|
| `buscar_produtos`, `buscar_por_ean`, `listar_departamentos`, `produtos_por_departamento`, `detalhes_produto`, `ofertas_do_dia`, `verificar_estoque` | `[{type: "noauth"}]` |
| `criar_sessao`, `adicionar_ao_carrinho`, `ver_carrinho`, `remover_do_carrinho`, `limpar_carrinho`, `salvar_lista`, `minhas_listas`, `ver_lista`, `excluir_lista` | `[{type: "oauth2", scopes: ["cart:read", "cart:write"]}]` |

## Fluxo de autenticação

1. Usuário abre ChatGPT, conecta Kawakami MCP
2. ChatGPT faz `tools/list` → vê `securitySchemes`
3. Tenta chamar `buscar_produtos("leite")` → `noauth` → funciona ✅
4. Tenta `adicionar_ao_carrinho(...)` → `oauth2` → 401
5. ChatGPT lê `/.well-known/oauth-protected-resource` → descobre Auth0
6. Abre popup → usuário faz login no Auth0 (Google, email, etc.)
7. Auth0 emite JWT com `sub=auth0|google-oauth2|12345`
8. ChatGPT anexa `Authorization: Bearer <JWT>` em toda request
9. `criar_sessao` extrai `sub` → `user_id = "auth0|google-oauth2|12345"`
10. Carrinho persiste entre conversas com o mesmo user_id

## Verificação

- Teste unitário: `Auth0TokenVerifier` (token válido, expirado, issuer errado)
- Teste integração: `tools/list` mostra `securitySchemes`
- Teste manual: MCP Inspector com token JWT falso (modo dev)
- Docker: `/.well-known/oauth-protected-resource` acessível
