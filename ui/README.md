# Kawakami MCP App UI

Interface React entregue pelo resource MCP Apps do servidor.

```bash
npm ci
npm run dev
npm run lint
npm run build
```

A UI usa `@modelcontextprotocol/ext-apps` para handshake, recebimento de
`structuredContent` e chamadas `tools/call`. Carrinho e sessão permanecem
autoritativos no backend.
