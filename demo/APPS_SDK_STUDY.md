# Estudo Completo — Apps SDK UI para Kawakami MCP

Documento baseado na leitura da documentação completa em https://openai.github.io/apps-sdk-ui/

---

## 1. Setup do Projeto

```bash
# Criar projeto Vite + React + TypeScript
npm create vite@latest kawakami-app -- --template react-ts
cd kawakami-app

# Instalar dependências
npm install @openai/apps-sdk-ui

# Tailwind 4 já vem incluso como peer dependency
```

### Arquivos para criar/modificar:

**`src/main.css`:**
```css
@import "tailwindcss";
@import "@openai/apps-sdk-ui/css";
@source "../node_modules/@openai/apps-sdk-ui";
```

**`src/main.tsx`:**
```tsx
import "./main.css";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import { App } from "./App";

createRoot(document.getElementById("root")!).render(
  <StrictMode>
    <App />
  </StrictMode>
);
```

**`index.html`:**
```html
<html data-theme="dark">
```

### Stack final:
- React 18/19 + TypeScript
- Vite (bundler)
- Tailwind 4 (estilos)
- `@openai/apps-sdk-ui` (componentes + tokens)
- `lucide-react` (ícones, já incluso no SDK)

---

## 2. Mapa de Componentes → Funcionalidades Kawakami

| Funcionalidade | Componente SDK | Como usar |
|---|---|---|
| **Card de produto** | `div` + Tailwind | `bg-surface border border-default rounded-xl p-3` |
| **Badge de oferta** | `<Badge>` | `color="danger"` (Clube Amigo), `color="success"` (Oferta), `variant="solid"` |
| **Imagem do produto** | `<img>` | `aspect-square object-contain bg-surface-secondary` |
| **Nome do produto** | `<p>` | `text-sm font-medium line-clamp-2` |
| **Preço** | `<p>` | `heading-sm` (18px) |
| **Preço antigo** | `<p>` | `text-2xs text-tertiary line-through` |
| **Botão Adicionar** | `<Button>` | `color="primary" variant="solid" size="sm" block` (mobile) |
| **Carrossel** | `div` + Tailwind | `flex gap-3 overflow-x-auto scroll-snap-x snap-mandatory` |
| **Carrinho PiP** | `<Button>` + `<Badge>` | `uniform pill variant="solid"` + badge de contagem |
| **Toast confirmação** | `<Badge>` custom | `variant="solid" color="success"` + ícone check |
| **Fullscreen carrinho** | `div` + Tailwind | `fixed inset-0 bg-surface z-50 flex flex-col` |
| **Item do carrinho** | `div` | `flex gap-3 border-b border-default` |
| **Controles +/-** | `<Button>` | `variant="ghost" uniform size="sm"` |
| **Estado vazio** | `<EmptyMessage>` | Ícone + texto "Carrinho vazio" |
| **Botão Finalizar** | `<Button>` | `color="primary" variant="solid" size="lg" block` |
| **Animações** | `<AnimateLayout>` / `<AnimateLayoutGroup>` | Listas com enter/exit animados |

---

## 3. Tokens de Design Relevantes

### Superfície
| Token | Uso |
|---|---|
| `bg-main` | Fundo da página |
| `bg-surface` | Fundo de cards |
| `bg-surface-secondary` | Fundo de imagens |
| `bg-surface-hover` | Hover de itens |

### Texto
| Token | Uso |
|---|---|
| `text-default` | Texto principal |
| `text-secondary` | Texto secundário |
| `text-tertiary` | Preço antigo, estoque |

### Borda
| Token | Uso |
|---|---|
| `border-default` | Borda padrão |
| `border-subtle` | Borda leve |

### Tipografia (classes Tailwind do SDK)
| Classe | Tamanho | Uso |
|---|---|---|
| `heading-lg` | 24px/28px | Título do carrinho |
| `heading-sm` | 18px/26px | Preço do produto |
| `heading-xs` | 16px/24px | Total do carrinho |
| `text-md` | 16px/24px | Corpo |
| `text-sm` | 14px/20px | Nome do produto |
| `text-xs` | 12px/18px | Badge, botão |
| `text-2xs` | 10px/14px | Estoque, unidade |

### Marca (Kawakami - usar apenas em CTAs e badges)
| Cor | Hex |
|---|---|
| Primary (verde) | `#138d45` |
| Clube Amigo (laranja) | `#f97316` |

### Dark Mode
- Ativar com `<html data-theme="dark">` ou `applyDocumentTheme("dark")`
- Tokens CSS trocam automaticamente com o atributo `[data-theme]`
- Usar `useDocumentTheme()` hook para ler estado atual

---

## 4. Padrão de Animação

### Entrada de cards no carrossel
Usar `<AnimateLayoutGroup>` com `enter={{ x: 20, opacity: 0 }}`:

```tsx
import { AnimateLayoutGroup } from "@openai/apps-sdk-ui/components/Transition";

<AnimateLayoutGroup dimension="width" enter={{ x: 20, opacity: 0, delay: 0 }} layoutEnter={{ duration: 400 }}>
  {products.map(p => (
    <ProductCard key={p.id} product={p} />
  ))}
</AnimateLayoutGroup>
```

### Item adicionado/removido do carrinho
Usar `<AnimateLayout>` com `exit={{ opacity: 0, x: -20 }}`:

```tsx
<AnimateLayout exit={{ opacity: 0, x: -20, duration: 300 }}>
  {showConfirmation && <ConfirmationCard />}
</AnimateLayout>
```

### Abertura do drawer (Fullscreen)
Usar CSS transition com `translateY`:

```tsx
<div className={`fixed inset-0 bg-surface transition-transform duration-350 ${open ? 'translate-y-0' : 'translate-y-full'}`}>
```

### Aparecimento do PiP
Usar CSS transition com `scale` + `opacity`:

```tsx
<div className={`fixed bottom-6 right-6 transition-all duration-300 ${visible ? 'opacity-100 scale-100' : 'opacity-0 scale-50 pointer-events-none'}`}>
```

### Easing padrão do SDK
```
cubic-bezier(0.19, 1, 0.22, 1)  // standard
cubic-bezier(0.8, 0, 0.4, 1)    // enter
cubic-bezier(0.65, 0, 0.35, 1)   // exit
```

Duração padrão: `150ms` (rápido), `350ms` (normal)

---

## 5. App.tsx Esqueleto

```tsx
import { useState } from "react";
import { Badge } from "@openai/apps-sdk-ui/components/Badge";
import { Button } from "@openai/apps-sdk-ui/components/Button";
import { EmptyMessage } from "@openai/apps-sdk-ui/components/EmptyMessage";
import { AnimateLayout, AnimateLayoutGroup } from "@openai/apps-sdk-ui/components/Transition";
import { Plus, ShoppingCart, Check, X, CreditCard, Minus } from "lucide-react";

// Types
interface Product {
  id: number; nome: string; preco: number; precoOferta: number | null;
  precoAntigo: number | null; unidade: string; imagem: string;
  estoque: number; tag: string | null; tagNome: string | null;
}
interface CartItem extends Product { quantidade: number; subtotal: number; }

// Product Card (inline carousel item)
function ProductCard({ product, onAdd }: { product: Product; onAdd: (id: number) => void }) {
  const preco = product.precoOferta ?? product.preco;
  const desconto = product.precoOferta && product.precoAntigo
    ? Math.round((1 - product.precoOferta / product.precoAntigo) * 100) : 0;

  return (
    <div className="min-w-[180px] bg-surface border border-default rounded-xl overflow-hidden flex flex-col snap-start">
      {/* Imagem */}
      <div className="relative bg-surface-secondary flex justify-center items-center h-[140px] border-b border-default">
        <img src={`${IMG_BASE}/${product.imagem}`} className="max-h-[100px] max-w-[90%] object-contain" />
        {product.tagNome && (
          <Badge color={tagColor(product.tag)} variant="solid" className="absolute top-2 left-2">
            {product.tagNome}
          </Badge>
        )}
      </div>
      {/* Corpo */}
      <div className="p-3 flex flex-col flex-1 gap-2">
        <p className="text-sm font-medium line-clamp-2">{product.nome}</p>
        <p className="text-2xs text-tertiary">{product.estoque} em estoque</p>
        <div className="mt-auto flex justify-between items-end">
          <div>
            {product.precoAntigo && <p className="text-2xs text-tertiary line-through">R$ {product.precoAntigo.toFixed(2)}</p>}
            <p className="heading-sm">{fmt(product.precoOferta ?? product.preco)}</p>
            <p className="text-2xs text-tertiary">/{product.unidade}</p>
          </div>
          <Button color="primary" variant="solid" size="sm" onClick={() => onAdd(product.id)}>
            <Plus className="size-3.5" /> Adicionar
          </Button>
        </div>
      </div>
    </div>
  );
}

// Carousel wrapper
function ProductCarousel({ products, onAdd }: { products: Product[]; onAdd: (id: number) => void }) {
  return (
    <div className="flex gap-3 overflow-x-auto pb-4 snap-x snap-mandatory [-ms-overflow-style:none] [scrollbar-width:none] [&::-webkit-scrollbar]:hidden">
      {products.map(p => <ProductCard key={p.id} product={p} onAdd={onAdd} />)}
    </div>
  );
}

// Cart Item (fullscreen list)
function CartRow({ item, onQty, onRemove }: { item: CartItem; onQty: (id: number, d: number) => void; onRemove: (id: number) => void }) {
  return (
    <div className="flex items-center gap-3 py-4 border-b border-default">
      <img src={`${IMG_BASE}/${item.imagem}`} className="w-14 h-14 object-contain bg-surface-secondary rounded-lg" />
      <div className="flex-1 min-w-0">
        <p className="text-sm font-medium truncate">{item.nome}</p>
        <p className="text-xs text-tertiary mt-1">R$ {item.preco.toFixed(2)}/{item.unidade}</p>
        <div className="flex items-center gap-2 mt-2">
          <Button variant="ghost" uniform size="sm" onClick={() => onQty(item.id, -1)}><Minus className="size-3.5"/></Button>
          <span className="text-sm font-semibold min-w-[20px] text-center">{item.quantidade}</span>
          <Button variant="ghost" uniform size="sm" onClick={() => onQty(item.id, 1)}><Plus className="size-3.5"/></Button>
        </div>
      </div>
      <div className="text-right">
        <p className="heading-xs">R$ {item.subtotal.toFixed(2)}</p>
        {item.precoOferta && item.precoAntigo && (
          <p className="text-2xs text-tertiary line-through">R$ {(item.precoAntigo * item.quantidade).toFixed(2)}</p>
        )}
      </div>
      <Button variant="ghost" uniform size="sm" onClick={() => onRemove(item.id)}>
        <X className="size-4 text-tertiary hover:text-danger" />
      </Button>
    </div>
  );
}

// Main App
export function App() {
  const [cart, setCart] = useState<CartItem[]>([]);
  const [showFullscreen, setShowFullscreen] = useState(false);

  const addToCart = (id: number) => { /* ... lógica do carrinho */ };
  const removeFromCart = (id: number) => { /* ... */ };
  const changeQty = (id: number, delta: number) => { /* ... */ };

  const total = cart.reduce((s, i) => s + i.subtotal, 0);
  const unitCount = cart.reduce((s, i) => s + i.quantidade, 0);

  return (
    <div className="bg-main text-default min-h-dvh max-w-[480px] mx-auto">
      {/* Conteúdo principal */}
      <div className="p-4 pb-24">
        <h2 className="text-xs font-semibold text-secondary uppercase tracking-wider mb-2">Ofertas do Dia</h2>
        <ProductCarousel products={OFFERS} onAdd={addToCart} />
      </div>

      {/* PiP — Carrinho flutuante */}
      {cart.length > 0 && (
        <div className="fixed top-4 right-4 z-50" onClick={() => setShowFullscreen(true)}>
          <Button uniform pill variant="solid" color="primary" size="lg">
            <ShoppingCart className="size-5" />
          </Button>
          <Badge color="danger" variant="solid" className="absolute -top-1 -right-1 min-w-[22px] h-[22px]">
            {unitCount}
          </Badge>
        </div>
      )}

      {/* Fullscreen — Carrinho completo */}
      {showFullscreen && (
        <div className="fixed inset-0 bg-surface z-[100] flex flex-col transition-transform duration-350 translate-y-0">
          <div className="flex items-center justify-between p-4 border-b border-default">
            <h2 className="heading-lg">Carrinho</h2>
            <Button variant="ghost" uniform size="sm" onClick={() => setShowFullscreen(false)}>
              <X className="size-5" />
            </Button>
          </div>

          <div className="flex-1 overflow-y-auto p-4">
            {cart.length === 0 ? (
              <EmptyMessage icon={ShoppingCart}>Carrinho vazio</EmptyMessage>
            ) : (
              <AnimateLayoutGroup dimension="height">
                {cart.map(item => (
                  <CartRow key={item.id} item={item} onQty={changeQty} onRemove={removeFromCart} />
                ))}
              </AnimateLayoutGroup>
            )}
          </div>

          <div className="p-4 border-t border-default">
            <div className="flex justify-between items-end mb-4">
              <div>
                <p className="text-xs text-tertiary uppercase tracking-wider">Total</p>
                <p className="text-xs text-tertiary">{unitCount} unidade{unitCount > 1 ? 's' : ''}</p>
              </div>
              <p className="text-2xl font-bold">R$ {total.toFixed(2)}</p>
            </div>
            <Button color="primary" variant="solid" size="lg" block onClick={() => {}}>
              <CreditCard className="size-5" /> Finalizar Compra
            </Button>
          </div>
        </div>
      )}
    </div>
  );
}
```

---

## 6. Regras Críticas da OpenAI

1. **"No duplicative inputs"** — nunca colocar search bar no iframe. O modelo busca via tool.
2. **"No nested scrolling"** — scroll só no carrossel horizontal, nunca vertical dentro de card.
3. **"Limit primary actions per card"** — máximo 1 CTA por card (botão Adicionar).
4. **"System fonts"** — herdar `ui-sans-serif`, não usar fonte customizada.
5. **"Brand colors only on accents"** — verde Kawakami só em badges e CTAs.
6. **"Extract, don't port"** — não é um e-commerce. É um assistente de compras.
7. **Iframe background** — `bg-main` = cor do ChatGPT. Cards = `bg-surface` (flutuam).

---

## Páginas lidas

✅ Introduction, Installation, Dark Mode, Typography, Badge, Button
⏭️ Responsive Design, Colors, Design Tokens, Icons (extraído via sidebar)
⏭️ Transition components (extraído via docs enviadas anteriormente)
