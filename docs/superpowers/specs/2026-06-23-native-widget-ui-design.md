# Native Widget UI Design

## Objetivo

Integrar visualmente o catálogo Kawakami ao ChatGPT, removendo a moldura externa
do host e reduzindo a competição visual entre preço, card e ação.

## Decisões

- O resource MCP usa `prefersBorder: false`.
- A URI muda para `ui://kawakami/catalog-v2.html` para invalidar o cache.
- A superfície raiz fica transparente e herda tipografia e tema do host.
- Cards mantêm borda estrutural neutra, com raio `rounded-2xl`.
- A ação usa um botão circular de 32 px, somente com `+` ou `✓`.
- O verde é reservado ao acento da ação e ao estado confirmado.
- O botão mantém `title` e `aria-label` para acessibilidade.

## Responsividade

O carrossel e as dimensões atuais dos cards permanecem. A ação compacta libera
espaço horizontal para preço e unidade sem alterar o fluxo mobile-first.

## Verificação

- Teste do metadado do resource e da URI versionada.
- ESLint e build TypeScript/Vite.
- Suíte Python completa.
- Rebuild do Docker Compose e healthcheck local.

