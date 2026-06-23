# Direcionamento — UI Components para MCP Kawakami

## Regra fundamental

**Cada tool MCP = 1 arquivo HTML separado.** Cada arquivo é um `iframe` que aparece embutido na conversa do ChatGPT — NÃO contém chat falso, mensagens de usuário, input de texto, ou simulação da interface do ChatGPT.

O ChatGPT fornece o chat. O nosso HTML fornece APENAS o componente visual da resposta.

## O que NÃO fazer (o modelo anterior errou nisso)

- ❌ Incluir mensagens de chat (`"Quais iogurtes estão em oferta?"`)
- ❌ Incluir input de texto simulando o composer do ChatGPT
- ❌ Incluir avatares, nomes de usuário, bolhas de conversa
- ❌ Misturar todas as tools numa página só
- ❌ Usar emojis (usar Lucide Icons sempre)
- ❌ Usar cores que não são da Kawakami (ex: verde `#10a37f` do ChatGPT)
- ❌ Usar imagens placeholder do Unsplash — usar imagens REAIS da API

## O que FAZER

- ✅ 1 arquivo HTML por tool MCP
- ✅ Apenas o widget/componente que o iframe renderiza
- ✅ Cores da Kawakami (ver abaixo)
- ✅ Lucide Icons (CDN: `https://unpkg.com/lucide@latest`)
- ✅ Imagens reais da API: `https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/{imagem}`
- ✅ Animações suaves (CSS animations ou Framer Motion via CDN)
- ✅ Mobile-first (max-width: 480px é o iframe, mas o componente se adapta)

## Branding Kawakami

| Token | Valor |
|-------|-------|
| Verde primário | `#138d45` |
| Verde escuro | `#005e1b` |
| Verde lima | `#a5c83f` |
| Preto | `#2f3138` |
| Cinza | `#545454` |
| Laranja (Clube Amigo) | `#f97316` |
| Vermelho (indisponível) | `#dc2626` |
| Fundo | `#ffffff` |
| Fonte | system-ui, sans-serif (herda do ChatGPT) |

## Tags de oferta

| Tag API | Cor | Label |
|---------|-----|-------|
| `clube-amigo` | `#f97316` | Clube Amigo |
| `oferta-da-semana` | `#138d45` | Oferta da Semana |
| `exclusiva-do-app-e-site` | `#2f3138` | Exclusiva App |

## Arquivos a criar (1 por tool)

### 1. `busca.html` — Buscar Produtos
**Quando aparece:** O modelo chama `buscar_produtos(termo="arroz")`
**Componente:** Grid de cards com foto, nome, preço, badge de oferta
**Layout mobile:** Cards em lista vertical, cada um com imagem quadrada grande + nome + preço + tag
**Interação:** Nenhuma (display only — o modelo decide o próximo passo)

### 2. `ofertas.html` — Ofertas do Dia
**Quando aparece:** O modelo chama `ofertas_do_dia()`
**Componente:** Lista rankeada por % de desconto
**Layout:** Cada linha: posição (#1, #2), miniatura 40px, nome, tag colorida, preço oferta (verde), preço antigo riscado, % OFF

### 3. `carrinho.html` — Carrinho (ver + adicionar + remover)
**Quando aparece:** O modelo chama `ver_carrinho()`, `adicionar_ao_carrinho()`, `remover_do_carrinho()`
**Componente:** Lista de itens com controles de quantidade (-/+) e botão remover, total no final
**Interação:** Botões +/- e remover são clicáveis (no MCP real, o clique chama a tool via ChatGPT SDK)
**Estados:** Vazio ("Carrinho vazio"), Com itens, Item adicionado (highlight por 1s)

### 4. `departamentos.html` — Listar Departamentos
**Quando aparece:** O modelo chama `listar_departamentos()`
**Componente:** Grid 2 colunas com nome do departamento e contagem de produtos

### 5. `detalhes.html` — Detalhes do Produto
**Quando aparece:** O modelo chama `detalhes_produto(id=285)`
**Componente:** Card expandido com imagem grande, nome, EAN, SKU, estoque, oferta ativa

### 6. `listas.html` — Listas Salvas
**Quando aparece:** O modelo chama `minhas_listas()` ou `ver_lista("nome")`
**Componente:** Lista vertical com nome da lista, quantidade de itens, total

## Interatividade (apenas no carrinho)

No `carrinho.html`, os botões +/- e remover disparam funções JavaScript que simulam a tool call. No MCP real, esses cliques são interceptados pelo ChatGPT Apps SDK e viram tool calls (`adicionar_ao_carrinho`, `remover_do_carrinho`). No HTML demo, apenas manipulam o estado local.

## Animações

Usar CSS `@keyframes` — sem dependência de Framer Motion (não funciona em iframe sem React):

```css
@keyframes slideIn { from { opacity: 0; transform: translateY(12px); } to { opacity: 1; transform: translateY(0); } }
@keyframes fadeIn { from { opacity: 0; } to { opacity: 1; } }
.card { animation: slideIn 0.3s ease-out forwards; }
```

## Exemplo de card de produto (busca.html)

```html
<div class="card">
  <img src="https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/6699785a-5a94-4a14-ad57-6094f8de5afc.jpg" alt="Produto">
  <div class="card-body">
    <span class="tag tag-exclusive">Exclusiva App</span>
    <h3>Mac. Nissin Lamen 85g Bacon</h3>
    <p class="price-offer">R$ 2,79</p>
    <p class="price-old">R$ 3,18</p>
  </div>
</div>
```

## Imagens reais para usar nos demos

```
https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/6699785a-5a94-4a14-ad57-6094f8de5afc.jpg (Nissin Lamen Bacon)
https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/c0f9116a-a928-4dc6-823c-fbc925c28bb2.jpg (Sabao Omo)
https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/4dd5bdb3-9133-4722-9f0d-1b34faeea910.jpg (Leite Terra Viva)
https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/e4c2e6d4-ca53-4274-9317-1da977d20e84.jpg (Arroz Pateko)
https://produto-assets-vipcommerce-com-br.br-se1.magaluobjects.com/250x250/d85d344b-4c1a-47e6-938c-e55d8a57c5ba.jpg (Requeijao Vigor)
```
