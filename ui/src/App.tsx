import { useState, useCallback, useSyncExternalStore } from "react"
import { applyDocumentTheme } from "@openai/apps-sdk-ui/theme"
import { OFFERS, activePrice } from "./data"
import { ProductCarousel } from "./components/ProductCarousel"
import { CartDrawer } from "./components/CartDrawer"
import type { CartItem } from "./components/CartDrawer"
import { PipButton } from "./components/PipButton"
import { getSections, onSectionsChange, type UiSection } from "./bridge"

applyDocumentTheme("dark")

export function App() {
  const [cart, setCart] = useState<CartItem[]>([])
  const [drawerOpen, setDrawerOpen] = useState(false)

  const bridgeSections = useSyncExternalStore(onSectionsChange, getSections)

  const sections: UiSection[] = bridgeSections.length > 0
    ? bridgeSections
    : [{ key: "offers", title: "Ofertas do Dia", products: OFFERS }]

  const allProducts = sections.flatMap(s => s.products)

  const addToCart = useCallback((id: number) => {
    const product = allProducts.find(p => p.id === id)
    if (!product) return
    setCart(prev => {
      const existing = prev.find(i => i.id === id)
      if (existing) { const q = existing.quantity + 1; return prev.map(i => i.id === id ? { ...i, quantity: q, subtotal: q * i.unitPrice } : i) }
      return [...prev, { id: product.id, name: product.name, unit: product.unit, unitPrice: activePrice(product), quantity: 1, subtotal: activePrice(product), image: product.image, isOffer: product.offerPrice !== null, originalPrice: product.originalPrice }]
    })
  }, [allProducts])

  const handleQtyChange = useCallback((id: number, delta: number) => {
    setCart(prev => { const item = prev.find(i => i.id === id); if (!item) return prev; const q = item.quantity + delta; if (q <= 0) return prev.filter(i => i.id !== id); return prev.map(i => i.id === id ? { ...i, quantity: q, subtotal: q * i.unitPrice } : i) })
  }, [])

  const handleRemove = useCallback((id: number) => { setCart(prev => prev.filter(i => i.id !== id)) }, [])
  const handleCheckout = useCallback(() => { console.log("Checkout:", cart) }, [cart])
  const unitCount = cart.reduce((s, i) => s + i.quantity, 0)

  return (
    <div className="bg-main text-default min-h-dvh">
      {sections.map(s => (
        <section key={s.key}>
          <p className="text-xs font-semibold text-secondary uppercase tracking-wider px-4 pt-4 pb-2.5">{s.title}</p>
          <ProductCarousel products={s.products} cartItems={cart} onAdd={addToCart} />
        </section>
      ))}
      {sections.length === 0 && <p className="text-center text-tertiary text-sm py-20">Nenhum produto para exibir.</p>}
      <div className="h-20" />
      <PipButton count={unitCount} onClick={() => setDrawerOpen(true)} />
      <CartDrawer items={cart} open={drawerOpen} onClose={() => setDrawerOpen(false)} onQuantityChange={handleQtyChange} onRemove={handleRemove} onCheckout={handleCheckout} />
    </div>
  )
}
